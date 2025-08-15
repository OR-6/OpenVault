# openvault/utils.py
import datetime
import hashlib
import threading
from typing import Optional, Callable, Dict, Any
import json
import os
from . import config

def format_timestamp(ts: str) -> str:
    try:
        dt = datetime.datetime.fromisoformat(ts)
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ts

def format_size(size: int) -> str:
    units = ['B','KB','MB','GB','TB']
    s = float(size)
    for u in units:
        if s < 1024 or u == units[-1]:
            return f"{s:.2f} {u}"
        s /= 1024.0
    return f"{s:.2f} PB"


ALGO_MAP = {
    "SHA1": hashlib.sha1,
    "SHA256": hashlib.sha256,
    "SHA512": hashlib.sha512
}

class ClipboardManager:
    def __init__(self, clear_seconds: int = 15, on_cleared: Optional[Callable] = None):
        self._timer: Optional[threading.Timer] = None
        self.clear_seconds = clear_seconds
        self.on_cleared = on_cleared

    def schedule_clear(self):
        if self._timer:
            self._timer.cancel()
        self._timer = threading.Timer(self.clear_seconds, self.clear)
        self._timer.daemon = True
        self._timer.start()

    def clear(self):
        try:
            import pyperclip
            pyperclip.copy("")
            if self.on_cleared:
                self.on_cleared()
        except Exception:
            pass

def load_config() -> Dict[str, Any]:
    os.makedirs(config.CONFIG_DIR, exist_ok=True)
    if not os.path.exists(config.CONFIG_FILE):
        cfg = config.DEFAULT_CONFIG.copy()
        save_config(cfg)
        return cfg
    try:
        with open(config.CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        cfg = config.DEFAULT_CONFIG.copy()
        save_config(cfg)
        return cfg

def save_config(cfg: Dict[str, Any]) -> None:
    os.makedirs(config.CONFIG_DIR, exist_ok=True)
    with open(config.CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)
