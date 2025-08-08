"""Constants for the Finance Assistant integration."""

DOMAIN = "finance_assistant"

# Configuration keys
CONF_HOST = "host"
CONF_PORT = "port"
CONF_API_KEY = "api_key"
CONF_SSL = "ssl"
CONF_SCAN_INTERVAL = "scan_interval"

# Defaults
DEFAULT_SCAN_INTERVAL = 300  # 5 minutes
DEFAULT_PORT = 8080

# API endpoints
API_ENDPOINT_QUERIES = "/api/ha/queries/"
API_ENDPOINT_SENSOR = "/api/ha/sensor/{query_id}/"
API_ENDPOINT_CALENDAR = "/api/ha/calendar/{query_id}/"

# Entity attributes
ATTR_QUERY_ID = "query_id"
ATTR_QUERY_NAME = "query_name"
ATTR_QUERY_DESCRIPTION = "query_description"
ATTR_LAST_UPDATED = "last_updated"
ATTR_DATA_SOURCE = "data_source"
ATTR_QUERY_TYPE = "query_type"

# Device info
DEVICE_INFO = {
    "identifiers": {(DOMAIN, "finance_assistant")},
    "name": "Finance Assistant",
    "manufacturer": "Finance Assistant",
    "model": "Finance Assistant",
                    "sw_version": "1.0.19",
} 