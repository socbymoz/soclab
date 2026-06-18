import hashlib
import os


def hash_password(password: str) -> str:
    salt = os.urandom(32)
    pwd = salt + hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return pwd.hex()


def verify_password(password: str, stored: str) -> bool:
    raw = bytes.fromhex(stored)
    salt = raw[:32]
    key = raw[32:]
    new_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return key == new_key
