import pytest
from fastapi.testclient import TestClient
from app.alpaca_server import app, model, config


@pytest.fixture(scope="module")
def client():
    config.serial.mock_mode = True
    with TestClient(app) as c:
        yield c


def test_management_api(client):
    r = client.get("/management/apiversions")
    assert r.status_code == 200
    data = r.json()
    assert data["ErrorNumber"] == 0
    assert 1 in data["Value"]

    r = client.get("/management/v1/description")
    assert r.status_code == 200
    data = r.json()
    assert "Jakokoski" in data["Value"]["ServerName"] or "Kaukoputki" in data["Value"]["ServerName"]

    r = client.get("/management/v1/configureddevices")
    assert r.status_code == 200
    data = r.json()
    devices = data["Value"]
    assert len(devices) > 0
    assert devices[0]["DeviceType"] == "Telescope"


def test_device_properties(client):
    # Connected
    r = client.get("/api/v1/telescope/0/connected")
    assert r.status_code == 200
    assert r.json()["Value"] is True

    # Name and description
    r = client.get("/api/v1/telescope/0/name")
    assert "Jetter" in r.json()["Value"]

    # Interface version
    r = client.get("/api/v1/telescope/0/interfaceversion")
    assert r.json()["Value"] == 3

    # Capabilities
    r = client.get("/api/v1/telescope/0/canabortslew")
    assert r.json()["Value"] is True
    r = client.get("/api/v1/telescope/0/canpark")
    assert r.json()["Value"] is True
    r = client.get("/api/v1/telescope/0/canslewasync")
    assert r.json()["Value"] is True

    # Coordinates
    r = client.get("/api/v1/telescope/0/rightascension")
    assert r.status_code == 200
    assert 0.0 <= r.json()["Value"] < 24.0

    r = client.get("/api/v1/telescope/0/declination")
    assert r.status_code == 200
    assert -90.0 <= r.json()["Value"] <= 90.0

    r = client.get("/api/v1/telescope/0/siderealtime")
    assert r.status_code == 200
    assert 0.0 <= r.json()["Value"] < 24.0


def test_calibration_and_safety_endpoints(client):
    # Calibration status
    r = client.get("/api/v1/telescope/0/calibration")
    assert r.status_code == 200
    data = r.json()["Value"]
    assert "is_calibrated" in data
    assert "recommended_action" in data

    # Read safety limits
    r = client.get("/api/v1/telescope/0/safety")
    assert r.status_code == 200
    safety = r.json()["Value"]
    assert safety["min_ha_deg"] == -220.0
    assert safety["max_ha_deg"] == 220.0

    # Update safety limits dynamically
    r = client.put("/api/v1/telescope/0/safety", json={"min_dec_deg": -40.0})
    assert r.status_code == 200
    r = client.get("/api/v1/telescope/0/safety")
    assert r.json()["Value"]["min_dec_deg"] == -40.0

    # Restore
    client.put("/api/v1/telescope/0/safety", json={"min_dec_deg": -50.0})


def test_motion_controls(client):
    # Unpark
    r = client.put("/api/v1/telescope/0/unpark")
    assert r.status_code == 200
    assert r.json()["ErrorNumber"] == 0

    # Check tracking
    r = client.get("/api/v1/telescope/0/tracking")
    assert r.json()["Value"] is True

    # Abort slew
    r = client.put("/api/v1/telescope/0/abortslew")
    assert r.status_code == 200
    assert r.json()["ErrorNumber"] == 0

    # Sync to coordinates
    r = client.put("/api/v1/telescope/0/synctocoordinates", json={
        "RightAscension": 12.0,
        "Declination": 45.0
    })
    assert r.status_code == 200
    assert r.json()["ErrorNumber"] == 0

    # Verify calibration status is now True
    r = client.get("/api/v1/telescope/0/calibration")
    assert r.json()["Value"]["is_calibrated"] is True
