import time
import pytest
from app.jetter_interface import JetterInterface, MockJetterController


def test_mock_controller_registers():
    mock = MockJetterController()
    try:
        # Initial status
        assert mock.read_register(12122) == 32
        assert mock.read_register(13122) == 32

        # Write and read registers
        mock.write_register(12102, 12345)
        assert mock.read_register(12102) == 12345

        mock.write_register(13102, -67890)
        assert mock.read_register(13102) == -67890

        # Bit operations
        mock.write_bit(12100, 9, 1) # Set bit 9
        assert mock.read_bit(12100, 9) == 1
        mock.write_bit(12100, 9, 0) # Clear bit 9
        assert mock.read_bit(12100, 9) == 0

        # Output / Buzzer
        mock.write_output(101, 1)
        assert mock.read_output(101) == 1
        mock.write_output(101, 0)
        assert mock.read_output(101) == 0
    finally:
        mock.stop()


def test_jetter_interface_mock_mode():
    iface = JetterInterface(mock_mode=True)
    assert iface.is_connected

    # Set and get register
    iface.set_register(12102, 54321)
    assert iface.get_register(12102) == 54321

    # Set and get bit
    iface.set_bit(12100, 9, 1)
    assert iface.get_bit(12100, 9) == 1

    # Output (buzzer)
    iface.set_output(101, 1)
    assert iface.get_output(101) == 1

    # Emergency abort
    iface.abort_motion()
    # Check that bit 9 of 12100 and 13100 is 0 (speed control)
    assert iface.get_bit(12100, 9) == 0
    assert iface.get_bit(13100, 9) == 0
    # Check speed is 0
    assert iface.get_register(12103) == 0
    assert iface.get_register(13103) == 0
    # Buzzer off
    assert iface.get_output(101) == 0

    iface.disconnect()
