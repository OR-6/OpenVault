# openvault/updater.py
import os
import requests
import zipfile
import io
import shutil
from openvault import config, ui, utils
from typing import Optional

def check_latest_release() -> Optional[dict]:
    """Return release dict from GitHub API or None on failure."""
    try:
        url = f"https://api.github.com/repos/{config.GITHUB_REPO}/releases/latest"
        resp = requests.get(url, timeout=10, headers={"Accept":"application/vnd.github.v3+json"})
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

def is_newer_version(current: str, latest_tag: str) -> bool:
    
    def norm(v): return v.lstrip('v').split('.')
    try:
        cur = [int(x) for x in norm(current)]
        lat = [int(x) for x in norm(latest_tag)]
        return lat > cur
    except Exception:
        return current != latest_tag

def perform_auto_update(dest_dir: str, release: dict) -> bool:
    """Download release zipball and extract to temp then copy over dest_dir.
       Returns True if files were written successfully (user should restart)."""
    try:
        zip_url = release.get("zipball_url")
        if not zip_url:
            return False
        r = requests.get(zip_url, timeout=30, stream=True)
        if r.status_code != 200:
            return False
        data = io.BytesIO(r.content)
        with zipfile.ZipFile(data) as z:
            
            tmp = os.path.join(config.TEMP_DIR, "openvault_update")
            if os.path.exists(tmp):
                shutil.rmtree(tmp)
            os.makedirs(tmp, exist_ok=True)
            z.extractall(tmp)
            
            entries = os.listdir(tmp)
            if not entries:
                return False
            top = os.path.join(tmp, entries[0])
            
            for root, dirs, files in os.walk(top):
                rel = os.path.relpath(root, top)
                dest_root = os.path.join(dest_dir, rel) if rel != "." else dest_dir
                os.makedirs(dest_root, exist_ok=True)
                for f in files:
                    src_file = os.path.join(root, f)
                    dst_file = os.path.join(dest_root, f)
                    shutil.copy2(src_file, dst_file)
        return True
    except Exception:
        return False

def run_update_check(dest_dir: str, cfg: dict, auto_apply: bool = True):
    """Check for updates and optionally apply them. Returns (checked, applied, message)."""
    release = check_latest_release()
    if not release:
        return False, False, "Unable to fetch release info"
    latest_tag = release.get("tag_name") or release.get("name")
    if not latest_tag:
        return False, False, "No release tag found"
    if not is_newer_version(config.APP_VERSION, latest_tag):
        return True, False, "Already up-to-date"
    
    if not auto_apply:
        return True, False, f"Update available: {latest_tag}"
    
    success = perform_auto_update(dest_dir, release)
    if success:
        cfg['last_update_check'] = latest_tag
        utils.save_config(cfg)
        return True, True, f"Updated to {latest_tag} (restart required)"
    return True, False, "Update download/apply failed"
