# openvault/vault.py
import os
import json
import uuid
import datetime
from typing import Optional
from openvault import config, encryption

class Vault:
    def __init__(self):
        os.makedirs(config.CONFIG_DIR, exist_ok=True)
        os.makedirs(config.LOCKER_DIR, exist_ok=True)
        os.makedirs(config.TEMP_DIR, exist_ok=True)
        self.vault_path = config.VAULT_FILE
        self.master_password: Optional[str] = None
        self.salt: Optional[bytes] = None
        self.vault_data = None

    def new_vault_structure(self):
        return {
            "passwords": {},
            "twofa": {},
            "notes": {},
            "categories": ["Personal", "Work", "Financial", "Social"],
        }

    def set_master_password_interactive(self, prompt_fn):
        while True:
            p1 = prompt_fn("Enter a strong master password")
            if len(p1) < 8:
                print("Password must be at least 8 characters")
                continue
            p2 = prompt_fn("Confirm master password")
            if p1 != p2:
                print("Passwords do not match")
                continue
            self.master_password = p1
            self.salt = os.urandom(encryption.SALT_SIZE)
            return True

    def save_vault(self) -> bool:
        if not self.master_password:
            return False
        try:
            data = self.vault_data or self.new_vault_structure()
            encrypted, salt = encryption.VaultEncryption.encrypt_data(data, self.master_password, self.salt)
            with open(self.vault_path, "wb") as f:
                f.write(salt)
                f.write(encrypted)
            return True
        except Exception:
            return False

    def load_vault(self, password: str) -> bool:
        if not os.path.exists(self.vault_path):
            return False
        try:
            with open(self.vault_path, "rb") as f:
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
