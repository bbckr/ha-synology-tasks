"""Constants for the Synology Tasks integration."""

from typing import Final

DOMAIN: Final = "synology_tasks"
PLATFORMS: Final = ["sensor", "button"]

# Configuration
CONF_COORDINATOR = "coordinator"

# Services
SERVICE_RUN_TASK = "run_task"

# API
API_LOGIN = "SYNO.API.Auth"
API_METHOD_LOGIN = "login"
API_VERSION_LOGIN = "7"
API_TASK_SCHEDULER = "SYNO.Core.TaskScheduler"
API_VERSION_TASK_SCHEDULER = "3"
API_METHOD_TASK_SCHEDULER = "list"
API_EVENT_SCHEDULER = "SYNO.Core.EventScheduler"
API_METHOD_EVENT_SCHEDULER = "run"
API_VERSION_EVENT_SCHEDULER = "1"

# Attributes
ATTR_TASK_ID = "task_id"
ATTR_TASK_NAME = "task_name"
ATTR_TASK_TYPE = "task_type"
ATTR_TASK_OWNER = "task_owner"
ATTR_TASK_ENABLED = "task_enabled"
ATTR_NEXT_RUN_TIME = "next_run_time"
ATTR_CAN_RUN = "can_run"

# Entity key patterns
KEY_STATUS = "status"
KEY_RUN = "run_task"

# API Query Parameters
API_SORT_BY_NAME = "name"
API_SORT_DIRECTION_ASC = "asc"
API_TASK_LIMIT = "50"
API_TASK_OFFSET = "0"

# API Request Keys
API_ENABLE_SYNO_TOKEN = "enable_syno_token"
API_SYNO_TOKEN = "SynoToken"

# Data Keys
DATA_KEY = "data"
DATA_TASKS_KEY = "tasks"
DATA_SID_KEY = "sid"
DATA_SYNOTOKEN_KEY = "synotoken"
DATA_SUCCESS_KEY = "success"
DATA_ERROR_KEY = "error"
DATA_CODE_KEY = "code"

# Config Flow Keys
CONFIG_DSM_ENTRY_ID = "dsm_entry_id"
CONFIG_DEVICE_IDENTIFIERS = "device_identifiers"
CONFIG_DEVICE_NAME = "device_name"
CONFIG_DEVICE_MANUFACTURER = "device_manufacturer"
CONFIG_DEVICE_MODEL = "device_model"
CONFIG_DEVICE_SW_VERSION = "device_sw_version"

# Config Flow Step and Reason Constants
STEP_USER = "user"
REASON_NO_DSM_INSTANCES = "no_dsm_instances"
REASON_UNKNOWN = "unknown"
REASON_INVALID_DSM_ENTRY = "invalid_dsm_entry"

# Service Data Keys
SERVICE_DATA_TASK_NAME = "task_name"

# API Response Values
API_YES = "yes"
API_UNKNOWN = "Unknown"
# DSM returns 119 when the session (SID) is invalid or expired
API_ERROR_CODE_INVALID_SESSION: Final = 119

# API Endpoint
API_WEBAPI_ENDPOINT = "/webapi/entry.cgi"

# Protocols
PROTOCOL_HTTPS = "https"
PROTOCOL_HTTP = "http"

# Entity State Values
STATE_ENABLED = "enabled"
STATE_DISABLED = "disabled"

# Translation Keys
TRANSLATION_KEY_TASK_STATUS = "task_status"
TRANSLATION_KEY_TASK_RUN = "task_run"

# Default values
DEFAULT_SCAN_INTERVAL = 60  # seconds

# Notifications
NOTIFICATION_TITLE = "Synology Tasks"
NOTIFICATION_ID_TASK_RUN = "synology_tasks_run_{task_id}"
