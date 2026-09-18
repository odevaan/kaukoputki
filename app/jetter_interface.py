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
        self.lock = threading.RLock()
        self.registers: Dict[int, int] = {}
        self.flags: Dict[int, int] = {}
        self.outputs: Dict[int, int] = {}
        self.inputs: Dict[int, int] = {}

        # Initialize Axis 2 (Dec: 121xx) and Axis 3 (RA: 13xx)
        # 12100: Status register (Bit 1 = In-Position, Bit 9 = Position Control)
        # Bit 1 = 1 (in-position initially, Jetter 1-based indexing)
        self.registers[12100] = (1 << 0)
        self.registers[13100] = (1 << 0)
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
                    target = JetterInterface.from_24bit_signed(self.registers.get(axis_reg_base + 2, 0))
                    actual = JetterInterface.from_24bit_signed(self.registers.get(axis_reg_base + 9, 0))
                    speed = abs(self.registers.get(axis_reg_base + 3, 6000))
                    is_position_mode = bool(self.read_bit(axis_reg_base, 9))

                    if is_position_mode:
                        diff = target - actual
                        if abs(diff) <= speed * dt:
                            self.registers[axis_reg_base + 9] = JetterInterface.to_24bit_unsigned(target)
                            # Set in-position bit (Bit 1 = 1)
                            self.write_bit(axis_reg_base, 1, 1)
                        else:
                            step = int(speed * dt) if diff > 0 else -int(speed * dt)
                            new_actual = actual + step
                            self.registers[axis_reg_base + 9] = JetterInterface.to_24bit_unsigned(new_actual)
                            # Clear in-position bit (Bit 1 = 0)
                            self.write_bit(axis_reg_base, 1, 0)
                    else:
                        # In speed mode, in-position bit is 1 (not slewing)
                        self.write_bit(axis_reg_base, 1, 1)

    def read_register(self, address: int) -> int:
        with self.lock:
            val = self.registers.get(address, 0)
            return JetterInterface.from_24bit_signed(val)

    def write_register(self, address: int, value: int) -> None:
        with self.lock:
            val_24 = JetterInterface.to_24bit_unsigned(value)
            self.registers[address] = val_24
            # If target position changed on axis 2 or 3, clear in-position bit
            if address == 12102 and self.registers.get(12109, 0) != val_24:
                self.write_bit(12100, 1, 0)
            elif address == 13102 and self.registers.get(13109, 0) != val_24:
                self.write_bit(13100, 1, 0)

    def read_bit(self, address: int, bit: int) -> int:
        with self.lock:
            val = self.registers.get(address, 0)
            shift = bit - 1 if bit >= 1 else bit
            return 1 if (val & (1 << shift)) else 0

    def write_bit(self, address: int, bit: int, value: int) -> None:
        with self.lock:
            shift = bit - 1 if bit >= 1 else bit
            val = self.registers.get(address, 0)
            if value:
                val |= (1 << shift)
                # If enabling position mode (bit 9), clear in-position bit (bit 1) if target != actual
                if bit == 9:
                    target = self.registers.get(address + 2, 0)
                    actual = self.registers.get(address + 9, 0)
                    if target != actual:
                        val &= ~(1 << 0)
            else:
                val &= ~(1 << shift)
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
      - RS-232 serial connection via PySerial (9600 baud, 8N1, Pin 7 Ground).
      - PCOM7 binary / register telegram protocol (0xDA STX, 0xDB ETX, XOR BCC).
      - 24-bit integer encoding with upper-byte zero masking (& 0x00FFFFFF).
      - Base-1 bit indexing (bits 1..24).
      - Automatic fallback to high-fidelity mock controller when testing or disconnected.
      - Thread-safe command execution and emergency abort.
    """
    STX = 0xDA  # 218 decimal: Jetter PCOM7 Start of Text
    ETX = 0xDB  # 219 decimal: Jetter PCOM7 End of Text
    ACK = 0x06
    NAK = 0x15

    @staticmethod
    def to_24bit_unsigned(val: int) -> int:
        """
        Converts a signed integer to a sanitized 24-bit representation (0x000000..0x00FFFFFF).
        Strictly clears bits 24..31 to prevent Jetter Nano-B 'Value is Incorrect' faults.
        Range: -8,388,608 to +8,388,607.
        """
        val = int(val)
        if val < -8388608:
            val = -8388608
        elif val > 8388607:
            val = 8388607
        if val < 0:
            return (val + (1 << 24)) & 0x00FFFFFF
        return val & 0x00FFFFFF

    @staticmethod
    def from_24bit_signed(val_24: int) -> int:
        """
        Converts a 24-bit unsigned integer back into a signed Python integer.
        """
        val_24 = int(val_24) & 0x00FFFFFF
        if val_24 & 0x800000:
            return val_24 - (1 << 24)
        return val_24

    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 9600, timeout: float = 2.0, mock_mode: bool = False):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.mock_mode = mock_mode
        self._ser: Optional[serial.Serial] = None
        self._mock = MockJetterController() if mock_mode else None
        self._lock = threading.RLock()
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
        """Reads a 24-bit signed register from the controller."""
        with self._lock:
            if self.mock_mode and self._mock:
                return self._mock.read_register(address)
            return self._serial_get_register(address)

    def set_register(self, address: int, value: int) -> bool:
        """Writes a 24-bit signed value to a controller register."""
        with self._lock:
            if self.mock_mode and self._mock:
                self._mock.write_register(address, value)
                return True
            return self._serial_set_register(address, value)

    def get_bit(self, address: int, bit: int) -> int:
        """Reads a specific bit (1..24, base-1 indexing) of a controller register."""
        with self._lock:
            if self.mock_mode and self._mock:
                return self._mock.read_bit(address, bit)
            val = self._serial_get_register(address)
            val_24 = self.to_24bit_unsigned(val)
            shift = bit - 1 if bit >= 1 else bit
            return 1 if (val_24 & (1 << shift)) else 0

    def set_bit(self, address: int, bit: int, value: int) -> bool:
        """Sets a specific bit (1..24, base-1 indexing) in a register using read-modify-write."""
        with self._lock:
            if self.mock_mode and self._mock:
                self._mock.write_bit(address, bit, value)
                return True
            curr = self._serial_get_register(address)
            curr_24 = self.to_24bit_unsigned(curr)
            shift = bit - 1 if bit >= 1 else bit
            if value:
                new_val_24 = curr_24 | (1 << shift)
            else:
                new_val_24 = curr_24 & ~(1 << shift)
            return self._serial_set_register(address, self.from_24bit_signed(new_val_24))

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
    # Low-Level Serial PCOM7 Framing Implementation
    # -------------------------------------------------------------------------

    def _calculate_checksum(self, payload: bytes) -> int:
        """Computes XOR Block Check Character (BCC) for Jetter telegram framing."""
        chk = 0
        for b in payload:
            chk ^= b
        return chk

    def _build_telegram(self, cmd_char: str, address: int, value: Optional[int] = None) -> bytes:
        """
        Constructs a PCOM7 telegram for Jetter Nano-B.
        Format: STX (0xDA) | CMD | ADDR | [:VALUE] | BCC | ETX (0xDB)
        """
        if value is not None:
            body = f"{cmd_char}{address}:{value}".encode("ascii")
        else:
            body = f"{cmd_char}{address}".encode("ascii")
        bcc = self._calculate_checksum(body)
        return bytes([self.STX]) + body + bytes([bcc, self.ETX])

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
            if b in (self.STX, 0x02):
                response = bytearray()
                in_frame = True
            elif in_frame:
                if b in (self.ETX, 0x03):
                    # End of frame reached. Format: payload | BCC
                    if len(response) >= 1:
                        payload = response[:-1]
                        expected_bcc = response[-1]
                        calc_bcc = self._calculate_checksum(payload)
                        if calc_bcc != expected_bcc:
                            logger.warning(f"BCC mismatch in Jetter response: calc={calc_bcc}, exp={expected_bcc}")
                        return bytes(payload)
                    return bytes(response)
                response.append(b)

        if not response:
            raise JetterProtocolError(f"Timeout waiting for response from Jetter controller on {self.port}")
        return bytes(response)

    def _serial_get_register(self, address: int) -> int:
        telegram = self._build_telegram('g', address)
        try:
            resp_bytes = self._send_and_receive(telegram)
            val_str = resp_bytes.decode('ascii', errors='ignore').strip()
            raw_int = int(val_str)
            return self.from_24bit_signed(raw_int)
        except Exception as e:
            logger.error(f"Failed to read register {address}: {e}")
            raise JetterProtocolError(f"Read register {address} failed: {e}")

    def _serial_set_register(self, address: int, value: int) -> bool:
        val_24 = self.to_24bit_unsigned(value)
        telegram = self._build_telegram('s', address, val_24)
        try:
            self._send_and_receive(telegram)
            return True
        except Exception as e:
            logger.error(f"Failed to write register {address}={value} ({val_24}): {e}")
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

