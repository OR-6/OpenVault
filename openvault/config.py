# openvault/config.py
import os

APP_NAME = "OpenVault"
APP_VERSION = "1.0.0"
GITHUB_REPO = "OR-6/OpenVault"  # used by updater: "owner/repo"

# directories
CONFIG_DIR = os.path.expanduser("~/.openvault")
VAULTS_DIR = os.path.join(CONFIG_DIR, "vaults")
VAULT_FILE_TEMPLATE = os.path.join(VAULTS_DIR, "{name}.enc")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
LOCKER_DIR = os.path.join(CONFIG_DIR, "locker")
TEMP_DIR = os.path.join(CONFIG_DIR, "temp")
BACKUPS_DIR = os.path.join(CONFIG_DIR, "backups")

# defaults
DEFAULT_TIMEOUT = 300  # seconds to auto-lock
DEFAULT_CLIP_CLEAR = 15
DEFAULT_CONFIG = {
    "active_vault": None,
    "vaults": {},  # name -> metadata dict {display_name, path}
    "auto_lock_timeout": DEFAULT_TIMEOUT,
    "clipboard_clear_time": DEFAULT_CLIP_CLEAR,
    "auto_update": True,
    "default_backup_path": "",  # user can set
    "last_update_check": None
}
