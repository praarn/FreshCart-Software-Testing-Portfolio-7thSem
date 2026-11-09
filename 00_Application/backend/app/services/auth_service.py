"""M1 business logic: registration, login with lockout, logout denylisting."""
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.errors import ConflictError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.cart import Cart
from app.models.enums import Role, UserStatus
from app.models.token_denylist import TokenDenylist
from app.models.user import User

settings = get_settings()


async def register_user(db: AsyncSession, now: datetime, name: str, email: str, password: str, phone: str) -> User:
    existing = await db.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise ConflictError(
            "Email is already registered.",
            field_errors=[{"field": "email", "message": "Email is already registered."}],
        )

    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        phone=phone,
        role=Role.CUSTOMER,
        status=UserStatus.ACTIVE,
        created_at=now,
        updated_at=now,
    )
    db.add(user)
    await db.flush()
    db.add(Cart(user_id=user.id))
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, now: datetime, email: str, password: str) -> tuple[User, str]:
    user = await db.scalar(select(User).where(User.email == email))
    if user is None:
        raise UnauthorizedError("Invalid email or password.")

    if user.status == UserStatus.LOCKED:
        if user.locked_until and user.locked_until <= now:
            user.status = UserStatus.ACTIVE
            user.failed_login_count = 0
            user.locked_until = None
        else:
            raise UnauthorizedError("This account is locked. Try again later or contact an admin to unlock it.")

    if not verify_password(password, user.password_hash):
        user.failed_login_count += 1
        if user.failed_login_count >= settings.MAX_FAILED_LOGINS:
            user.status = UserStatus.LOCKED
            user.locked_until = now + timedelta(minutes=settings.ACCOUNT_LOCK_MINUTES)
        user.updated_at = now
        await db.commit()
        raise UnauthorizedError("Invalid email or password.")

    user.failed_login_count = 0
    user.updated_at = now
    await db.commit()

    token, _jti = create_access_token(user.id, user.role.value, now)
    return user, token


async def denylist_token(db: AsyncSession, jti: str, expires_at: datetime) -> None:
    db.add(TokenDenylist(jti=jti, expires_at=expires_at))
    await db.commit()
