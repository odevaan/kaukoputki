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
    iface.disconnect()


def test_jetter_24bit_integer_conversion():
    # Boundary tests
    assert JetterInterface.to_24bit_unsigned(0) == 0
    assert JetterInterface.from_24bit_signed(0) == 0

    assert JetterInterface.to_24bit_unsigned(8388607) == 0x007FFFFF
    assert JetterInterface.from_24bit_signed(0x007FFFFF) == 8388607

    assert JetterInterface.to_24bit_unsigned(-1) == 0x00FFFFFF
    assert JetterInterface.from_24bit_signed(0x00FFFFFF) == -1

    assert JetterInterface.to_24bit_unsigned(-8388608) == 0x00800000
    assert JetterInterface.from_24bit_signed(0x00800000) == -8388608

    # Arbitrary negative and positive values
    test_vals = [12345, -67890, 5000000, -5000000, -100, 100]
    for v in test_vals:
        encoded = JetterInterface.to_24bit_unsigned(v)
        # Upper 8 bits (bits 24..31) must be strictly 0
        assert (encoded & 0xFF000000) == 0
        decoded = JetterInterface.from_24bit_signed(encoded)
        assert decoded == v


def test_pcom7_telegram_framing():
    iface = JetterInterface(mock_mode=True)
    try:
        # Build register set telegram: 's', 12102, 100
        tgram = iface._build_telegram('s', 12102, 100)
        assert tgram[0] == 0xDA  # Jetter PCOM7 STX
        assert tgram[-1] == 0xDB # Jetter PCOM7 ETX

        # Check payload and BCC
        body = b"s12102:100"
        expected_bcc = iface._calculate_checksum(body)
        assert tgram[1:-2] == body
        assert tgram[-2] == expected_bcc
    finally:
        iface.disconnect()

