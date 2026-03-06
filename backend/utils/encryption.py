import base64
import os

from cryptography.fernet import Fernet

from backend.config.settings import storage_settings


def get_encryption_key() -> bytes:
    key_file = storage_settings.DATA_DIR / ".encryption_key"

    if key_file.exists():
        with open(key_file, "rb") as f:
            return f.read()

    key = Fernet.generate_key()

    storage_settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(key_file, "wb") as f:
        f.write(key)

    os.chmod(key_file, 0o600)
    return key


def encrypt_data(data: str) -> str:
    key = get_encryption_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_data(encrypted_data: str) -> str:
    key = get_encryption_key()
    fernet = Fernet(key)
    encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
    decrypted = fernet.decrypt(encrypted_bytes)
    return decrypted.decode()
