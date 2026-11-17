"""White-box tests for auth_service.authenticate_user (R1.5 lockout) and core/security (R1.5 token expiry, DEF-003).

White-box method 2, statement/branch/condition coverage: TC-M1-038 (authenticate_user, create/decode_access_token)."""
from datetime import datetime, timedelta

import pytest

from app.config import get_settings
from app.core import security
from app.core.errors import UnauthorizedError
from app.core.security import create_access_token, decode_access_token, hash_password
from app.models.enums import UserStatus
from app.services.auth_service import authenticate_user
from tests.unit.conftest import NOW, make_user

PW = "Customer@1234"
HASH = hash_password(PW)  # bcrypt once for the whole module


async def _user(db, **kw):
    return await make_user(db, email="c@x.test", password_hash=HASH, **kw)


async def _fail(db, now, times):
    for _ in range(times):
        with pytest.raises(UnauthorizedError, match="Invalid email or password"):
            await authenticate_user(db, now, "c@x.test", "WrongPass1")


async def test_unknown_email(db):
    with pytest.raises(UnauthorizedError, match="Invalid email or password"):
        await authenticate_user(db, NOW, "nobody@x.test", PW)


async def test_valid_login_returns_token(db):  # TC-M1-012
    user = await _user(db)
    got, token = await authenticate_user(db, NOW, "c@x.test", PW)
    assert got.id == user.id and token


async def test_four_failures_do_not_lock_then_success(db):  # TC-M1-026
    user = await _user(db)
    await _fail(db, NOW, 4)
    assert user.status == UserStatus.ACTIVE and user.failed_login_count == 4
    await authenticate_user(db, NOW, "c@x.test", PW)
    assert user.failed_login_count == 0


async def test_success_resets_counter(db):  # TC-M1-015
    user = await _user(db)
    await _fail(db, NOW, 3)
    await authenticate_user(db, NOW, "c@x.test", PW)
    await _fail(db, NOW, 3)
    assert user.status == UserStatus.ACTIVE and user.failed_login_count == 3


async def test_fifth_failure_locks_for_15_minutes(db):  # TC-M1-014
    user = await _user(db)
    await _fail(db, NOW, 5)
    assert user.status == UserStatus.LOCKED and user.locked_until == NOW + timedelta(minutes=15)


async def test_locked_account_rejects_correct_password(db):  # TC-M1-014
    await _user(db)
    await _fail(db, NOW, 5)
    with pytest.raises(UnauthorizedError, match="locked"):
        await authenticate_user(db, NOW + timedelta(minutes=1), "c@x.test", PW)


async def test_lock_expiry_boundary(db):  # TC-M1-020: 14:59 locked, 15:00 active
    user = await _user(db)
    await _fail(db, NOW, 5)
    with pytest.raises(UnauthorizedError, match="locked"):
        await authenticate_user(db, NOW + timedelta(minutes=14, seconds=59), "c@x.test", PW)
    got, _ = await authenticate_user(db, NOW + timedelta(minutes=15), "c@x.test", PW)
    assert got.status == UserStatus.ACTIVE and user.failed_login_count == 0 and user.locked_until is None


async def test_admin_style_lock_without_expiry_stays_locked(db):  # LOCKED, locked_until is None (admin lock)
    await _user(db, status=UserStatus.LOCKED)
    with pytest.raises(UnauthorizedError, match="locked"):
        await authenticate_user(db, NOW + timedelta(days=30), "c@x.test", PW)


async def test_failed_login_after_lock_expiry_restarts_count(db):
    user = await _user(db)
    await _fail(db, NOW, 5)
    later = NOW + timedelta(minutes=16)
    with pytest.raises(UnauthorizedError, match="Invalid email or password"):
        await authenticate_user(db, later, "c@x.test", "WrongPass1")
    assert user.status == UserStatus.ACTIVE and user.failed_login_count == 1


# ---- core/security: token expiry uses the injected clock (DEF-003) ----
def _with_fixed_now(monkeypatch, value):
    monkeypatch.setattr(security, "settings", get_settings().model_copy(update={"FIXED_NOW": value}))


def test_token_valid_under_fixed_clock_even_if_real_clock_is_later(monkeypatch):  # DEF-003 regression
    _with_fixed_now(monkeypatch, "2026-11-10T09:00:00")
    token, _ = create_access_token(1, "CUSTOMER", datetime(2026, 11, 10, 9, 0))
    assert decode_access_token(token)["sub"] == "1"


def test_token_expired_under_fixed_clock(monkeypatch):
    _with_fixed_now(monkeypatch, "2026-11-10T10:00:00")
    token, _ = create_access_token(1, "CUSTOMER", datetime(2026, 11, 10, 9, 0))  # exp 09:30 < clock 10:00
    with pytest.raises(ValueError, match="expired"):
        decode_access_token(token)


def test_token_boundary_exactly_at_expiry_is_rejected(monkeypatch):
    _with_fixed_now(monkeypatch, "2026-11-10T09:30:00")
    token, _ = create_access_token(1, "CUSTOMER", datetime(2026, 11, 10, 9, 0))
    with pytest.raises(ValueError):
        decode_access_token(token)


def test_token_uses_wall_clock_when_not_fixed(monkeypatch):
    _with_fixed_now(monkeypatch, None)
    now = datetime.utcnow()
    ok, _ = create_access_token(1, "CUSTOMER", now)
    old, _ = create_access_token(1, "CUSTOMER", now - timedelta(hours=2))
    assert decode_access_token(ok)["sub"] == "1"
    with pytest.raises(ValueError):
        decode_access_token(old)


def test_garbage_token_rejected():
    with pytest.raises(ValueError):
        decode_access_token("not.a.jwt")
