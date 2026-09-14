import logging
import math
import threading
import time
from typing import Optional, Tuple

import astropy.units as u
from astropy.coordinates import AltAz, EarthLocation, SkyCoord, get_sun
from astropy.time import Time

from app.config import DriverConfig, load_config
from app.jetter_interface import JetterInterface

logger = logging.getLogger(__name__)


class SafetyLimitViolation(Exception):
    """Exception raised when a requested position or motion violates software safety envelopes."""
    pass


class TelescopeModel:
    """
    Kinematic, safety, and coordinate management engine for the telescope mount.
    Translates celestial coordinates (RA/Dec) to topocentric Hour Angle / Declination,
    enforces safety envelopes, interfaces with the Jetter Nano-B controller,
    and manages tracking, slewing, parking, and plate-solve calibration status.
    """

    def __init__(self, config: Optional[DriverConfig] = None, jetter: Optional[JetterInterface] = None):
        self.config = config or load_config()
        self.jetter = jetter or JetterInterface(
            port=self.config.serial.port,
            baudrate=self.config.serial.baudrate,
            timeout=self.config.serial.timeout_sec,
            mock_mode=self.config.serial.mock_mode,
        )

        self._lock = threading.RLock()
        self.is_connected = False
        self.is_slewing = False
        self.is_tracking = False
        self.is_parked = True
        self.is_calibrated = False  # Set to True once a plate-solve sync is performed
        self.calibration_message = "Telescope initialized at South park position (HA=0, Dec=0). NOT yet calibrated by plate solve."

        # Location
        obs = self.config.observatory
        self.location = EarthLocation(
            lat=obs.latitude_deg * u.deg,
            lon=obs.longitude_deg * u.deg,
            height=obs.elevation_m * u.m
        )

        # Coordinate offsets (for plate solve sync)
        self._ha_offset_deg = 0.0
        self._dec_offset_deg = 0.0

        # Background threads
        self._tracking_running = False
        self._tracking_thread: Optional[threading.Thread] = None
        self._slew_thread: Optional[threading.Thread] = None
        self._abort_requested = False

    def connect(self) -> bool:
        """Connects to hardware controller and initializes initial park reference."""
        with self._lock:
            if self.is_connected:
                return True
            ok = self.jetter.connect()
            if ok:
                self.is_connected = True
                self._initialize_park_position()
                self._start_tracking_thread()
                logger.info("Telescope mount connected and initialized at South park position.")
            return ok

    def disconnect(self) -> None:
        """Stops background threads and disconnects from controller."""
        with self._lock:
            if not self.is_connected:
                return
            self.abort_slew()
            self._tracking_running = False
            if self._tracking_thread and self._tracking_thread.is_alive():
                self._tracking_thread.join(timeout=1.0)
            self.jetter.disconnect()
            self.is_connected = False
            logger.info("Telescope mount disconnected.")

    # -------------------------------------------------------------------------
    # Astrometry & Coordinate Calculations
    # -------------------------------------------------------------------------

    def get_local_sidereal_time_hours(self, at_time: Optional[Time] = None) -> float:
        """Calculates current Local Sidereal Time (LST) in hours [0, 24)."""
        t = at_time or Time.now()
        lst_angle = t.sidereal_time('apparent', longitude=self.config.observatory.longitude_deg * u.deg)
        return lst_angle.hour

    def _initialize_park_position(self) -> None:
        """
        Initializes controller registers to the known South-facing park position.
        By requirement: Park position is pointing South on meridian (HA = 0.0, Dec = 0.0).
        """
        park_ha = self.config.kinematics.park_ha_deg
        park_dec = self.config.kinematics.park_dec_deg

        ha_step = round(self.config.kinematics.ra_steps_per_deg * park_ha)
        dec_step = -round(self.config.kinematics.dec_steps_per_deg * park_dec)

        # Write initial position to actual and target registers
        self.jetter.set_register(13109, ha_step) # RA/HA actual
        self.jetter.set_register(13102, ha_step) # RA/HA target
        self.jetter.set_register(12109, dec_step) # Dec actual
        self.jetter.set_register(12102, dec_step) # Dec target

        # Set resolution prescalers (32)
        self.jetter.set_register(12122, 32)
        self.jetter.set_register(13122, 32)

        # Ensure speed control mode (Bit 9 = 0)
        self.jetter.set_bit(12100, 9, 0)
        self.jetter.set_bit(13100, 9, 0)

        self.is_parked = True
        self.is_tracking = False
        self.is_calibrated = False
        self.calibration_message = "Mount initialized at South park position (HA=0, Dec=0). NOT yet calibrated by plate solve."
        logger.warning(self.calibration_message)

    def get_current_coordinates(self) -> Tuple[float, float, float, float]:
        """
        Reads actual motor encoder counts and converts to (RA hours, Dec deg, Alt deg, Az deg).
        """
        with self._lock:
            ha_step = self.jetter.get_register(13109)
            dec_step = self.jetter.get_register(12109)

            # Inverse kinematics
            ha_deg = (ha_step / self.config.kinematics.ra_steps_per_deg) + self._ha_offset_deg
            dec_deg = (-dec_step / self.config.kinematics.dec_steps_per_deg) + self._dec_offset_deg

            # Convert HA to RA: RA = LST - HA
            lst_hours = self.get_local_sidereal_time_hours()
            ha_hours = ha_deg / 15.0
            ra_hours = (lst_hours - ha_hours) % 24.0

            # Convert to Alt/Az for horizon monitoring
            t = Time.now()
            coord = SkyCoord(ra=ra_hours * 15.0 * u.deg, dec=dec_deg * u.deg, frame='icrs')
            altaz_frame = AltAz(
                obstime=t,
                location=self.location,
                pressure=self.config.observatory.pressure_hpa * u.hPa,
                temperature=self.config.observatory.temperature_c * u.deg_C
            )
            altaz = coord.transform_to(altaz_frame)

            return ra_hours, dec_deg, altaz.alt.deg, altaz.az.deg

    # -------------------------------------------------------------------------
    # Safety Checks
    # -------------------------------------------------------------------------

    def validate_safety_limits(self, target_ra_hours: float, target_dec_deg: float) -> None:
        """
        Validates whether target coordinates fall within software safety envelopes.
        Raises SafetyLimitViolation if limits are breached.
        """
        # 1. Declination limit
        if not (self.config.safety.min_dec_deg <= target_dec_deg <= self.config.safety.max_dec_deg):
            raise SafetyLimitViolation(
                f"Target Declination {target_dec_deg:.2f}° violates safety limits "
                f"[{self.config.safety.min_dec_deg}°, {self.config.safety.max_dec_deg}°]."
            )

        # 2. Hour Angle limit
        lst_hours = self.get_local_sidereal_time_hours()
        ha_hours = (lst_hours - target_ra_hours)
        # Normalize HA to [-12, +12] hours
        if ha_hours > 12.0:
            ha_hours -= 24.0
        elif ha_hours < -12.0:
            ha_hours += 24.0
        ha_deg = ha_hours * 15.0

        if not (self.config.safety.min_ha_deg <= ha_deg <= self.config.safety.max_ha_deg):
            raise SafetyLimitViolation(
                f"Target Hour Angle {ha_deg:.2f}° violates safety limits "
                f"[{self.config.safety.min_ha_deg}°, {self.config.safety.max_ha_deg}°]."
            )

        # 3. Altitude / Horizon limit
        t = Time.now()
        target_coord = SkyCoord(ra=target_ra_hours * 15.0 * u.deg, dec=target_dec_deg * u.deg, frame='icrs')
        altaz_frame = AltAz(
            obstime=t,
            location=self.location,
            pressure=self.config.observatory.pressure_hpa * u.hPa,
            temperature=self.config.observatory.temperature_c * u.deg_C
        )
        altaz = target_coord.transform_to(altaz_frame)
        if altaz.alt.deg < self.config.safety.min_alt_deg:
            raise SafetyLimitViolation(
                f"Target altitude {altaz.alt.deg:.2f}° is below minimum safety altitude "
                f"{self.config.safety.min_alt_deg}° (below horizon)."
            )

        # 4. Solar Avoidance limit
        sun_coord = get_sun(t)
        sep_deg = target_coord.separation(sun_coord).deg
        if sep_deg < self.config.safety.sun_avoidance_deg:
            raise SafetyLimitViolation(
                f"Target is {sep_deg:.2f}° from the Sun, violating solar safety margin "
                f"({self.config.safety.sun_avoidance_deg}°)."
            )

    # -------------------------------------------------------------------------
    # Slewing & Motion
    # -------------------------------------------------------------------------

    def slew_to_coordinates(self, ra_hours: float, dec_deg: float, async_mode: bool = True) -> None:
        """
        Slews telescope to target RA and Dec coordinates.
        """
        with self._lock:
            if not self.is_connected:
                raise RuntimeError("Cannot slew: Mount is not connected.")
            if self.is_parked:
                raise RuntimeError("Cannot slew: Mount is currently parked. Unpark first.")
            if self.is_slewing:
                raise RuntimeError("Cannot slew: A slew operation is already in progress.")

            # Perform comprehensive safety validation
            self.validate_safety_limits(ra_hours, dec_deg)

            self._abort_requested = False
            self.is_slewing = True

        if async_mode:
            self._slew_thread = threading.Thread(
                target=self._execute_slew,
                args=(ra_hours, dec_deg),
                daemon=True
            )
            self._slew_thread.start()
        else:
            self._execute_slew(ra_hours, dec_deg)

    def _execute_slew(self, target_ra_hours: float, target_dec_deg: float) -> None:
        """Performs physical or simulated slew execution."""
        logger.info(f"Beginning slew to RA={target_ra_hours:.4f}h, Dec={target_dec_deg:.4f}°")
        try:
            # 1. Turn on warning buzzer
            self.jetter.set_output(101, 1)

            # 2. Calculate target steps
            lst_hours = self.get_local_sidereal_time_hours()
            ha_hours = (lst_hours - target_ra_hours)
            if ha_hours > 12.0:
                ha_hours -= 24.0
            elif ha_hours < -12.0:
                ha_hours += 24.0
            ha_deg = (ha_hours * 15.0) - self._ha_offset_deg
            effective_dec_deg = target_dec_deg - self._dec_offset_deg

            target_ha_step = round(self.config.kinematics.ra_steps_per_deg * ha_deg)
            target_dec_step = -round(self.config.kinematics.dec_steps_per_deg * effective_dec_deg)

            # 3. Configure velocities and nominal positions
            slew_speed = self.config.safety.max_slew_speed
            self.jetter.set_register(12103, slew_speed)
            self.jetter.set_register(13103, slew_speed)

            self.jetter.set_register(12102, target_dec_step)
            self.jetter.set_register(13102, target_ha_step)

            # 4. Engage Position Control Mode (Bit 9 = 1)
            self.jetter.set_bit(12100, 1, 0) # Clear in-position bit
            self.jetter.set_bit(13100, 1, 0)
            self.jetter.set_bit(12100, 9, 1)
            self.jetter.set_bit(13100, 9, 1)

            # 5. Monitor progress until target reached or abort
            start_time = time.time()
            while not self._abort_requested:
                dec_done = bool(self.jetter.get_bit(12100, 1))
                ra_done = bool(self.jetter.get_bit(13100, 1))

                if dec_done and ra_done:
                    logger.info("Slew successfully reached target coordinates.")
                    break

                # Dynamic sidereal compensation for RA during long slews
                elapsed = time.time() - start_time
                if elapsed > 1.0:
                    lst_now = self.get_local_sidereal_time_hours()
                    curr_ha_deg = ((lst_now - target_ra_hours) * 15.0) - self._ha_offset_deg
                    updated_ha_step = round(self.config.kinematics.ra_steps_per_deg * curr_ha_deg)
                    self.jetter.set_register(13102, updated_ha_step)

                time.sleep(0.05)

        except Exception as e:
            logger.error(f"Error during slew execution: {e}")
        finally:
            with self._lock:
                # Disengage position mode -> switch back to speed mode (Bit 9 = 0)
                self.jetter.set_bit(12100, 9, 0)
                self.jetter.set_bit(13100, 9, 0)
                # Silence buzzer
                self.jetter.set_output(101, 0)
                self.is_slewing = False

            if not self.is_calibrated:
                logger.info("Slew completed. Mount is still UNCALIBRATED. Please trigger a plate solve to sync.")

    def abort_slew(self) -> None:
        """Immediately halts all motion."""
        logger.warning("Abort requested on TelescopeModel.")
        self._abort_requested = True
        self.jetter.abort_motion()
        self.is_slewing = False

    # -------------------------------------------------------------------------
    # Tracking
    # -------------------------------------------------------------------------

    def set_tracking(self, enable: bool) -> None:
        """Enables or disables sidereal tracking."""
        with self._lock:
            if enable and self.is_parked:
                raise RuntimeError("Cannot start tracking while mount is parked.")
            self.is_tracking = enable
            logger.info(f"Sidereal tracking set to: {enable}")

    def _start_tracking_thread(self) -> None:
        self._tracking_running = True
        self._tracking_thread = threading.Thread(target=self._tracking_loop, daemon=True)
        self._tracking_thread.start()

    def _tracking_loop(self) -> None:
        """
        Background loop to increment RA step at sidereal rate when tracking is enabled.
        Sidereal rate = ~111.712 steps/second.
        """
        last_time = time.time()
        accumulator = 0.0

        while self._tracking_running:
            time.sleep(0.05)
            now = time.time()
            dt = now - last_time
            last_time = now

            if self.is_connected and self.is_tracking and not self.is_slewing and not self.is_parked:
                # Increment RA position by sidereal delta
                steps_float = self.config.kinematics.sidereal_steps_per_sec * dt + accumulator
                steps_to_apply = int(steps_float)
                accumulator = steps_float - steps_to_apply

                if steps_to_apply != 0:
                    with self._lock:
                        curr_step = self.jetter.get_register(13109)
                        new_step = curr_step + steps_to_apply
                        self.jetter.set_register(13109, new_step)
                        self.jetter.set_register(13102, new_step)

    # -------------------------------------------------------------------------
    # Parking & Calibration Sync
    # -------------------------------------------------------------------------

    def park(self) -> None:
        """Slews telescope back to South park position and halts tracking."""
        with self._lock:
            if not self.is_connected:
                raise RuntimeError("Cannot park: Mount is not connected.")
            self.set_tracking(False)
            self.is_parked = False  # temporarily enable slew
            logger.info("Parking telescope to South park position.")

        park_ha = self.config.kinematics.park_ha_deg
        park_dec = self.config.kinematics.park_dec_deg
        lst_hours = self.get_local_sidereal_time_hours()
        park_ra_hours = (lst_hours - (park_ha / 15.0)) % 24.0

        self.slew_to_coordinates(park_ra_hours, park_dec, async_mode=False)
        with self._lock:
            self.is_parked = True
            logger.info("Telescope is now safely parked.")

    def unpark(self) -> None:
        """Unparks telescope and engages sidereal tracking."""
        with self._lock:
            if not self.is_connected:
                raise RuntimeError("Cannot unpark: Mount is not connected.")
            self.is_parked = False
            self.set_tracking(True)
            logger.info("Telescope unparked; tracking enabled.")

    def sync_to_coordinates(self, solved_ra_hours: float, solved_dec_deg: float) -> None:
        """
        Synchronizes telescope coordinate system to a resolved plate-solve coordinate.
        Marks mount as calibrated!
        """
        with self._lock:
            # Current raw reported values
            curr_ra, curr_dec, _, _ = self.get_current_coordinates()

            # Calculate coordinate correction offsets
            self._dec_offset_deg += (solved_dec_deg - curr_dec)
            ra_err_hours = (solved_ra_hours - curr_ra)
            if ra_err_hours > 12.0:
                ra_err_hours -= 24.0
            elif ra_err_hours < -12.0:
                ra_err_hours += 24.0
            self._ha_offset_deg -= (ra_err_hours * 15.0)

            self.is_calibrated = True
            self.calibration_message = (
                f"Telescope successfully calibrated against plate solve at "
                f"RA={solved_ra_hours:.4f}h, Dec={solved_dec_deg:.4f}°."
            )
            logger.info(self.calibration_message)

    def move_axis(self, axis: int, rate_deg_per_sec: float) -> None:
        """
        Moves a mount axis (0 = Primary / RA, 1 = Secondary / Dec) at specified rate (deg/s).
        Used for manual jogging and pulse guiding.
        """
        with self._lock:
            if not self.is_connected:
                raise RuntimeError("Mount not connected.")
            if axis == 0: # RA axis
                steps_per_sec = int(self.config.kinematics.ra_steps_per_deg * rate_deg_per_sec)
                self.jetter.set_register(13103, abs(steps_per_sec))
                # If rate > 0 positive direction (reg 13101 = 9), else negative (reg 13101 = 10)
                if steps_per_sec != 0:
                    self.jetter.set_register(13101, 9 if steps_per_sec > 0 else 10)
            elif axis == 1: # Dec axis
                steps_per_sec = -int(self.config.kinematics.dec_steps_per_deg * rate_deg_per_sec)
                self.jetter.set_register(12103, abs(steps_per_sec))
                if steps_per_sec != 0:
                    self.jetter.set_register(12101, 9 if steps_per_sec > 0 else 10)
