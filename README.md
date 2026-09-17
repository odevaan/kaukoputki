# Jakokoski Telescope Control (Kaukoputki)

Cross-platform ASCOM Alpaca telescope control driver for the Jakokoski Observatory equatorial mount driven by a Jetter Nano-B motion controller over RS-232 serial. Compatible with N.I.N.A., Stellarium, and other ASCOM Alpaca clients.

---

## Quick Start on Linux

### 1. Prerequisites & Serial Permissions
```bash
# Install system packages (Debian/Ubuntu/Raspberry Pi OS)
sudo apt update
sudo apt install -y python3 python3-venv python3-pip

# Add user to dialout group for serial port (/dev/ttyUSB0) access
sudo usermod -aG dialout $USER
# Log out and back in (or run 'newgrp dialout') for changes to take effect
```

### 2. Create Virtual Environment & Install Dependencies
```bash
# Clone the repository and enter directory
cd kaukoputki

# Create the virtual environment (.venv)
python3 -m venv .venv

# Activate and install Python dependencies
source .venv/bin/activate
pip install --upgrade pip
pip install -r app/requirements.txt
```

### 3. Run the Driver
```bash
# Activate virtual environment
source .venv/bin/activate

# Run connected to physical Jetter Nano-B (adjust serial port as needed)
python run_driver.py --port /dev/ttyUSB0

# Or run in mock simulation mode (no hardware required)
python run_driver.py --mock
```

---

## Quick Start on Windows
```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r app/requirements.txt
python run_driver.py --port COM1
```

---

## Documentation
- [KStars & Ekos Connection Guide](docs/KSTARS_EKOS_SETUP.md) - Connecting and plate-solving with KStars / Ekos via INDI on Linux.
- [Operating Guide](docs/OPERATING_GUIDE.md) - Standard operating procedures, N.I.N.A./Stellarium integration, plate-solve calibration, and systemd service setup.
- [Architecture](docs/ARCHITECTURE.md) - Software architecture, components, and Alpaca V3 endpoints.
- [Findings & Reverse Engineering](docs/findings.md) - Extracted MATLAB control parameters, Jetter Nano-B registers, gear ratios, and safety envelopes.
