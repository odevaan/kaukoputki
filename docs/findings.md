# Reverse Engineering Findings & Technical Documentation

This document records all reverse-engineering discoveries, technical parameters, and architectural findings extracted from the legacy MATLAB telescope control system (running on Windows 98) and the Jetter Nano-B motion controller for the Jakokoski Observatory.

---

## 1. System History & Context
- **Observatory Location**: Jakokoski, Finland
  - Latitude: $62^\circ 43' 38''\text{ N}$ ($62.727222^\circ$)
  - Longitude: $29^\circ 59' 48''\text{ E}$ (legacy code notation: `-29°59'48"` West-negative)
  - Elevation: 155 m
  - Nominal Weather: 1013 mbar, $-10^\circ\text{C}$
- **Legacy Authors**:
  - Original motion DLL interface (`nanomex.dll` / `nanocom`): Dr. Jari Räsänen (2000)
  - Original MATLAB control: FM Marjut Ristola (2000)
  - Upgraded TPoint modeling & calibration: Dr. Pertti Pääkkönen (2001–2003)
- **Mount Configuration**: Custom Equatorial (EQ) mount driven by DC servo motors with optical encoders.
- **Sensors & Switches Status**:
  - All physical limit switches and reference/homing optocoupler switches have been removed.
  - A physical, manual hardware Emergency Stop button remains in place inline with motor DC power.
  - Software must enforce all motion envelopes and safety limits.

---

## 2. Serial Communication & Jetter Nano-B Interface

### 2.1 Hardware Interface & Pinout
- **Port**: RS-232 (Sub-D 9-pin female connector on controller).
  - On Linux: Typically `/dev/ttyUSB0` (USB-RS232 adapter) or `/dev/ttyS0` (onboard COM port).
  - On Legacy Windows 98: `COM1`.
- **Cable Specification (Jetter EM-PK Cable)**:
  - Jetter Pin 2 (TXD) $\to$ Host Pin 2 (RXD)
  - Jetter Pin 3 (RXD) $\to$ Host Pin 3 (TXD)
  - Jetter Pin 7 (GND) $\to$ Host Pin 5 (GND)
  - Pins 7 & 8 (RTS/CTS) and 1, 4, 6 (DCD, DTR, DSR) were short-circuited on the PC connector for passive loopback handshake.
  - **Flow Control**: None (3-wire connection).
- **Serial Framing**:
  - Baud Rate: **9600 baud** (Nano-B default register `2823 = 6`). Range 150 to 19200 baud.
  - Data Bits: **8**
  - Parity: **None** (or Even Parity in some Jetter configurations)
  - Stop Bits: **1**
  - Handshake: **None** (hardware loopback)
  - Default Timeout: 4000 ms (`JET32_SERIAL_DEFAULT_TIMEOUT`)

### 2.2 Jetter Register Architecture
The Jetter Nano-B controller uses dedicated register blocks for intelligent servo modules:
- **Axis 2: Declination ($\delta$)**
  - Register range: `12100` .. `12199`
  - `12100`: Axis Control and Status
    - Bit 9 = 1: Position Control Mode (point-to-point motion).
    - Bit 9 = 0: Speed Control Mode (velocity/tracking mode).
    - Bit 1: In-position / target reached flag (1 = target reached, 0 = in motion).
  - `12101`: Axis Direction / Motion Command (9 = positive, 10 = negative).
  - `12102`: Target / Nominal Position (`destep`, signed 32-bit).
  - `12103`: Slewing Speed (`speed = 6000`, reference speed = `2000`).
  - `12104`: Limit / Reference Sensor configuration (Bit 0 = active level).
  - `12109`: Actual Encoder Position (`destep`, signed 32-bit).
  - `12122`: Motor Resolution Prescaler (`32` for 512 steps/rev to avoid register overflow).
- **Axis 3: Right Ascension / Hour Angle ($HA$)**
  - Register range: `13100` .. `13199`
  - `13100`: Axis Control and Status (Bit 9 = Position/Speed mode, Bit 1 = In-position).
  - `13101`: Axis Direction / Motion Command (9 = positive, 10 = negative).
  - `13102`: Target / Nominal Position (`hastep`, signed 32-bit).
  - `13103`: Slewing Speed (`speed = 6000`, reference speed = `2000`).
  - `13104`: Limit / Reference Sensor configuration.
  - `13109`: Actual Encoder Position (`hastep`, signed 32-bit).
  - `13122`: Motor Resolution Prescaler (`32` for 512 steps/rev).
- **Digital Outputs**:
  - Output `101`: Movement warning buzzer (`SetOutput(101, 1)` to sound during slew, `0` to silence).

---

## 3. Kinematics, Gear Ratios & Tracking Calculations

### 3.1 Gearing & Resolution
- RA Axis Reduction Ratio: $M_{RA} = 18800 : 1$
- Dec Axis Reduction Ratio: $M_{DE} = 14100 : 1$
- Motor Encoder Counts per Revolution: $N_{step} = 512$
- **Total Counts per Mount Revolution (360°)**:
  - RA Axis: $18800 \times 512 = 9,625,600\text{ steps}$
    - Scale: $26,737.778\text{ steps/degree} \approx 7.42716\text{ steps/arcsec}$
  - Dec Axis: $14100 \times 512 = 7,219,200\text{ steps}$
    - Scale: $20,053.333\text{ steps/degree} \approx 5.57037\text{ steps/arcsec}$

### 3.2 Coordinate to Step Conversion
Extracted from `telpos.m` and `movetel.m`:
$$\text{hastep} = \text{round}\left(\frac{M_{RA} \cdot N_{step} \cdot HA}{2\pi}\right)$$
$$\text{destep} = -\text{round}\left(\frac{M_{DE} \cdot N_{step} \cdot \delta}{2\pi}\right)$$
> **Critical Sign Convention**: Notice the negative sign in the Declination axis (`destep = -round(...)`).

### 3.3 Sidereal Tracking Rate
- Earth sidereal rotation period: $T_{sid} \approx 86,164.0905\text{ s}$
- Sidereal angular velocity: $\omega_{sid} \approx 7.292115 \times 10^{-5}\text{ rad/s} \approx 15.041067''/\text{s}$
- Sidereal step rate:
  $$\text{Rate}_{RA} = \frac{9,625,600\text{ steps}}{86,164.0905\text{ s}} \approx 111.7122\text{ steps/second}$$
- In the legacy `movetel.m`, real-time time-dependent tracking was injected into the target position register:
  $$\Delta \text{hastep} = \text{round}\left(\frac{M_{RA} \cdot N_{step} \cdot 1.0027378 \cdot \Delta t \cdot 2\pi / 86400}{2\pi}\right)$$

### 3.4 Slew Speed & Timing
- Slewing speed: `speed = 6000` steps/second
  - In RA: $\frac{6000}{26737.78} \approx 0.224^\circ/\text{s} = 13.46^\circ/\text{min}$
  - In Dec: $\frac{6000}{20053.33} \approx 0.299^\circ/\text{s} = 17.95^\circ/\text{min}$
- Reference speed: `SiirtoV1 = 2000` steps/second ($\approx 4.5^\circ - 6.0^\circ/\text{min}$)

---

## 4. Safety Envelopes & Limits
Because electrical switches were removed, all limits are checked in software before initiating any motion:
1. **Hour Angle Limits**:
   - Software limit: $HA \in [-220^\circ, +220^\circ]$ (configurable, defaults from `kaukoputki.cfg`)
2. **Declination Limits**:
   - Software limit: $\delta \in [-50^\circ, +90^\circ]$ (from `kohdista.m`)
3. **Horizon Safety**:
   - Altitude $> 0^\circ$ (do not slew into the ground)
4. **Solar Protection**:
   - Angular separation from the Sun must exceed $4.0^\circ$ ($0.07$ rad)
5. **Emergency Halt**:
   - Immediately switch axes out of Position Control Mode (`SetBit(axis, 0, 9)`), write speed = 0, turn off buzzer (`SetOutput(101, 0)`).

---

## 5. Mount Parking & Calibration Philosophy
- **Park Position**: Pointing South on the meridian ($HA = 0^\circ, \delta = 0^\circ$).
- **Boot Assumption**: When the driver service is started, the mount is assumed to be in this physical park position.
- **Initial Calibration Status**:
  - The driver flags `is_calibrated = False` on boot.
  - The user is notified that the mount is uncalibrated.
  - A quick plate solve (e.g. from the guide camera or main camera via ASTAP/PlateSolve3 in N.I.N.A.) should be performed after the first slew to resolve the true sky position and issue a `SyncToCoordinates` command to calibrate the pointing model.
