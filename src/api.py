import secrets


def generate_secret_key() -> str:
    # To put in .env as 'SECRET_KEY'
    secret = secrets.token_hex()
    print(f"Secret : {secret}")
    return secret
