from datetime import datetime, timezone

from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.errors import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.database import get_db
from app.models.enums import Role, UserStatus
from app.models.token_denylist import TokenDenylist
from app.models.user import User

settings = get_settings()


def get_now() -> datetime:
    """R: injected clock. FIXED_NOW freezes business time for deterministic slot/weekday tests."""
    fixed = settings.fixed_now
    return fixed if fixed is not None else datetime.now(timezone.utc).replace(tzinfo=None)


async def get_current_user(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Missing or invalid Authorization header.")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise UnauthorizedError(str(exc)) from exc

    jti = payload.get("jti")
    denylisted = await db.scalar(select(TokenDenylist).where(TokenDenylist.jti == jti))
    if denylisted is not None:
        raise UnauthorizedError("Token has been revoked. Please log in again.")

    user_id = int(payload["sub"])
    user = await db.get(User, user_id)
    if user is None:
        raise UnauthorizedError("User no longer exists.")

    now = get_now()
    if user.status == UserStatus.LOCKED and user.locked_until and user.locked_until <= now:
        user.status = UserStatus.ACTIVE
        user.failed_login_count = 0
        user.locked_until = None
        await db.commit()

    return user


def require_role(*roles: Role):
    async def _dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise ForbiddenError("You do not have permission to access this resource.")
        return user

    return _dependency


require_customer = require_role(Role.CUSTOMER)
require_admin = require_role(Role.ADMIN)
require_delivery_partner = require_role(Role.DELIVERY_PARTNER)
