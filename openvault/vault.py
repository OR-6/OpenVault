# openvault/vault.py
import os
import json
import uuid
import datetime
from typing import Optional, Dict, Any
from openvault import config, encryption, utils

class Vault:
    """Represents a single vault file and operations on it."""
    def __init__(self, vault_name: Optional[str] = None):
        os.makedirs(config.CONFIG_DIR, exist_ok=True)
        os.makedirs(config.VAULTS_DIR, exist_ok=True)
        os.makedirs(config.LOCKER_DIR, exist_ok=True)
        os.makedirs(config.TEMP_DIR, exist_ok=True)
        os.makedirs(config.BACKUPS_DIR, exist_ok=True)

        self.vault_name = vault_name
        self.path = config.VAULT_FILE_TEMPLATE.format(name=vault_name) if vault_name else None
        self.master_password: Optional[str] = None
        self.salt: Optional[bytes] = None
        self.vault_data: Optional[Dict[str, Any]] = None

    @staticmethod
    def new_structure() -> Dict[str, Any]:
        return {
            "passwords": {},
            "twofa": {},
            "notes": {},
            "files": {},
            "categories": ["Personal", "Work", "Financial", "Social"]
        }

    def create_new(self, master_password: str):
        """Initialize a new vault file for this vault_name."""
        if not self.vault_name:
            raise ValueError("Vault name must be set to create a file.")
        self.path = config.VAULT_FILE_TEMPLATE.format(name=self.vault_name)
        self.master_password = master_password
        self.salt = os.urandom(encryption.SALT_SIZE)
        self.vault_data = Vault.new_structure()
        return self.save()

    def save(self) -> bool:
        if not self.master_password or not self.path:
            return False
        try:
            encrypted, salt = encryption.VaultEncryption.encrypt_data(self.vault_data, self.master_password, self.salt)
            with open(self.path, "wb") as f:
                f.write(salt)
                f.write(encrypted)
            return True
        except Exception:
            return False

    def load(self, password: str) -> bool:
        """Load vault from file using password."""
        if not self.path or not os.path.exists(self.path):
            return False
        try:
            with open(self.path, "rb") as f:
                salt = f.read(encryption.SALT_SIZE)
                encrypted = f.read()
            data = encryption.VaultEncryption.decrypt_data(encrypted, password, salt)
            if data is None:
                return False
            self.master_password = password
            self.salt = salt
            self.vault_data = data
            return True
        except Exception:
            return False

    def backup_to(self, dest_path: str) -> bool:
        """Save a full encrypted backup file (copy of vault file + metadata)."""
        if not self.path or not os.path.exists(self.path):
            return False
        try:
            import shutil
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(self.path, dest_path)
            return True
        except Exception:
            return False

    def restore_from(self, backup_path: str) -> bool:
        """Replace current vault file with a backup file (user must supply password on load)."""
        if not self.path:
            return False
        try:
            import shutil
            shutil.copy2(backup_path, self.path)
            return True
        except Exception:
            return False


    def get_password_entry(self, entry_id: str):
        return self.vault_data["passwords"].get(entry_id)
