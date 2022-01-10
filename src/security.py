from hashlib import pbkdf2_hmac
from secrets import token_bytes, compare_digest


def hash_password(password: str) -> tuple[bytes, bytes]:
    salt = token_bytes(32)
    hashed = pbkdf2_hmac('sha256', password.encode(), salt, 200000)
    return hashed, salt


def check_password(password: str, hashed: bytes, salt: bytes) -> bool:
    h = pbkdf2_hmac('sha256', password.encode(), salt, 200000)
    return compare_digest(h, hashed)


def generate_token() -> bytes:
    return token_bytes(32)
