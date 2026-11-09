from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header

from app.config import get_settings
from app.core.errors import UnauthorizedError
from app.core.rate_limit import rate_limiter
from app.core.security import decode_access_token
from app.database import get_db
from app.deps import get_current_user, get_now
from app.schemas.user import LoginRequest, RegisterRequest, TokenResponse, UserOut
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post(
    "/register",
    response_model=UserOut,
    status_code=201,
    summary="Register a new customer account (R1.1-R1.4)",
    dependencies=[Depends(rate_limiter("register", max_requests=10, window_seconds=60))],
)
async def register(payload: RegisterRequest, db=Depends(get_db), now: datetime = Depends(get_now)):
    user = await auth_service.register_user(db, now, payload.name, payload.email, payload.password, payload.phone)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in and receive a JWT access token (R1.5)",
    dependencies=[Depends(rate_limiter("login", max_requests=10, window_seconds=60))],
)
async def login(payload: LoginRequest, db=Depends(get_db), now: datetime = Depends(get_now)):
    _user, token = await auth_service.authenticate_user(db, now, payload.email, payload.password)
    return TokenResponse(access_token=token, expires_in=settings.JWT_EXPIRE_MINUTES * 60)


@router.post("/logout", summary="Log out and revoke the current token (R1.8)")
async def logout(
    authorization: str | None = Header(default=None),
    db=Depends(get_db),
    user=Depends(get_current_user),
):
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise UnauthorizedError(str(exc)) from exc
    expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc).replace(tzinfo=None)
    await auth_service.denylist_token(db, payload["jti"], expires_at)
    return {"message": "Logged out successfully."}


@router.get("/me", response_model=UserOut, summary="Get the current authenticated user")
async def me(user=Depends(get_current_user)):
    return user
