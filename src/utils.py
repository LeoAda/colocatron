import secrets
from hashlib import sha256


def generate_secret_key() -> str:
    # To put in .env as 'SECRET_KEY'
    secret = secrets.token_hex()
    print(f"Secret : {secret}")
    return secret


def string_hash(string: str) -> str:
    return sha256(string.encode("utf-8")).hexdigest()
