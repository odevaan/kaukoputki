import math
import time
import pytest
from app.config import DriverConfig, MountKinematics, SafetyLimits
from app.jetter_interface import JetterInterface
from app.telescope_model import SafetyLimitViolation, TelescopeModel


@pytest.fixture
def model():
    config = DriverConfig()
    config.serial.mock_mode = True
    jetter = JetterInterface(mock_mode=True)
    m = TelescopeModel(config=config, jetter=jetter)
    m.connect()
    yield m
    m.disconnect()


def test_kinematics_scaling(model):
    k = model.config.kinematics
    assert k.ra_steps_per_rev == 18800 * 512 # 9,625,600
    assert k.dec_steps_per_rev == 14100 * 512 # 7,219,200
    assert abs(k.ra_steps_per_deg - 26737.7778) < 0.001
    assert abs(k.dec_steps_per_deg - 20053.3333) < 0.001
    assert abs(k.sidereal_steps_per_sec - 111.712) < 0.01


def test_initial_park_and_calibration_state(model):
    assert model.is_parked
    assert not model.is_tracking
    assert not model.is_calibrated
    assert "NOT yet calibrated" in model.calibration_message

    # Verify controller registers were initialized to South park (0, 0)
    assert model.jetter.get_register(13109) == 0
    assert model.jetter.get_register(12109) == 0

    # Read coordinates
    ra, dec, alt, az = model.get_current_coordinates()
    assert abs(dec - 0.0) < 0.001
    lst = model.get_local_sidereal_time_hours()
    diff = abs(ra - lst) % 24.0
    assert min(diff, 24.0 - diff) < 0.05 # RA equals LST when HA=0


def test_safety_envelope_enforcement(model):
    # Unpark before testing slew validation
    model.unpark()

    # 1. Declination limit violation (> 90 deg or < -50 deg)
    with pytest.raises(SafetyLimitViolation) as exc:
        model.validate_safety_limits(target_ra_hours=12.0, target_dec_deg=95.0)
    assert "Declination" in str(exc.value)

    with pytest.raises(SafetyLimitViolation) as exc:
        model.validate_safety_limits(target_ra_hours=12.0, target_dec_deg=-60.0)
    assert "Declination" in str(exc.value)

    # 2. Altitude below horizon violation (target deep below southern horizon)
    lst = model.get_local_sidereal_time_hours()
    # At latitude 62.7N, Dec -45 at HA=0 has altitude ~ (90 - 62.7 - 45) = -17 deg
    with pytest.raises(SafetyLimitViolation) as exc:
        model.validate_safety_limits(target_ra_hours=lst, target_dec_deg=-45.0)
    assert "horizon" in str(exc.value).lower() or "altitude" in str(exc.value).lower()


def test_dynamic_safety_limits_editing(model):
    # Test editing safety limits as requested by user
    model.config.safety.min_dec_deg = -30.0
    with pytest.raises(SafetyLimitViolation):
        model.validate_safety_limits(target_ra_hours=12.0, target_dec_deg=-35.0)

    # Restore
    model.config.safety.min_dec_deg = -50.0


def test_sync_to_coordinates_calibration(model):
    assert not model.is_calibrated
    # Simulate a plate solve result
    solved_ra = 14.5
    solved_dec = 25.0

    model.sync_to_coordinates(solved_ra, solved_dec)
    assert model.is_calibrated
    assert "successfully calibrated" in model.calibration_message

    curr_ra, curr_dec, _, _ = model.get_current_coordinates()
    assert abs(curr_ra - solved_ra) < 0.01
    assert abs(curr_dec - solved_dec) < 0.01


def test_slew_and_abort(model):
    model.unpark()
    lst = model.get_local_sidereal_time_hours()
    # Target near zenith (RA = LST, Dec = 62.7 deg)
    target_ra = lst
    target_dec = model.config.observatory.latitude_deg

    # Start async slew
    model.slew_to_coordinates(target_ra, target_dec, async_mode=True)
    time.sleep(0.1)
    assert model.is_slewing

    # Emergency abort
    model.abort_slew()
    time.sleep(0.1)
    assert not model.is_slewing
    assert model.jetter.get_output(101) == 0 # buzzer off
