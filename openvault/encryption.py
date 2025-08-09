# openvault/encryption.py
import os
import base64
import json
from typing import Tuple, Optional, Callable
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet, InvalidToken

SALT_SIZE = 16

class VaultEncryption:
    @staticmethod
    def generate_key(password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        if salt is None:
            salt = os.urandom(SALT_SIZE)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt

    @staticmethod
    def encrypt_data(data: dict, password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        key, salt = VaultEncryption.generate_key(password, salt)
        fernet = Fernet(key)
        encrypted = fernet.encrypt(json.dumps(data).encode())
        return encrypted, salt

    @staticmethod
    def decrypt_data(encrypted_data: bytes, password: str, salt: bytes) -> Optional[dict]:
        key, _ = VaultEncryption.generate_key(password, salt)
        fernet = Fernet(key)
        try:
            raw = fernet.decrypt(encrypted_data)
            return json.loads(raw.decode())
        except InvalidToken:
            return None

    @staticmethod
    def encrypt_file(input_path: str, out_path: str, password: str,
                     progress_callback: Optional[Callable[[int], None]] = None) -> bool:
        """Chunk-read the file (progress_callback receives percent 0..100)."""
        try:
            file_size = os.path.getsize(input_path)
            read = 0
            CHUNK = 8 * 1024 * 1024
            buf = bytearray()
            with open(input_path, "rb") as f:
                while True:
                    chunk = f.read(CHUNK)
                    if not chunk:
                        break
                    buf.extend(chunk)
                    read += len(chunk)
                    if progress_callback and file_size:
                        progress_callback(min(100, int(read / file_size * 100)))
            key, salt = VaultEncryption.generate_key(password)
            fernet = Fernet(key)
            encrypted = fernet.encrypt(bytes(buf))
            with open(out_path, "wb") as out:
                out.write(salt)
                out.write(encrypted)
            if progress_callback:
                progress_callback(100)
            return True
        except Exception:
            return False

    @staticmethod
    def decrypt_file(encrypted_path: str, out_path: str, password: str,
                     progress_callback: Optional[Callable[[int], None]] = None) -> bool:
        try:
            with open(encrypted_path, "rb") as f:
                salt = f.read(SALT_SIZE)
                encrypted = f.read()
            key, _ = VaultEncryption.generate_key(password, salt)
            fernet = Fernet(key)
            decrypted = fernet.decrypt(encrypted)
            with open(out_path, "wb") as out:
                out.write(decrypted)
            if progress_callback:
                progress_callback(100)
            return True
        except Exception:
            return False
