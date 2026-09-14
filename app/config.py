import json
import os
from dataclasses import asdict, dataclass, field
from typing import Optional
import logging

logger = logging.getLogger(__name__)

CONFIG_PATH = os.environ.get("KAUKOPUTKI_CONFIG", os.path.join(os.path.dirname(__file__), "config.json"))

@dataclass
class SafetyLimits:
    min_ha_deg: float = -220.0
    max_ha_deg: float = 220.0
    min_dec_deg: float = -50.0
    max_dec_deg: float = 90.0
    min_alt_deg: float = 0.0
    sun_avoidance_deg: float = 4.0
    max_slew_speed: int = 6000

@dataclass
class ObservatoryConfig:
    name: str = "Jakokoski Observatory"
    latitude_deg: float = 62.727222  # 62°43'38" N
    longitude_deg: float = 29.996667 # 29°59'48" E (East positive)
    elevation_m: float = 155.0
    temperature_c: float = -10.0
    pressure_hpa: float = 1013.0

@dataclass
class SerialConfig:
    port: str = "/dev/ttyUSB0" if os.name != 'nt' else "COM1"
    baudrate: int = 9600
    timeout_sec: float = 2.0
    mock_mode: bool = False

@dataclass
class MountKinematics:
    m_ra: float = 18800.0   # RA gear ratio
    m_de: float = 14100.0   # Dec gear ratio
    n_step: float = 512.0   # Encoder counts / motor shaft rev
    park_ha_deg: float = 0.0    # Meridian pointing South
    park_dec_deg: float = 0.0   # Celestial Equator (exact 0.0 deg)

    @property
    def ra_steps_per_rev(self) -> float:
        return self.m_ra * self.n_step  # 9,625,600

    @property
    def dec_steps_per_rev(self) -> float:
        return self.m_de * self.n_step  # 7,219,200

    @property
    def ra_steps_per_deg(self) -> float:
        return self.ra_steps_per_rev / 360.0

    @property
    def dec_steps_per_deg(self) -> float:
        return self.dec_steps_per_rev / 360.0

    @property
    def sidereal_steps_per_sec(self) -> float:
        # 1 sidereal day = 86164.0905 SI seconds
        return self.ra_steps_per_rev / 86164.0905382

@dataclass
class PointingModel:
    # TPoint parameters in radians (loaded from legacy calibration)
    ih: float = -0.02978904
    id: float = 0.02517092
    ma: float = 0.00289460
    me: float = -0.00086716
    ch: float = -0.00006161
    np: float = -0.00028962
    tf: float = -0.00006670
    ff: float = 0.0
    df: float = -0.00059630
    enabled: bool = True

@dataclass
class DriverConfig:
    observatory: ObservatoryConfig = field(default_factory=ObservatoryConfig)
    serial: SerialConfig = field(default_factory=SerialConfig)
    safety: SafetyLimits = field(default_factory=SafetyLimits)
    kinematics: MountKinematics = field(default_factory=MountKinematics)
    pointing: PointingModel = field(default_factory=PointingModel)
    alpaca_port: int = 11111
    enable_discovery: bool = True

def load_config(file_path: Optional[str] = None) -> DriverConfig:
    path = file_path or CONFIG_PATH
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            config = DriverConfig(
                observatory=ObservatoryConfig(**data.get("observatory", {})),
                serial=SerialConfig(**data.get("serial", {})),
                safety=SafetyLimits(**data.get("safety", {})),
                kinematics=MountKinematics(**data.get("kinematics", {})),
                pointing=PointingModel(**data.get("pointing", {})),
                alpaca_port=data.get("alpaca_port", 11111),
                enable_discovery=data.get("enable_discovery", True),
            )
            logger.info(f"Loaded configuration from {path}")
            return config
        except Exception as e:
            logger.warning(f"Failed to parse config file {path}: {e}. Using defaults.")
    
    config = DriverConfig()
    save_config(config, path)
    return config

def save_config(config: DriverConfig, file_path: Optional[str] = None) -> None:
    path = file_path or CONFIG_PATH
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(config), f, indent=4)
        logger.info(f"Saved configuration to {path}")
    except Exception as e:
        logger.error(f"Failed to save configuration to {path}: {e}")
