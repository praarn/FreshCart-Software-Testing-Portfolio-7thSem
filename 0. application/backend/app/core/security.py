from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

settings = get_settings()
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _pwd_context.verify(password, password_hash)


def create_access_token(user_id: int, role: str, now: datetime) -> tuple[str, str]:
    jti = uuid4().hex
    expire = now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "role": role,
        "jti": jti,
        "iat": int(now.replace(tzinfo=timezone.utc).timestamp()),
        "exp": int(expire.replace(tzinfo=timezone.utc).timestamp()),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token, jti


def decode_access_token(token: str) -> dict:
    """Expiry is checked against the same injected clock that issued the token (FIXED_NOW in
    test mode, wall clock otherwise). jose's built-in exp check uses the real clock, which
    rejected every token once real time passed FIXED_NOW + 30 min (DEF-003)."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM], options={"verify_exp": False}
        )
    except JWTError as exc:
        raise ValueError("Invalid or expired token.") from exc
    now = settings.fixed_now or datetime.now(timezone.utc).replace(tzinfo=None)
    if int(payload.get("exp", 0)) <= int(now.replace(tzinfo=timezone.utc).timestamp()):
        raise ValueError("Invalid or expired token.")
    return payload
