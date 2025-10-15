"""
Configuration and Constants
"""
import os

# Page Configuration
PAGE_CONFIG = {
    "page_title": "Cycle Time Recorder",
    "layout": "wide"
}

# File Paths
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
DATA_FILE = os.path.join(DATA_DIR, "cycle_time_records.json")
AUDIT_FILE = os.path.join(DATA_DIR, "audit_log.json")

# Default Admin Credentials
DEFAULT_ADMIN = ("admin", "admin123")

# Application Limits
MAX_ROWS = 20
MAX_LOGIN_ATTEMPTS = 5
LOGIN_TIMEOUT = 300  # 5 minutes
PASSWORD_MIN_LENGTH = 8

# Logging
LOG_LEVEL = "INFO"