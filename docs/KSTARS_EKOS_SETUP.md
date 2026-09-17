# KStars & Ekos Connection Guide for Linux

This guide explains how to connect and operate the **Kaukoputki Jetter Nano-B Telescope Driver** using **KStars and Ekos** on Linux (Ubuntu, Debian, Raspberry Pi OS, Astroberry, or StellarMate).

The driver supports two connection methods for Linux:
1. **Method 1 (Recommended & Instant)**: Connect via **Meade LX200 Generic** over TCP (`localhost:4030`). This driver is **pre-installed by default in 100% of KStars/Ekos installations**. No PPAs or extra packages are needed!
2. **Method 2**: Connect via the **INDI Alpaca Telescope Bridge** over HTTP (`localhost:11111`) using the official INDI PPA.

---

## Method 1: Direct Connection via LX200 Generic (No extra packages needed!)

The Kaukoputki driver service includes a built-in Meade LX200 network server on TCP port `4030`. Every KStars/Ekos installation already comes with the `indi_lx200generic` driver pre-installed.

### Step 1: Start the Kaukoputki Driver
```bash
cd ~/kaukoputki
source .venv/bin/activate

# Launch with your serial port (or --mock for simulation)
python run_driver.py --port /dev/ttyUSB0
```
The driver will log:
`LX200 TCP server running on 0.0.0.0:4030 (KStars/Ekos compatible)`

### Step 2: Configure Ekos Equipment Profile
1. In KStars, press `Ctrl + K` to open **Ekos**.
2. Click **+** to add or edit your Equipment Profile:
   - **Profile Name**: `Jakokoski Observatory`
   - Under **Mount**: Select **Meade $\to$ LX200 Generic** (or filter `LX200 Generic`).
   - Under **CCD / Guider**: Select your imaging and guide cameras (or CCD Simulator).
3. Click **Save**.

### Step 3: Set Connection Port in Ekos
1. Select the profile and click **Start INDI**.
2. In the **INDI Control Panel** that opens, switch to the **LX200 Generic** tab.
3. Open the **Connection** tab:
   - Connection Mode: Select **Network** (TCP) instead of Serial.
   - **Server Host / IP**: `127.0.0.1` (or the IP of the Linux driver machine).
   - **Port**: `4030`.
   - Click **Save**.
4. Click **Connect**:
   - The status turns green!
   - The telescope crosshairs will appear on the KStars map at the South park position.
   - Slew, sync (plate solve), park, unpark, and guiding are fully functional.

---

## Method 2: Connecting via INDI Alpaca Bridge (`indi_alpaca_telescope`)

If you prefer using the ASCOM Alpaca bridge in Ekos, the `indi-full` package containing `indi_alpaca_telescope` must be installed from the official INDI PPA.

### Why `Unable to locate package indi-full` happens:
Standard Ubuntu/Debian repositories do not include the `indi-full` metapackage. It is hosted exclusively in the **INDI Library PPA** maintained by the INDI developers.

### Installation Steps (Ubuntu / Linux Mint):
```bash
# 1. Add the official INDI PPA
sudo add-apt-repository -y ppa:mutlaqja/ppa

# 2. Update package cache
sudo apt update

# 3. Install the full driver suite
sudo apt install -y indi-full indi-bin

# 4. Verify the Alpaca driver binary is present
which indi_alpaca_telescope
# (Output should be: /usr/bin/indi_alpaca_telescope)
```

### Configure in Ekos:
1. **Restart KStars** so it re-reads `/usr/share/indi/drivers.xml`.
2. Open Ekos (`Ctrl + K`) $\to$ edit profile.
3. Under **Mount**:
   - Expand the **Alpaca** manufacturer $\to$ select **Alpaca Telescope**.
4. Start INDI $\to$ In the **Alpaca Telescope** tab:
   - Set **Host**: `127.0.0.1`
   - Set **Port**: `11111`
   - Set **Device Number**: `0`
5. Click **Connect**.

---

## Slew & Plate-Solve Alignment Routine in Ekos

Because physical homing switches have been removed from the mount, the telescope boots in an uncalibrated park state ($HA = 0^\circ, \delta = 0^\circ$).

1. **Unpark**: In the Ekos **Mount** tab, click **Unpark**.
2. **Slew**: Right-click a bright star near the meridian in KStars $\to$ select **Telescope $\to$ Slew**.
3. **Plate Solve**:
   - Switch to the Ekos **Align** module (target icon).
   - Select **Action: Sync** (or **Slew to Target**).
   - Click **Capture & Solve**.
   - Ekos captures an image using your camera, solves the field with StellarSolver / ASTAP, and sends a `Sync` command to the mount.
   - The Kaukoputki driver updates internal offsets and marks `is_calibrated = True`!
4. **Guiding**:
   - In the Ekos **Guide** module, choose **Guide Via: Mount**. Pulse guiding corrections are handled automatically.
