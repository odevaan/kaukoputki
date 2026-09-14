import logging
import threading
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

from fastapi import Body, FastAPI, Form, HTTPException, Query, Request
from fastapi.responses import JSONResponse
import uvicorn

from app.alpaca_discovery import AlpacaDiscoveryServer
from app.config import DriverConfig, SafetyLimits, load_config, save_config
from app.telescope_model import SafetyLimitViolation, TelescopeModel

logger = logging.getLogger(__name__)

# Global state
config: DriverConfig = load_config()
model: TelescopeModel = TelescopeModel(config=config)
discovery_server: Optional[AlpacaDiscoveryServer] = None
server_transaction_id = 0
tx_lock = threading.Lock()


def get_next_server_tx_id() -> int:
    global server_transaction_id
    with tx_lock:
        server_transaction_id += 1
        return server_transaction_id


def alpaca_response(
    value: Any = None,
    client_tx_id: int = 0,
    error_number: int = 0,
    error_message: str = ""
) -> Dict[str, Any]:
    """Formats standard ASCOM Alpaca REST response envelope."""
    return {
        "Value": value,
        "ClientTransactionID": client_tx_id,
        "ServerTransactionID": get_next_server_tx_id(),
        "ErrorNumber": error_number,
        "ErrorMessage": error_message,
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: auto-connect model & start discovery
    global discovery_server
    logger.info("Starting Kaukoputki Alpaca Telescope Driver Service...")
    model.connect()
    if config.enable_discovery:
        discovery_server = AlpacaDiscoveryServer(alpaca_port=config.alpaca_port)
        discovery_server.start()
    yield
    # Shutdown
    if discovery_server:
        discovery_server.stop()
    model.disconnect()
    logger.info("Kaukoputki Alpaca Telescope Driver Service stopped.")


app = FastAPI(
    title="Kaukoputki ASCOM Alpaca Telescope Driver",
    description="ASCOM Alpaca V3 compliant server for Jetter Nano-B telescope motion controller",
    version="2.0.0",
    lifespan=lifespan
)


# -----------------------------------------------------------------------------
# ASCOM Alpaca Management API Endpoints
# -----------------------------------------------------------------------------

@app.get("/management/apiversions")
def get_api_versions(ClientTransactionID: int = Query(0)):
    return alpaca_response(value=[1], client_tx_id=ClientTransactionID)


@app.get("/management/v1/description")
def get_server_description(ClientTransactionID: int = Query(0)):
    desc = {
        "ServerName": "Kaukoputki Jetter Nano-B Telescope Server",
        "Manufacturer": "Jakokoski Observatory",
        "ManufacturerVersion": "2.0.0",
        "Location": config.observatory.name,
    }
    return alpaca_response(value=desc, client_tx_id=ClientTransactionID)


@app.get("/management/v1/configureddevices")
def get_configured_devices(ClientTransactionID: int = Query(0)):
    devices = [
        {
            "DeviceName": "Jakokoski Jetter Nano-B Equatorial Mount",
            "DeviceType": "Telescope",
            "DeviceNumber": 0,
            "UniqueID": "8b5f3a09-6467-4e92-9a3d-b4b104928dbf",
        }
    ]
    return alpaca_response(value=devices, client_tx_id=ClientTransactionID)


# -----------------------------------------------------------------------------
# ASCOM Alpaca Telescope Device API Endpoints (/api/v1/telescope/0/...)
# -----------------------------------------------------------------------------

@app.get("/api/v1/telescope/0/connected")
def get_connected(ClientTransactionID: int = Query(0)):
    return alpaca_response(value=model.is_connected, client_tx_id=ClientTransactionID)


@app.put("/api/v1/telescope/0/connected")
async def set_connected(
    request: Request,
    Connected: Optional[bool] = Form(None),
    ClientTransactionID: int = Form(0)
):
    # Support form body, query param, or JSON body
    if Connected is None:
        try:
            body = await request.json()
            Connected = body.get("Connected", True)
            ClientTransactionID = body.get("ClientTransactionID", 0)
        except Exception:
            Connected = True

    if Connected:
        model.connect()
    else:
        model.disconnect()
    return alpaca_response(client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/name")
def get_name(ClientTransactionID: int = Query(0)):
    return alpaca_response(value="Jakokoski Jetter Telescope", client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/description")
def get_description(ClientTransactionID: int = Query(0)):
    return alpaca_response(
        value="Jetter Nano-B Equatorial Mount with real-time software safety envelopes",
        client_tx_id=ClientTransactionID
    )


@app.get("/api/v1/telescope/0/driverinfo")
def get_driver_info(ClientTransactionID: int = Query(0)):
    return alpaca_response(
        value="Reverse-engineered cross-platform driver replacing legacy Windows 98 MATLAB control",
        client_tx_id=ClientTransactionID
    )


@app.get("/api/v1/telescope/0/driverversion")
def get_driver_version(ClientTransactionID: int = Query(0)):
    return alpaca_response(value="2.0.0", client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/interfaceversion")
def get_interface_version(ClientTransactionID: int = Query(0)):
    return alpaca_response(value=3, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/alignmentmode")
def get_alignment_mode(ClientTransactionID: int = Query(0)):
    # 1 = Polar (Equatorial)
    return alpaca_response(value=1, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/athome")
def get_at_home(ClientTransactionID: int = Query(0)):
    return alpaca_response(value=False, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/atpark")
def get_at_park(ClientTransactionID: int = Query(0)):
    return alpaca_response(value=model.is_parked, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/canabortslew")
def get_can_abort_slew(ClientTransactionID: int = Query(0)):
    return alpaca_response(value=True, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/canfindhome")
def get_can_find_home(ClientTransactionID: int = Query(0)):
    return alpaca_response(value=False, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/canpark")
def get_can_park(ClientTransactionID: int = Query(0)):
    return alpaca_response(value=True, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/canunpark")
def get_can_unpark(ClientTransactionID: int = Query(0)):
    return alpaca_response(value=True, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/cansetpark")
def get_can_set_park(ClientTransactionID: int = Query(0)):
    return alpaca_response(value=False, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/canslew")
def get_can_slew(ClientTransactionID: int = Query(0)):
    return alpaca_response(value=True, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/canslewasync")
def get_can_slew_async(ClientTransactionID: int = Query(0)):
    return alpaca_response(value=True, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/canslewaltaz")
def get_can_slew_altaz(ClientTransactionID: int = Query(0)):
    return alpaca_response(value=False, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/canslewaltazasync")
def get_can_slew_altaz_async(ClientTransactionID: int = Query(0)):
    return alpaca_response(value=False, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/cansync")
def get_can_sync(ClientTransactionID: int = Query(0)):
    return alpaca_response(value=True, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/cansyncaltaz")
def get_can_sync_altaz(ClientTransactionID: int = Query(0)):
    return alpaca_response(value=False, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/cansettracking")
def get_can_set_tracking(ClientTransactionID: int = Query(0)):
    return alpaca_response(value=True, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/canmoveaxis")
def get_can_move_axis(ClientTransactionID: int = Query(0)):
    return alpaca_response(value=True, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/canpulseguide")
def get_can_pulse_guide(ClientTransactionID: int = Query(0)):
    return alpaca_response(value=True, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/rightascension")
def get_right_ascension(ClientTransactionID: int = Query(0)):
    ra, _, _, _ = model.get_current_coordinates()
    return alpaca_response(value=ra, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/declination")
def get_declination(ClientTransactionID: int = Query(0)):
    _, dec, _, _ = model.get_current_coordinates()
    return alpaca_response(value=dec, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/altitude")
def get_altitude(ClientTransactionID: int = Query(0)):
    _, _, alt, _ = model.get_current_coordinates()
    return alpaca_response(value=alt, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/azimuth")
def get_azimuth(ClientTransactionID: int = Query(0)):
    _, _, _, az = model.get_current_coordinates()
    return alpaca_response(value=az, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/siderealtime")
def get_sidereal_time(ClientTransactionID: int = Query(0)):
    lst = model.get_local_sidereal_time_hours()
    return alpaca_response(value=lst, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/sitelatitude")
def get_site_latitude(ClientTransactionID: int = Query(0)):
    return alpaca_response(value=config.observatory.latitude_deg, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/sitelongitude")
def get_site_longitude(ClientTransactionID: int = Query(0)):
    return alpaca_response(value=config.observatory.longitude_deg, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/siteelevation")
def get_site_elevation(ClientTransactionID: int = Query(0)):
    return alpaca_response(value=config.observatory.elevation_m, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/slewing")
def get_slewing(ClientTransactionID: int = Query(0)):
    return alpaca_response(value=model.is_slewing, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/tracking")
def get_tracking(ClientTransactionID: int = Query(0)):
    return alpaca_response(value=model.is_tracking, client_tx_id=ClientTransactionID)


@app.put("/api/v1/telescope/0/tracking")
async def set_tracking(
    request: Request,
    Tracking: Optional[bool] = Form(None),
    ClientTransactionID: int = Form(0)
):
    if Tracking is None:
        try:
            body = await request.json()
            Tracking = body.get("Tracking", True)
            ClientTransactionID = body.get("ClientTransactionID", 0)
        except Exception:
            Tracking = True
    try:
        model.set_tracking(bool(Tracking))
        return alpaca_response(client_tx_id=ClientTransactionID)
    except Exception as e:
        return alpaca_response(client_tx_id=ClientTransactionID, error_number=0x400, error_message=str(e))


@app.get("/api/v1/telescope/0/trackingrate")
def get_tracking_rate(ClientTransactionID: int = Query(0)):
    # 0 = driveSidereal
    return alpaca_response(value=0, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/trackingrates")
def get_tracking_rates(ClientTransactionID: int = Query(0)):
    return alpaca_response(value=[0], client_tx_id=ClientTransactionID)


@app.put("/api/v1/telescope/0/slewtocoordinates")
async def slew_to_coordinates_sync(
    request: Request,
    RightAscension: Optional[float] = Form(None),
    Declination: Optional[float] = Form(None),
    ClientTransactionID: int = Form(0)
):
    if RightAscension is None or Declination is None:
        try:
            body = await request.json()
            RightAscension = body.get("RightAscension")
            Declination = body.get("Declination")
            ClientTransactionID = body.get("ClientTransactionID", 0)
        except Exception:
            pass

    if RightAscension is None or Declination is None:
        return alpaca_response(
            client_tx_id=ClientTransactionID,
            error_number=0x401,
            error_message="Missing RightAscension or Declination parameter"
        )

    try:
        model.slew_to_coordinates(RightAscension, Declination, async_mode=False)
        return alpaca_response(client_tx_id=ClientTransactionID)
    except SafetyLimitViolation as e:
        return alpaca_response(client_tx_id=ClientTransactionID, error_number=0x400, error_message=f"Safety violation: {e}")
    except Exception as e:
        return alpaca_response(client_tx_id=ClientTransactionID, error_number=0x400, error_message=str(e))


@app.put("/api/v1/telescope/0/slewtocoordinatesasync")
async def slew_to_coordinates_async(
    request: Request,
    RightAscension: Optional[float] = Form(None),
    Declination: Optional[float] = Form(None),
    ClientTransactionID: int = Form(0)
):
    if RightAscension is None or Declination is None:
        try:
            body = await request.json()
            RightAscension = body.get("RightAscension")
            Declination = body.get("Declination")
            ClientTransactionID = body.get("ClientTransactionID", 0)
        except Exception:
            pass

    if RightAscension is None or Declination is None:
        return alpaca_response(
            client_tx_id=ClientTransactionID,
            error_number=0x401,
            error_message="Missing RightAscension or Declination parameter"
        )

    try:
        model.slew_to_coordinates(RightAscension, Declination, async_mode=True)
        return alpaca_response(client_tx_id=ClientTransactionID)
    except SafetyLimitViolation as e:
        return alpaca_response(client_tx_id=ClientTransactionID, error_number=0x400, error_message=f"Safety violation: {e}")
    except Exception as e:
        return alpaca_response(client_tx_id=ClientTransactionID, error_number=0x400, error_message=str(e))


@app.put("/api/v1/telescope/0/abortslew")
def abort_slew(ClientTransactionID: int = Form(0)):
    model.abort_slew()
    return alpaca_response(client_tx_id=ClientTransactionID)


@app.put("/api/v1/telescope/0/park")
def park(ClientTransactionID: int = Form(0)):
    try:
        model.park()
        return alpaca_response(client_tx_id=ClientTransactionID)
    except Exception as e:
        return alpaca_response(client_tx_id=ClientTransactionID, error_number=0x400, error_message=str(e))


@app.put("/api/v1/telescope/0/unpark")
def unpark(ClientTransactionID: int = Form(0)):
    try:
        model.unpark()
        return alpaca_response(client_tx_id=ClientTransactionID)
    except Exception as e:
        return alpaca_response(client_tx_id=ClientTransactionID, error_number=0x400, error_message=str(e))


@app.put("/api/v1/telescope/0/synctocoordinates")
async def sync_to_coordinates(
    request: Request,
    RightAscension: Optional[float] = Form(None),
    Declination: Optional[float] = Form(None),
    ClientTransactionID: int = Form(0)
):
    if RightAscension is None or Declination is None:
        try:
            body = await request.json()
            RightAscension = body.get("RightAscension")
            Declination = body.get("Declination")
            ClientTransactionID = body.get("ClientTransactionID", 0)
        except Exception:
            pass

    if RightAscension is None or Declination is None:
        return alpaca_response(
            client_tx_id=ClientTransactionID,
            error_number=0x401,
            error_message="Missing RightAscension or Declination parameter"
        )

    try:
        model.sync_to_coordinates(RightAscension, Declination)
        return alpaca_response(client_tx_id=ClientTransactionID)
    except Exception as e:
        return alpaca_response(client_tx_id=ClientTransactionID, error_number=0x400, error_message=str(e))


@app.put("/api/v1/telescope/0/moveaxis")
async def move_axis(
    request: Request,
    Axis: Optional[int] = Form(None),
    Rate: Optional[float] = Form(None),
    ClientTransactionID: int = Form(0)
):
    if Axis is None or Rate is None:
        try:
            body = await request.json()
            Axis = body.get("Axis")
            Rate = body.get("Rate")
            ClientTransactionID = body.get("ClientTransactionID", 0)
        except Exception:
            pass

    if Axis is None or Rate is None:
        return alpaca_response(client_tx_id=ClientTransactionID, error_number=0x401, error_message="Missing Axis or Rate")

    try:
        model.move_axis(Axis, Rate)
        return alpaca_response(client_tx_id=ClientTransactionID)
    except Exception as e:
        return alpaca_response(client_tx_id=ClientTransactionID, error_number=0x400, error_message=str(e))


# -----------------------------------------------------------------------------
# Custom Safety & Calibration Management Endpoints
# -----------------------------------------------------------------------------

@app.get("/api/v1/telescope/0/calibration")
def get_calibration_status(ClientTransactionID: int = Query(0)):
    """Reports whether telescope pointing is calibrated against a resolved plate solve."""
    status = {
        "is_calibrated": model.is_calibrated,
        "message": model.calibration_message,
        "recommended_action": "Use guide camera image to do a quick plate solve and sync after first slew."
    }
    return alpaca_response(value=status, client_tx_id=ClientTransactionID)


@app.get("/api/v1/telescope/0/safety")
def get_safety_limits(ClientTransactionID: int = Query(0)):
    """Returns currently active safety envelope boundaries."""
    limits = {
        "min_ha_deg": config.safety.min_ha_deg,
        "max_ha_deg": config.safety.max_ha_deg,
        "min_dec_deg": config.safety.min_dec_deg,
        "max_dec_deg": config.safety.max_dec_deg,
        "min_alt_deg": config.safety.min_alt_deg,
        "sun_avoidance_deg": config.safety.sun_avoidance_deg,
        "max_slew_speed": config.safety.max_slew_speed,
    }
    return alpaca_response(value=limits, client_tx_id=ClientTransactionID)


@app.put("/api/v1/telescope/0/safety")
async def update_safety_limits(
    request: Request,
    min_ha_deg: Optional[float] = Form(None),
    max_ha_deg: Optional[float] = Form(None),
    min_dec_deg: Optional[float] = Form(None),
    max_dec_deg: Optional[float] = Form(None),
    min_alt_deg: Optional[float] = Form(None),
    sun_avoidance_deg: Optional[float] = Form(None),
    max_slew_speed: Optional[int] = Form(None),
    ClientTransactionID: int = Form(0)
):
    """Dynamically updates safety envelopes and persists them to config."""
    try:
        body = await request.json()
    except Exception:
        body = {}

    def get_val(param_name, form_val):
        return form_val if form_val is not None else body.get(param_name)

    if (v := get_val("min_ha_deg", min_ha_deg)) is not None:
        config.safety.min_ha_deg = float(v)
    if (v := get_val("max_ha_deg", max_ha_deg)) is not None:
        config.safety.max_ha_deg = float(v)
    if (v := get_val("min_dec_deg", min_dec_deg)) is not None:
        config.safety.min_dec_deg = float(v)
    if (v := get_val("max_dec_deg", max_dec_deg)) is not None:
        config.safety.max_dec_deg = float(v)
    if (v := get_val("min_alt_deg", min_alt_deg)) is not None:
        config.safety.min_alt_deg = float(v)
    if (v := get_val("sun_avoidance_deg", sun_avoidance_deg)) is not None:
        config.safety.sun_avoidance_deg = float(v)
    if (v := get_val("max_slew_speed", max_slew_speed)) is not None:
        config.safety.max_slew_speed = int(v)

    save_config(config)
    logger.info("Updated safety limits from API.")
    return alpaca_response(value="Safety limits updated successfully", client_tx_id=ClientTransactionID)


def start_server():
    """Entry point for launching the Alpaca service."""
    uvicorn.run(app, host="0.0.0.0", port=config.alpaca_port, log_level="info")


if __name__ == "__main__":
    start_server()
