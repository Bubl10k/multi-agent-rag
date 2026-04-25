from cryptography.fernet import Fernet

from rag.src.common import settings


def _get_fernet() -> Fernet:
    return Fernet(settings.crypto.ENCRYPTION_KEY.encode())


def encrypt(value: str) -> bytes:
    return _get_fernet().encrypt(value.encode())


def decrypt(value: bytes) -> str:
    return _get_fernet().decrypt(value).decode()
