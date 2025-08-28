import serial
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Nanomex:
    """
    This class provides an interface to the Nanomex B telescope controller.
    It aims to replicate the functionality of the original `nanocom.m` MATLAB script.
    """
    def __init__(self, port='COM1', baudrate=9600, timeout=1, testing=False):
        """
        Initializes the Nanomex controller interface.

        Args:
            port (str): The serial port to connect to (e.g., 'COM1' or '/dev/ttyS0').
            baudrate (int): The communication speed.
            timeout (int): The read timeout in seconds.
            testing (bool): If True, the class will operate in testing mode without
                            a real serial connection.
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.testing = testing
        self.ser = None

        if not self.testing:
            try:
                self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
                logging.info(f"Successfully connected to serial port {self.port}")
            except serial.SerialException as e:
                logging.error(f"Failed to connect to serial port {self.port}: {e}")
                # In a real application, you might want to raise the exception
                # or handle it more gracefully.
                self.ser = None
        else:
            logging.info("Nanomex running in testing mode.")

    def _send_command(self, ctype, address, value=0, bit_num=0):
        """
        A private method to send commands to the controller.
        This is a placeholder for the actual command protocol.
        The original MATLAB script used an external program (NANOCOM.EXE) or a MEX function.
        Here, we would implement the serial communication protocol directly.
        """
        if self.testing:
            logging.info(f"TESTING: Sent command: type={ctype}, address={address}, value={value}, bit_num={bit_num}")
            # Simulate a successful response
            return 0, 0

        if not self.ser or not self.ser.is_open:
            logging.error("Serial port not available.")
            return None, -1

        # This is where the actual protocol to talk to the Nanomex would be implemented.
        # It would involve packing the command and data into a binary format,
        # writing it to the serial port, and reading the response.
        # For now, we'll just log the action.
        command = f"{ctype} {address} {value} {bit_num}\n"
        try:
            self.ser.write(command.encode('ascii'))
            response = self.ser.readline().decode('ascii').strip()
            logging.info(f"Sent: {command.strip()}, Received: {response}")
            # This is a mock response parsing. The actual implementation would be more complex.
            parts = response.split()
            if len(parts) >= 2 and parts[1] == 'OK':
                 return int(parts[0]), 0
            else:
                 return None, -1 # Error
        except serial.SerialException as e:
            logging.error(f"Error during serial communication: {e}")
            return None, -1

    def get_reg(self, address):
        """Reads a register."""
        return self._send_command('g', address)

    def set_reg(self, address, value):
        """Writes to a register."""
        return self._send_command('s', address, value)

    def get_flag(self, address):
        """Reads a flag."""
        return self._send_command('h', address)

    def set_flag(self, address, value):
        """Sets a flag."""
        return self._send_command('t', address, value)

    def get_input(self, address):
        """Reads an input port."""
        return self._send_command('i', address)

    def set_output(self, address, value):
        """Sets an output port."""
        return self._send_command('o', address, value)

    def get_bit(self, address, bit_num):
        """Reads a specific bit from a register."""
        # The original MATLAB code did this with a special command 'r'
        return self._send_command('r', address, bit_num=bit_num)

    def set_bit(self, address, bit_num, value):
        """Sets a specific bit in a register."""
        # The MATLAB script implemented this as a read-modify-write operation.
        # We can do the same.
        current_val, status = self.get_reg(address)
        if status != 0:
            logging.error("Failed to read register for set_bit operation.")
            return None, status

        if value == 1:
            new_val = current_val | (1 << bit_num)
        else:
            new_val = current_val & ~(1 << bit_num)

        return self.set_reg(address, new_val)

    def close(self):
        """Closes the serial connection."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            logging.info("Serial port closed.")

# Example usage (for testing purposes)
if __name__ == '__main__':
    # To test this, you would need a virtual serial port loopback pair (e.g., com0com on Windows)
    # or run with testing=True
    nanomex_controller = Nanomex(port='COM1', testing=True)

    # Example operations
    val, status = nanomex_controller.get_reg(1024)
    if status == 0:
        print(f"Read register 1024, value: {val}")

    status = nanomex_controller.set_reg(1024, 5)
    if status == 0:
        print("Set register 1024 to 5")

    nanomex_controller.close()
