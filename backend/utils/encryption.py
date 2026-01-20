from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from pathlib import Path
from backend.config.settings import settings


def get_encryption_key() -> bytes:
    """Génère ou récupère la clé de chiffrement basée sur l'utilisateur système"""
    key_file = settings.DATA_DIR / ".encryption_key"
    
    if key_file.exists():
        with open(key_file, "rb") as f:
            return f.read()
    
    # Générer une nouvelle clé basée sur le nom d'utilisateur système
    # Utiliser PBKDF2 pour dériver une clé à partir d'un salt
    username = os.getenv("USERNAME") or os.getenv("USER") or "default"
    salt = b"nadia_salt_2024"  # Salt fixe pour la cohérence
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(username.encode()))
    
    # Sauvegarder la clé
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(key_file, "wb") as f:
        f.write(key)
    
    # Sécuriser le fichier de clé
    os.chmod(key_file, 0o600)
    
    return key


def encrypt_data(data: str) -> str:
    """Chiffre une chaîne de caractères"""
    key = get_encryption_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_data(encrypted_data: str) -> str:
    """Déchiffre une chaîne de caractères"""
    key = get_encryption_key()
    fernet = Fernet(key)
    encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
    decrypted = fernet.decrypt(encrypted_bytes)
    return decrypted.decode()
