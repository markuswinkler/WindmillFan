"""Constants for Windmill Fan."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "WindmillFan"
DOMAIN = "windmillfan"
VERSION = "1.0.5"
PLATFORMS = ["fan"]
UPDATE_INTERVAL = 60
CONF_TOKEN = "token"
BASE_URL = "https://dashboard.windmillair.com"

# HTTP Configuration
HTTP_TIMEOUT = 30
MAX_RETRIES = 3

# Fan speed mappings
FAN_SPEED_MAPPING = {
    "Whisper": "1",
    "Low": "2", 
    "Medium": "3",
    "High": "4",
    "Boost": "5"
}

FAN_SPEED_REVERSE_MAPPING = {v: k for k, v in FAN_SPEED_MAPPING.items()}

POWER_MAPPING = {
    False: 0,
    True: 1
}

# Pin mappings
PIN_POWER = "V0"
PIN_FAN_SPEED = "V2"

# Default values
DEFAULT_FAN_SPEED = "Medium"
DEFAULT_TIMEOUT = 10
