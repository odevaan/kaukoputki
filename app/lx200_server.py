import logging
import socket
import threading
from typing import Optional

from app.telescope_model import TelescopeModel, SafetyLimitViolation

logger = logging.getLogger(__name__)

DEFAULT_LX200_PORT = 4030


class LX200Server:
    """
    Meade LX200 TCP Command Protocol Server.
    Provides direct network connectivity for KStars/Ekos (via indi_lx200generic),
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

                # Process commands separated by '#' or specific single-character prefixes
                while "#" in buffer or "\x06" in buffer:
                    if "\x06" in buffer and buffer.index("\x06") < buffer.find("#") if "#" in buffer else True:
                        # Alignment query byte (ACK / 0x06)
                        buffer = buffer[buffer.index("\x06") + 1:]
                        client_sock.sendall(b"P") # Polar alignment
                        continue

                    idx = buffer.index("#")
                    cmd = buffer[:idx].strip()
                    buffer = buffer[idx + 1:]

                    if cmd:
                        resp = self._execute_command(cmd)
                        if resp:
                            client_sock.sendall(resp.encode("latin1"))

        except Exception as e:
            logger.debug(f"LX200 client handler disconnected: {e}")
        finally:
            try:
                client_sock.close()
            except Exception:
                pass

    def _execute_command(self, cmd: str) -> Optional[str]:
        """
        Executes standard LX200 commands.
        """
        # 1. Coordinate queries
        if cmd == ":GR" or cmd == "GR":
            # Get RA: HH:MM:SS# or HH:MM.T#
            ra, _, _, _ = self.model.get_current_coordinates()
            h = int(ra)
            m = int((ra - h) * 60)
            s = int(((ra - h) * 60 - m) * 60)
            return f"{h:02d}:{m:02d}:{s:02d}#"

        elif cmd == ":GD" or cmd == "GD":
            # Get Dec: sDD*MM:SS# or sDD*MM#
            _, dec, _, _ = self.model.get_current_coordinates()
            sign = "+" if dec >= 0 else "-"
            abs_dec = abs(dec)
            d = int(abs_dec)
            m = int((abs_dec - d) * 60)
            s = int(((abs_dec - d) * 60 - m) * 60)
            return f"{sign}{d:02d}*{m:02d}:{s:02d}#"

        # 2. Coordinate staging
        elif cmd.startswith(":Sr") or cmd.startswith("Sr"):
            # Set Target RA: :SrHH:MM:SS# or :SrHH:MM.T#
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

        elif cmd.startswith(":Sd") or cmd.startswith("Sd"):
            # Set Target Dec: :SdsDD*MM# or :SdsDD*MM:SS#
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

        # 3. Motion & Slew
        elif cmd == ":MS" or cmd == "MS":
            # Slew to target coordinates
            if self.target_ra_hours is not None and self.target_dec_deg is not None:
                try:
                    if self.model.is_parked:
                        self.model.unpark()
                    self.model.slew_to_coordinates(self.target_ra_hours, self.target_dec_deg, async_mode=True)
                    return "0" # 0 = Slew possible and started
                except SafetyLimitViolation as e:
                    logger.warning(f"LX200 Slew blocked by safety envelope: {e}")
                    return "1" # 1 = Object below horizon or limits
                except Exception as e:
                    logger.error(f"LX200 Slew failed: {e}")
                    return "1"
            return "1"

        # 4. Abort
        elif cmd in [":Q", "Q", ":Qn", ":Qs", ":Qe", ":Qw"]:
            self.model.abort_slew()
            return None

        # 5. Synchronization (Plate Solve Sync)
        elif cmd == ":CM" or cmd == "CM":
            # Synchronize mount coordinates to current target coordinates
            if self.target_ra_hours is not None and self.target_dec_deg is not None:
                self.model.sync_to_coordinates(self.target_ra_hours, self.target_dec_deg)
                return "M#" # Coordinates matched
            return "N#"

        # 6. Status queries
        elif cmd == ":GW" or cmd == "GW":
            # Alignment status: P = Polar
            return "PT#"

        elif cmd == ":hP" or cmd == "hP":
            # Park mount
            self.model.park()
            return None

        elif cmd == ":hU" or cmd == "hU":
            # Unpark mount
            self.model.unpark()
            return None

        elif cmd.startswith(":Me") or cmd.startswith(":Mw") or cmd.startswith(":Mn") or cmd.startswith(":Ms"):
            # Move direction (Pulse guide / jog)
            direction = cmd[2].lower()
            guide_rate = 0.5 * (15.041 / 3600.0) # 0.5x sidereal in deg/sec
            if direction == "e":
                self.model.move_axis(0, guide_rate)
            elif direction == "w":
                self.model.move_axis(0, -guide_rate)
            elif direction == "n":
                self.model.move_axis(1, guide_rate)
            elif direction == "s":
                self.model.move_axis(1, -guide_rate)
            return None

        # Default fallback
        return None
