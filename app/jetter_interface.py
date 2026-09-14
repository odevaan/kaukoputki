import logging
import threading
import time
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

try:
    import serial
except ImportError:
    serial = None


class JetterProtocolError(Exception):
    """Exception raised for errors in Jetter controller communication."""
    pass


class MockJetterController:
    """
    High-fidelity software simulation of the Jetter Nano-B motion controller.
    Simulates:
      - 32-bit registers, flags, digital inputs/outputs.
      - Axis 2 (Declination, regs 12100-12199) and Axis 3 (RA/HA, regs 13100-13199).
      - Position control vs Speed control transitions.
      - Realistic velocity integration and in-position target flags.
    """
    def __init__(self):
        self.lock = threading.Lock()
        self.registers: Dict[int, int] = {}
        self.flags: Dict[int, int] = {}
        self.outputs: Dict[int, int] = {}
        self.inputs: Dict[int, int] = {}

        # Initialize Axis 2 (Dec: 121xx) and Axis 3 (RA: 13xx)
        # 12100: Status register (Bit 1 = In-Position, Bit 9 = Position Control)
        # Bit 1 = 1 (in-position initially)
        self.registers[12100] = (1 << 1)
        self.registers[13100] = (1 << 1)
        self.registers[12102] = 0  # Dec target position
        self.registers[13102] = 0  # RA target position
        self.registers[12109] = 0  # Dec actual position
        self.registers[13109] = 0  # RA actual position
        self.registers[12103] = 6000 # Dec speed
        self.registers[13103] = 6000 # RA speed
        self.registers[12122] = 32   # Dec resolution prescaler
        self.registers[13122] = 32   # RA resolution prescaler
        self.outputs[101] = 0        # Buzzer off

        self._running = True
        self._last_time = time.time()
        self._thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self._thread.start()

    def _simulation_loop(self):
        while self._running:
            time.sleep(0.02)
            now = time.time()
            dt = now - self._last_time
            self._last_time = now

            with self.lock:
                for axis_reg_base in [12100, 13100]:
                    status = self.registers.get(axis_reg_base, 0)
                    target = self.registers.get(axis_reg_base + 2, 0)
                    actual = self.registers.get(axis_reg_base + 9, 0)
                    speed = abs(self.registers.get(axis_reg_base + 3, 6000))
                    is_position_mode = bool(status & (1 << 9))

                    if is_position_mode:
                        diff = target - actual
                        if abs(diff) <= speed * dt:
                            self.registers[axis_reg_base + 9] = target
                            # Set in-position bit (Bit 1 = 1)
                            self.registers[axis_reg_base] |= (1 << 1)
                        else:
                            step = int(speed * dt) if diff > 0 else -int(speed * dt)
                            self.registers[axis_reg_base + 9] = actual + step
                            # Clear in-position bit (Bit 1 = 0)
                            self.registers[axis_reg_base] &= ~(1 << 1)
                    else:
                        # In speed mode, in-position bit is 1 (not slewing)
                        self.registers[axis_reg_base] |= (1 << 1)

    def read_register(self, address: int) -> int:
        with self.lock:
            return self.registers.get(address, 0)

    def write_register(self, address: int, value: int) -> None:
        with self.lock:
            self.registers[address] = int(value)
            # If target position changed on axis 2 or 3, clear in-position bit
            if address == 12102 and self.registers.get(12109, 0) != value:
                self.registers[12100] &= ~(1 << 1)
            elif address == 13102 and self.registers.get(13109, 0) != value:
                self.registers[13100] &= ~(1 << 1)

    def read_bit(self, address: int, bit: int) -> int:
        with self.lock:
            val = self.registers.get(address, 0)
            return 1 if (val & (1 << bit)) else 0

    def write_bit(self, address: int, bit: int, value: int) -> None:
        with self.lock:
            val = self.registers.get(address, 0)
            if value:
                val |= (1 << bit)
                # If enabling position mode (bit 9), clear in-position bit if target != actual
                if bit == 9:
                    target = self.registers.get(address + 2, 0)
                    actual = self.registers.get(address + 9, 0)
                    if target != actual:
                        val &= ~(1 << 1)
            else:
                val &= ~(1 << bit)
            self.registers[address] = val

    def read_output(self, address: int) -> int:
        with self.lock:
            return self.outputs.get(address, 0)

    def write_output(self, address: int, value: int) -> None:
        with self.lock:
            self.outputs[address] = 1 if value else 0

    def read_flag(self, address: int) -> int:
        with self.lock:
            return self.flags.get(address, 0)

    def write_flag(self, address: int, value: int) -> None:
        with self.lock:
            self.flags[address] = 1 if value else 0

    def stop(self):
        self._running = False


class JetterInterface:
    """
    Hardware communication interface for the Jetter Nano-B motion controller.
    Supports:
      - RS-232 serial connection via PySerial.
      - PCOM binary / register telegram protocol.
      - Automatic fallback to high-fidelity mock controller when testing or disconnected.
      - Thread-safe command execution and emergency abort.
    """
    STX = 0x02
    ETX = 0x03
    ACK = 0x06
    NAK = 0x15

    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 9600, timeout: float = 2.0, mock_mode: bool = False):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.mock_mode = mock_mode
        self._ser: Optional[serial.Serial] = None
        self._mock = MockJetterController() if mock_mode else None
        self._lock = threading.Lock()
        self._is_connected = False

        if not mock_mode:
            self.connect()

    @property
    def is_connected(self) -> bool:
        return self._is_connected or (self.mock_mode and self._mock is not None)

    def connect(self) -> bool:
        """Establishes connection to physical serial port or falls back to mock."""
        with self._lock:
            if self.mock_mode:
                self._is_connected = True
                return True

            if serial is None:
                logger.warning("pyserial is not installed. Falling back to Mock mode.")
                self.mock_mode = True
                self._mock = MockJetterController()
                self._is_connected = True
                return True

            try:
                self._ser = serial.Serial(
                    port=self.port,
                    baudrate=self.baudrate,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=self.timeout,
                    write_timeout=self.timeout
                )
                self._is_connected = True
                logger.info(f"Connected to Jetter Nano-B on {self.port} at {self.baudrate} baud.")
                return True
            except Exception as e:
                logger.warning(f"Unable to open serial port {self.port}: {e}. Switching to Mock controller.")
                self.mock_mode = True
                self._mock = MockJetterController()
                self._is_connected = True
                return True

    def disconnect(self) -> None:
        """Closes serial connection."""
        with self._lock:
            if self._ser and self._ser.is_open:
                try:
                    self._ser.close()
                except Exception as e:
                    logger.warning(f"Error closing serial port: {e}")
            self._ser = None
            self._is_connected = False
            logger.info("Jetter interface disconnected.")

    # -------------------------------------------------------------------------
    # Core Register and I/O Operations
    # -------------------------------------------------------------------------

    def get_register(self, address: int) -> int:
        """Reads a 32-bit signed register from the controller."""
        with self._lock:
            if self.mock_mode and self._mock:
                return self._mock.read_register(address)
            return self._serial_get_register(address)

    def set_register(self, address: int, value: int) -> bool:
        """Writes a 32-bit signed value to a controller register."""
        with self._lock:
            if self.mock_mode and self._mock:
                self._mock.write_register(address, value)
                return True
            return self._serial_set_register(address, value)

    def get_bit(self, address: int, bit: int) -> int:
        """Reads a specific bit (0..31) of a controller register."""
        with self._lock:
            if self.mock_mode and self._mock:
                return self._mock.read_bit(address, bit)
            val = self._serial_get_register(address)
            return 1 if (val & (1 << bit)) else 0

    def set_bit(self, address: int, bit: int, value: int) -> bool:
        """Sets a specific bit in a register using read-modify-write."""
        with self._lock:
            if self.mock_mode and self._mock:
                self._mock.write_bit(address, bit, value)
                return True
            curr = self._serial_get_register(address)
            if value:
                new_val = curr | (1 << bit)
            else:
                new_val = curr & ~(1 << bit)
            return self._serial_set_register(address, new_val)

    def get_output(self, address: int) -> int:
        """Reads digital output state."""
        with self._lock:
            if self.mock_mode and self._mock:
                return self._mock.read_output(address)
            return self._serial_get_io('o', address)

    def set_output(self, address: int, value: int) -> bool:
        """Sets digital output (e.g. output 101 for buzzer)."""
        with self._lock:
            if self.mock_mode and self._mock:
                self._mock.write_output(address, value)
                return True
            return self._serial_set_io('o', address, value)

    def get_flag(self, address: int) -> int:
        """Reads a boolean flag."""
        with self._lock:
            if self.mock_mode and self._mock:
                return self._mock.read_flag(address)
            return self._serial_get_io('h', address)

    def set_flag(self, address: int, value: int) -> bool:
        """Sets a boolean flag."""
        with self._lock:
            if self.mock_mode and self._mock:
                self._mock.write_flag(address, value)
                return True
            return self._serial_set_io('t', address, value)

    def abort_motion(self) -> None:
        """
        Emergency abort:
        Instantly halts motion by switching axes to Speed Control mode with 0 velocity,
        and turning off the movement buzzer.
        """
        logger.warning("EMERGENCY ABORT TRIGGERED ON JETTER CONTROLLER")
        # 1. Dec Axis (12100) -> Speed mode (Bit 9 = 0)
        self.set_bit(12100, 9, 0)
        self.set_register(12103, 0)

        # 2. RA Axis (13100) -> Speed mode (Bit 9 = 0)
        self.set_bit(13100, 9, 0)
        self.set_register(13103, 0)

        # 3. Buzzer (Output 101) off
        self.set_output(101, 0)

    # -------------------------------------------------------------------------
    # Low-Level Serial PCOM Framing Implementation
    # -------------------------------------------------------------------------

    def _calculate_checksum(self, payload: bytes) -> int:
        """Computes XOR checksum for Jetter telegram framing."""
        chk = 0
        for b in payload:
            chk ^= b
        return chk

    def _build_telegram(self, cmd_char: str, address: int, value: int = 0) -> bytes:
        """
        Constructs a telegram for Jetter Nano-B.
        Format: STX (0x02) | CMD | ADDR (ASCII dec) | VALUE (ASCII dec) | ETX (0x03) | CHK
        """
        body = f"{cmd_char}{address}:{value}".encode("ascii")
        chk = self._calculate_checksum(body)
        return bytes([self.STX]) + body + bytes([self.ETX, chk])

    def _send_and_receive(self, telegram: bytes) -> bytes:
        if not self._ser or not self._ser.is_open:
            raise JetterProtocolError("Serial port is not open")

        self._ser.reset_input_buffer()
        self._ser.write(telegram)
        self._ser.flush()

        response = bytearray()
        start_time = time.time()
        in_frame = False

        while time.time() - start_time < self.timeout:
            chunk = self._ser.read(1)
            if not chunk:
                continue
            b = chunk[0]
            if b == self.STX:
                response = bytearray()
                in_frame = True
            elif in_frame:
                response.append(b)
                if len(response) >= 2 and response[-2] == self.ETX:
                    # Received ETX and checksum
                    payload = response[:-2]
                    expected_chk = response[-1]
                    if self._calculate_checksum(payload) != expected_chk:
                        raise JetterProtocolError("Checksum mismatch in received Jetter frame")
                    return bytes(payload)

        if not response:
            raise JetterProtocolError(f"Timeout waiting for response from Jetter controller on {self.port}")
        return bytes(response)

    def _serial_get_register(self, address: int) -> int:
        telegram = self._build_telegram('g', address)
        try:
            resp_bytes = self._send_and_receive(telegram)
            val_str = resp_bytes.decode('ascii', errors='ignore').strip()
            return int(val_str)
        except Exception as e:
            logger.error(f"Failed to read register {address}: {e}")
            raise JetterProtocolError(f"Read register {address} failed: {e}")

    def _serial_set_register(self, address: int, value: int) -> bool:
        telegram = self._build_telegram('s', address, value)
        try:
            resp_bytes = self._send_and_receive(telegram)
            return True
        except Exception as e:
            logger.error(f"Failed to write register {address}={value}: {e}")
            raise JetterProtocolError(f"Write register {address} failed: {e}")

    def _serial_get_io(self, io_type: str, address: int) -> int:
        telegram = self._build_telegram(io_type, address)
        try:
            resp_bytes = self._send_and_receive(telegram)
            return int(resp_bytes.decode('ascii', errors='ignore').strip())
        except Exception as e:
            logger.error(f"Failed to read IO {io_type} at {address}: {e}")
            raise JetterProtocolError(f"Read IO failed: {e}")

    def _serial_set_io(self, io_type: str, address: int, value: int) -> bool:
        telegram = self._build_telegram(io_type, address, value)
        try:
            self._send_and_receive(telegram)
            return True
        except Exception as e:
            logger.error(f"Failed to set IO {io_type} at {address}={value}: {e}")
            raise JetterProtocolError(f"Set IO failed: {e}")
