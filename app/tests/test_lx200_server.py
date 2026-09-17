import socket
import time
import pytest
from app.config import DriverConfig
from app.jetter_interface import JetterInterface
from app.telescope_model import TelescopeModel
from app.lx200_server import LX200Server


@pytest.fixture
def lx200():
    config = DriverConfig()
    config.serial.mock_mode = True
    jetter = JetterInterface(mock_mode=True)
    model = TelescopeModel(config=config, jetter=jetter)
    model.connect()
    server = LX200Server(model=model, host="127.0.0.1", port=4035)
    server.start()
    time.sleep(0.1)
    yield server
    server.stop()
    model.disconnect()


def send_cmd(port: int, cmd: str) -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("127.0.0.1", port))
        s.sendall(cmd.encode("latin1"))
        s.settimeout(2.0)
        resp = b""
        try:
            while b"#" not in resp and resp != b"1" and resp != b"0" and resp != b"P":
                chunk = s.recv(1024)
                if not chunk:
                    break
                resp += chunk
        except socket.timeout:
            pass
        return resp.decode("latin1")


def test_lx200_queries(lx200):
    # Query RA
    resp = send_cmd(4035, ":GR#")
    assert ":" in resp and resp.endswith("#")

    # Query Dec
    resp = send_cmd(4035, ":GD#")
    assert "*" in resp and resp.endswith("#")

    # Altitude & Azimuth
    resp = send_cmd(4035, ":GA#")
    assert "*" in resp and resp.endswith("#")
    resp = send_cmd(4035, ":GZ#")
    assert "*" in resp and resp.endswith("#")

    # Time & Date
    resp = send_cmd(4035, ":Gc#")
    assert resp == "24#"

    resp = send_cmd(4035, ":GS#")
    assert ":" in resp and resp.endswith("#")

    resp = send_cmd(4035, ":GL#")
    assert ":" in resp and resp.endswith("#")

    resp = send_cmd(4035, ":GC#")
    assert "/" in resp and resp.endswith("#")

    resp = send_cmd(4035, ":GG#")
    assert resp.endswith("#")

    # Product and version queries
    assert send_cmd(4035, ":GVP#") == "Kaukoputki#"
    assert send_cmd(4035, ":GVN#") == "2.0#"
    assert send_cmd(4035, ":GVF#") == "Kaukoputki v2.0 Meade LX200#"

    # Unknown query and set fallbacks (must never hang INDI)
    assert send_cmd(4035, ":GUNKNOWN#") == "0#"
    assert send_cmd(4035, ":SUNKNOWN#") == "1"

    # Alignment ACK
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("127.0.0.1", 4035))
        s.sendall(b"\x06")
        s.settimeout(1.0)
        ack = s.recv(10)
        assert ack == b"P"


def test_lx200_slew_and_sync(lx200):
    # Set target coordinates
    resp = send_cmd(4035, ":Sr12:30:00#")
    assert resp == "1"
    assert lx200.target_ra_hours == 12.5

    resp = send_cmd(4035, ":Sd+45*00:00#")
    assert resp == "1"
    assert lx200.target_dec_deg == 45.0

    # Query target coordinates
    resp = send_cmd(4035, ":Gr#")
    assert "12:30:00#" in resp
    resp = send_cmd(4035, ":Gd#")
    assert "+45*00:00#" in resp

    # Sync
    resp = send_cmd(4035, ":CM#")
    assert "Coordinates matched" in resp or "M#" in resp
    assert lx200.model.is_calibrated

    # Slew
    resp = send_cmd(4035, ":MS#")
    assert resp == "0"

