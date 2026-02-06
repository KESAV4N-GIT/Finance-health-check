"""
Encryption Utilities
AES-256 encryption for sensitive data.
"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.config import settings


def get_encryption_key() -> bytes:
    """Derive encryption key from settings."""
    password = settings.ENCRYPTION_KEY.encode()
    salt = settings.SECRET_KEY[:16].encode()
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key


def get_fernet() -> Fernet:
    """Get Fernet instance for encryption/decryption."""
    return Fernet(get_encryption_key())


def encrypt_data(data: str) -> str:
    """Encrypt string data."""
    f = get_fernet()
    return f.encrypt(data.encode()).decode()


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt string data."""
    f = get_fernet()
    return f.decrypt(encrypted_data.encode()).decode()


def encrypt_file(content: bytes) -> bytes:
    """Encrypt file content."""
    f = get_fernet()
    return f.encrypt(content)


def decrypt_file(encrypted_content: bytes) -> bytes:
    """Decrypt file content."""
    f = get_fernet()
    return f.decrypt(encrypted_content)
