"""Constants"""
# Base component constants
NAME = "Ferroamp Portal"
MANUFACTURER = "Ferroamp"
DOMAIN = "ferroamp_portal"
DOMAIN_DATA = f"{DOMAIN}_data"
ATTRIBUTION = "Data provided by Ferroamp Portal"
ISSUE_URL = "https://github.com/bj00rn/ha-ferroamp-portal/issues"
# Icons
ICON = "mdi:format-quote-close"

# Platforms
SENSOR = "sensor"
SWITCH = "switch"
CLIMATE = "climate"
PLATFORMS = [SENSOR]


# Configuration and options
CONF_ENABLED = "enabled"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SYSTEM_ID = "system_id"

# Defaults
DEFAULT_NAME = DOMAIN

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME} %s
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
