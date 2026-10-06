from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ValueError:  # malformed hash in config
        return False


def authenticate_admin(username: str, password: str) -> bool:
    # Always run bcrypt so a wrong username takes as long as a wrong password.
    password_ok = verify_password(password, settings.admin_password_hash)
    return username == settings.admin_username and password_ok


def create_access_token(subject: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expires_at}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str:
    """Return the token's subject. Raises `jwt.InvalidTokenError` if invalid or expired."""
    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    subject = payload.get("sub")
    if not subject:
        raise jwt.InvalidTokenError("Token has no subject")
    return subject
