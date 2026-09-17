import logging
import socket
import threading
import time
from typing import Optional

from app.telescope_model import TelescopeModel, SafetyLimitViolation

logger = logging.getLogger(__name__)

DEFAULT_LX200_PORT = 4030


class LX200Server:
    """
    Meade LX200 TCP Command Protocol Server.
    Provides direct network connectivity for KStars/Ekos (via indi_lx200generic / indi_lx200basic),
    Stellarium, SkySafari, and Cartes du Ciel without requiring extra INDI bridge packages.
    """

    def __init__(self, model: TelescopeModel, host: str = "0.0.0.0", port: int = DEFAULT_LX200_PORT):
        self.model = model
        self.host = host
        self.port = port
        self._server_sock: Optional[socket.socket] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None

        # LX200 Target staging registers
        self.target_ra_hours: Optional[float] = None
        self.target_dec_deg: Optional[float] = None

    def start(self) -> None:
        if self._running:
            return
        try:
            self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_sock.bind((self.host, self.port))
            self._server_sock.listen(5)
            self._running = True
            self._thread = threading.Thread(target=self._listen_loop, daemon=True)
            self._thread.start()
            logger.info(f"LX200 TCP server running on {self.host}:{self.port} (KStars/Ekos compatible)")
        except Exception as e:
            logger.warning(f"Could not start LX200 TCP server on port {self.port}: {e}")

    def stop(self) -> None:
        self._running = False
        if self._server_sock:
            try:
                self._server_sock.close()
            except Exception:
                pass
            self._server_sock = None
        logger.info("LX200 TCP server stopped.")

    def _listen_loop(self) -> None:
        while self._running:
            try:
                client_sock, addr = self._server_sock.accept()
                logger.info(f"LX200 client connected from {addr[0]}:{addr[1]}")
                handler = threading.Thread(target=self._handle_client, args=(client_sock,), daemon=True)
                handler.start()
            except Exception as e:
                if self._running:
                    logger.error(f"LX200 accept error: {e}")

    def _handle_client(self, client_sock: socket.socket) -> None:
        client_sock.settimeout(5.0)
        buffer = ""
        try:
            while self._running:
                try:
                    data = client_sock.recv(1024)
                    if not data:
                        break
                    buffer += data.decode("latin1", errors="ignore")
                except socket.timeout:
                    continue

                # Process commands separated by '#' or alignment ACK prefix (0x06)
                while "#" in buffer or "\x06" in buffer:
                    ack_pos = buffer.find("\x06")
                    hash_pos = buffer.find("#")

                    if ack_pos != -1 and (hash_pos == -1 or ack_pos < hash_pos):
                        # Alignment query byte (ACK / 0x06)
                        buffer = buffer[ack_pos + 1:]
                        client_sock.sendall(b"P")  # Polar alignment
                        continue

                    if hash_pos != -1:
                        cmd = buffer[:hash_pos].strip()
                        buffer = buffer[hash_pos + 1:]
                        if cmd:
                            resp = self._execute_command(cmd)
                            if resp:
                                client_sock.sendall(resp.encode("latin1"))
                    else:
                        break

        except Exception as e:
            logger.debug(f"LX200 client handler disconnected: {e}")
        finally:
            try:
                client_sock.close()
            except Exception:
                pass

    def _execute_command(self, cmd: str) -> Optional[str]:
        """
        Executes standard Meade LX200 commands.
        """
        try:
            # 1. Coordinate queries
            if cmd in [":GR", "GR"]:
                # Get RA: HH:MM:SS#
                ra, _, _, _ = self.model.get_current_coordinates()
                h = int(ra) % 24
                m = int((ra - int(ra)) * 60)
                s = int(((ra - int(ra)) * 60 - m) * 60)
                return f"{h:02d}:{m:02d}:{s:02d}#"

            elif cmd in [":GD", "GD"]:
                # Get Dec: sDD*MM:SS#
                _, dec, _, _ = self.model.get_current_coordinates()
                sign = "+" if dec >= 0 else "-"
                abs_dec = abs(dec)
                d = int(abs_dec)
                m = int((abs_dec - d) * 60)
                s = int(((abs_dec - d) * 60 - m) * 60)
                return f"{sign}{d:02d}*{m:02d}:{s:02d}#"

            elif cmd in [":GA", "GA"]:
                # Get Altitude: sDD*MM:SS#
                _, _, alt, _ = self.model.get_current_coordinates()
                sign = "+" if alt >= 0 else "-"
                abs_alt = abs(alt)
                d = int(abs_alt)
                m = int((abs_alt - d) * 60)
                s = int(((abs_alt - d) * 60 - m) * 60)
                return f"{sign}{d:02d}*{m:02d}:{s:02d}#"

            elif cmd in [":GZ", "GZ"]:
                # Get Azimuth: DDD*MM:SS#
                _, _, _, az = self.model.get_current_coordinates()
                az = az % 360.0
                d = int(az)
                m = int((az - d) * 60)
                s = int(((az - d) * 60 - m) * 60)
                return f"{d:03d}*{m:02d}:{s:02d}#"

            elif cmd in [":Gr", "Gr"]:
                # Get Target RA: HH:MM:SS#
                ra = self.target_ra_hours if self.target_ra_hours is not None else self.model.get_current_coordinates()[0]
                h = int(ra) % 24
                m = int((ra - int(ra)) * 60)
                s = int(((ra - int(ra)) * 60 - m) * 60)
                return f"{h:02d}:{m:02d}:{s:02d}#"

            elif cmd in [":Gd", "Gd"]:
                # Get Target Dec: sDD*MM:SS#
                dec = self.target_dec_deg if self.target_dec_deg is not None else self.model.get_current_coordinates()[1]
                sign = "+" if dec >= 0 else "-"
                abs_dec = abs(dec)
                d = int(abs_dec)
                m = int((abs_dec - d) * 60)
                s = int(((abs_dec - d) * 60 - m) * 60)
                return f"{sign}{d:02d}*{m:02d}:{s:02d}#"

            # 2. Time & Date queries
            elif cmd in [":GS", "GS"]:
                # Get Sidereal Time: HH:MM:SS#
                lst = self.model.get_local_sidereal_time_hours()
                h = int(lst) % 24
                m = int((lst - int(lst)) * 60)
                s = int(((lst - int(lst)) * 60 - m) * 60)
                return f"{h:02d}:{m:02d}:{s:02d}#"

            elif cmd in [":Gc", "Gc"]:
                # Get Clock Format: 24#
                return "24#"

            elif cmd in [":Ga", "Ga"]:
                # Local time 12-hour format: HH:MM:SS#
                now = time.localtime()
                h12 = now.tm_hour % 12
                h12 = 12 if h12 == 0 else h12
                return f"{h12:02d}:{now.tm_min:02d}:{now.tm_sec:02d}#"

            elif cmd in [":GL", "GL"]:
                # Get Local Time 24h: HH:MM:SS#
                now = time.localtime()
                return f"{now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}#"

            elif cmd in [":GC", "GC"]:
                # Get Calendar Date: MM/DD/YY#
                now = time.localtime()
                return f"{now.tm_mon:02d}/{now.tm_mday:02d}/{str(now.tm_year)[-2:]}#"

            elif cmd in [":GG", "GG"]:
                # Get UTC offset in hours: sHH#
                if time.daylight and time.localtime().tm_isdst > 0:
                    offset_sec = time.altzone
                else:
                    offset_sec = time.timezone
                offset_hours = int(offset_sec / 3600)
                sign = "+" if offset_hours >= 0 else "-"
                return f"{sign}{abs(offset_hours):02d}#"

            # 3. Product, Version & Site Info
            elif cmd in [":GVP", "GVP"]:
                return "Kaukoputki#"

            elif cmd in [":GVN", "GVN"]:
                return "2.0#"

            elif cmd in [":GVD", "GVD"]:
                return "Sep 17 2026#"

            elif cmd in [":GVT", "GVT"]:
                return "12:00:00#"

            elif cmd in [":GVF", "GVF"]:
                return "Kaukoputki v2.0 Meade LX200#"

            elif cmd in [":Gt", "Gt"]:
                # Get Latitude: sDD*MM#
                lat = self.model.config.observatory.latitude_deg
                sign = "+" if lat >= 0 else "-"
                abs_lat = abs(lat)
                d = int(abs_lat)
                m = int((abs_lat - d) * 60)
                return f"{sign}{d:02d}*{m:02d}#"

            elif cmd in [":Gg", "Gg"]:
                # Get Longitude: DDD*MM# (Meade standard: degrees West 0..360)
                lon_east = self.model.config.observatory.longitude_deg
                lon_west = (360.0 - (lon_east % 360.0)) % 360.0
                d = int(lon_west)
                m = int((lon_west - d) * 60)
                return f"{d:03d}*{m:02d}#"

            elif cmd in [":GW", "GW"]:
                # Alignment status: P = Polar, T = Tracking
                return "PT#"

            elif cmd in [":GT", "GT"]:
                # Tracking frequency (Hz)
                return "60.0#"

            elif cmd in [":GSTAT", "GSTAT"]:
                return "0#"

            elif cmd in [":GM", "GM", ":GN", "GN", ":GO", "GO", ":GP", "GP"]:
                return "Jakokoski#"

            elif cmd in [":LI", "LI"]:
                return "None#"

            # 4. Target staging
            elif cmd.startswith((":Sr", "Sr")):
                val_str = cmd.replace(":Sr", "").replace("Sr", "").strip()
                try:
                    parts = val_str.split(":")
                    if len(parts) >= 2:
                        h = float(parts[0])
                        m = float(parts[1])
                        s = float(parts[2]) if len(parts) > 2 else 0.0
                        self.target_ra_hours = h + (m / 60.0) + (s / 3600.0)
                        return "1"
                except Exception as e:
                    logger.error(f"Error parsing LX200 RA {val_str}: {e}")
                return "0"

            elif cmd.startswith((":Sd", "Sd")):
                val_str = cmd.replace(":Sd", "").replace("Sd", "").strip()
                try:
                    sign = -1.0 if val_str.startswith("-") else 1.0
                    clean = val_str.lstrip("+-").replace("*", ":")
                    parts = clean.split(":")
                    if len(parts) >= 2:
                        d = float(parts[0])
                        m = float(parts[1])
                        s = float(parts[2]) if len(parts) > 2 else 0.0
                        self.target_dec_deg = sign * (d + (m / 60.0) + (s / 3600.0))
                        return "1"
                except Exception as e:
                    logger.error(f"Error parsing LX200 Dec {val_str}: {e}")
                return "0"

            # 5. Motion & Slew
            elif cmd in [":MS", "MS"]:
                if self.target_ra_hours is not None and self.target_dec_deg is not None:
                    try:
                        if self.model.is_parked:
                            self.model.unpark()
                        self.model.slew_to_coordinates(self.target_ra_hours, self.target_dec_deg, async_mode=True)
                        return "0"  # 0 = Slew possible and started
                    except SafetyLimitViolation as e:
                        logger.warning(f"LX200 Slew blocked by safety envelope: {e}")
                        return "1"  # 1 = Below horizon or limits
                    except Exception as e:
                        logger.error(f"LX200 Slew failed: {e}")
                        return "1"
                return "1"

            elif cmd in [":Q", "Q", ":Qn", ":Qs", ":Qe", ":Qw"]:
                self.model.abort_slew()
                return None

            elif cmd in [":CM", "CM"]:
                # Synchronize mount coordinates
                if self.target_ra_hours is not None and self.target_dec_deg is not None:
                    self.model.sync_to_coordinates(self.target_ra_hours, self.target_dec_deg)
                    return "M#"
                return "N#"

            elif cmd in [":D", "D"]:
                # Slewing status
                return "|#" if self.model.is_slewing else "#"

            elif cmd in [":U", "U"]:
                return None

            elif cmd.startswith((":St", "St", ":Sg", "Sg", ":SL", "SL", ":SC", "SC", ":SG", "SG")):
                return "1"

            elif cmd.startswith((":Rg", "Rg", ":Rc", "Rc", ":Rm", "Rm", ":Rs", "Rs")):
                return None

            elif cmd in [":hP", "hP"]:
                self.model.park()
                return None

            elif cmd in [":hU", "hU"]:
                self.model.unpark()
                return None

            elif cmd.startswith((":Me", ":Mw", ":Mn", ":Ms")):
                direction = cmd[2].lower()
                guide_rate = 0.5 * (15.041 / 3600.0)
                if direction == "e":
                    self.model.move_axis(0, guide_rate)
                elif direction == "w":
                    self.model.move_axis(0, -guide_rate)
                elif direction == "n":
                    self.model.move_axis(1, guide_rate)
                elif direction == "s":
                    self.model.move_axis(1, -guide_rate)
                return None

            # Fallbacks
            if cmd.startswith((":G", "G")):
                logger.debug(f"LX200 unhandled query '{cmd}', returning default '0#'")
                return "0#"

            if cmd.startswith((":S", "S")):
                logger.debug(f"LX200 unhandled set command '{cmd}', returning acknowledgment '1'")
                return "1"

            logger.debug(f"LX200 unhandled command '{cmd}'")
            return None

        except Exception as e:
            logger.exception(f"LX200 error executing command '{cmd}': {e}")
            if cmd.startswith((":G", "G")):
                return "0#"
            return None
