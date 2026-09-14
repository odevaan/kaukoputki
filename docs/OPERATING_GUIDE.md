# Telescope Operating & Safety Guide

This guide details the standard operating procedures, safety workflows, and software integration for the Jakokoski Observatory telescope mount.

---

## 1. Safety Architecture Notice

> [!WARNING]
> **No Electrical Limit or Homing Switches**:
> All physical limit and reference switches have been removed from the mount.
> The system relies strictly on:
> 1. **User manual park positioning** prior to driver boot.
> 2. **Software safety envelopes** enforced mathematically by the driver.
> 3. **The physical hardware Emergency Stop button** inline with motor power.

---

## 2. Startup Procedure

### Step 1: Physical Mount Positioning
Before turning on the motor power or launching the driver:
1. Manually release clutches and position the telescope pointing **directly South on the meridian** at **$0^\circ$ Declination** (between the horizon and celestial equator / ecliptic).
2. Lock both RA and Dec clutches firmly.

### Step 2: Power Up
1. Verify the physical Emergency Stop button is accessible and not depressed.
2. Power on the Jetter Nano-B controller and motor power supplies.

### Step 3: Launch the Driver Service
On Linux (or Windows):
```bash
# Activate virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Run with physical serial port
python run_driver.py --port /dev/ttyUSB0

# Or run in mock mode for testing without hardware
python run_driver.py --mock
```

Upon launch, the driver:
- Reads the system clock and computes the exact **Local Sidereal Time (LST)**.
- Initializes the mount coordinates to:
  - $\text{Hour Angle } HA = 0.0^\circ$
  - $\text{Declination } \delta = 0.0^\circ$
  - $\text{Right Ascension } RA = LST$
- Flags the mount status as **`is_calibrated: False`**.

---

## 3. Client Connection (N.I.N.A. & Stellarium)

### Connecting N.I.N.A.
1. Open N.I.N.A. $\to$ **Equipment** $\to$ **Telescope**.
2. Select **ASCOM Alpaca** as the driver source.
3. Click the gear icon or **Discover**. N.I.N.A. will automatically detect `Jakokoski Jetter Nano-B Equatorial Mount` via UDP discovery on port 32227.
4. Click **Connect**.

### Connecting Stellarium
1. Open Stellarium $\to$ **Configuration** $\to$ **Plugins** $\to$ **Telescope Control**.
2. Add a new telescope $\to$ Select **ASCOM Alpaca**.
3. Specify Host: `localhost` (or IP of driver machine), Port: `11111`, Device Number: `0`.
4. Connect.

---

## 4. Calibration & Plate Solve Workflow

> [!IMPORTANT]
> **First Slew & Plate Solve Routine**:
> Because homing switches are absent, the boot coordinate is only as accurate as manual visual alignment.
> **Standard Operating Practice**:
> 1. Issue an initial slew to a bright star or field near the meridian.
> 2. Take a quick exposure using the **guide camera** or main camera.
> 3. Trigger a plate solve (ASTAP / PlateSolve3) in N.I.N.A.
> 4. Issue a **Sync** (`SyncToCoordinates`) in N.I.N.A.
> 5. The driver automatically calculates the coordinate offset and transitions `is_calibrated` to `True`.

---

## 5. Adjusting Safety Limits

Safety limits can be adjusted to account for changes in attached equipment, cameras, or cable routing:

### Via Configuration File
Edit `app/config.json`:
```json
"safety": {
    "min_ha_deg": -220.0,
    "max_ha_deg": 220.0,
    "min_dec_deg": -50.0,
    "max_dec_deg": 90.0,
    "min_alt_deg": 0.0,
    "sun_avoidance_deg": 4.0,
    "max_slew_speed": 6000
}
```

### Via HTTP REST API
```bash
curl -X PUT http://localhost:11111/api/v1/telescope/0/safety \
     -H "Content-Type: application/json" \
     -d '{"min_dec_deg": -45.0, "max_dec_deg": 85.0}'
```

---

## 6. Emergency Stop Procedures

1. **Software Abort**:
   - In N.I.N.A.: Click the **Cancel Slew** button.
   - In API / Terminal:
     ```bash
     curl -X PUT http://localhost:11111/api/v1/telescope/0/abortslew
     ```
   - This instantly switches axes to speed mode with velocity = 0, silences the buzzer, and halts motion.
2. **Hardware E-Stop**:
   - Hit the physical red emergency stop button inline with motor DC power.
