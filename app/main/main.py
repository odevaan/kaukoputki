from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.utils.nanomex import Nanomex
from app.utils.pointing import get_horizontal_coords
from app.utils.catalogs import load_messier_catalog
from astropy.time import Time
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# Mount the static directory to serve files like index.html, css, js
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# --- Global State ---
# In a real app, this might be handled by a more robust state management system.
nanomex_controller = Nanomex(testing=True)
messier_catalog = []

# --- Lifespan Events ---
@app.on_event("startup")
def startup_event():
    """Load catalogs into memory on application startup."""
    global messier_catalog
    # This assumes the app is run from the project root.
    catalog_path = os.path.join("matlab_code", "messier.cat")
    messier_catalog = load_messier_catalog(catalog_path)
    if not messier_catalog:
        # Log this issue, but don't prevent startup
        print("WARNING: Messier catalog could not be loaded.")


class SlewRequest(BaseModel):
    ra: float
    dec: float

@app.get("/")
async def read_index():
    """Serves the main index.html file."""
    return FileResponse('app/static/index.html')

@app.get("/nanomex/get_reg/{address}")
def get_register(address: int):
    """
    API endpoint to read a register from the Nanomex controller.
    """
    try:
        value, status = nanomex_controller.get_reg(address)
        if status != 0:
            raise HTTPException(status_code=500, detail="Failed to communicate with Nanomex controller")
        return {"address": address, "value": value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/nanomex/set_reg/{address}")
def set_register(address: int, value: int):
    """
    API endpoint to write a register to the Nanomex controller.
    """
    try:
        _, status = nanomex_controller.set_reg(address, value)
        if status != 0:
            raise HTTPException(status_code=500, detail="Failed to communicate with Nanomex controller")
        return {"status": "success", "address": address, "value_set": value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/telescope/slew")
def slew_to_coords(req: SlewRequest):
    """
    Calculates pointing coordinates and simulates slewing the telescope.
    """
    try:
        # Hardcoded observatory and weather parameters for now
        lat, lon, alt = 62.727, 29.996, 155
        temp, pressure = -10.0, 1013.0

        now = Time.now()

        # Calculate the required Az/Alt for the target
        horizontal_coords = get_horizontal_coords(
            ra=req.ra, dec=req.dec,
            lat=lat, lon=lon, alt=alt,
            temp=temp, pressure=pressure,
            time=now
        )

        if not horizontal_coords:
            raise HTTPException(status_code=500, detail="Coordinate transformation failed.")

        az = horizontal_coords.az.deg
        alt = horizontal_coords.alt.deg

        # --- Simulation of telescope control ---
        # In a real implementation, this would involve a complex process:
        # 1. Convert Az/Alt to motor steps/encoder counts.
        # 2. Communicate with the Nanomex controller to start the slew.
        # 3. Monitor the slew's progress and confirm completion.
        # For now, we just log the action and use the Nanomex class to show the principle.

        # Example: Set a register to indicate slewing status
        nanomex_controller.set_reg(address=2000, value=1) # 2000 = "slewing_status_reg", 1 = "slewing"

        # Log the simulated action
        print(f"SIMULATING: Slewing telescope to Az={az:.4f}, Alt={alt:.4f}")

        # Example: Set target coordinates in controller's registers
        # (assuming registers 2001 and 2002 are for target Az/Alt)
        # Note: We would need to convert float degrees to a suitable integer format.
        nanomex_controller.set_reg(address=2001, value=int(az * 10000))
        nanomex_controller.set_reg(address=2002, value=int(alt * 10000))

        # Simulate end of slew
        nanomex_controller.set_reg(address=2000, value=0) # 0 = "idle"

        return {
            "message": "Slew command sent successfully.",
            "target_ra_dec": {"ra": req.ra, "dec": req.dec},
            "calculated_alt_az": {"alt": alt, "az": az}
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Catalog Endpoints ---

@app.get("/catalog/messier")
def get_messier_catalog():
    """Returns the entire Messier catalog."""
    return messier_catalog

@app.get("/catalog/messier/{m_num}")
def get_messier_object(m_num: int):
    """Returns a single object from the Messier catalog."""
    obj = next((item for item in messier_catalog if item["m_num"] == m_num), None)
    if not obj:
        raise HTTPException(status_code=404, detail=f"Messier object M{m_num} not found.")
    return obj
