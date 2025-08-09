# openvault/config.py
import os

APP_NAME = "OpenVault"
APP_VERSION = "1.0.0"

CONFIG_DIR = os.path.expanduser("~/.openvault")
VAULT_FILE = os.path.join(CONFIG_DIR, "vault.enc")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
LOCKER_DIR = os.path.join(CONFIG_DIR, "locker")
TEMP_DIR = os.path.join(CONFIG_DIR, "temp")

DEFAULT_TIMEOUT = 300
DEFAULT_CONFIG = {
    "auto_lock_timeout": DEFAULT_TIMEOUT,
    "theme": "default",
    "clipboard_clear_time": 15,
    "last_access": None
}
