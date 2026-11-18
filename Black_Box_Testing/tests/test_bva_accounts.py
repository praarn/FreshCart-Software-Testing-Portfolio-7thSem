"""Boundary value analysis, M1. Each limit is probed at min-1, min, min+1, max-1, max, max+1.

TC-M1-033 name length 2..50 (R1.1)       TC-M1-034 email length max 100 (R1.2)
TC-M1-035 password length 8..20 (R1.3)   TC-M1-036 phone length and first digit (R1.4)
TC-M1-037 failed-login threshold of 5 (R1.5)
"""
import pytest

import helpers
from helpers import field_names, register, unique_email


def P(tc, label, *values):
    return pytest.param(*values, id=f"{tc}-{label}")


@pytest.mark.parametrize("length,status", [
    P("TC-M1-033", "len1-min-1", 1, 422), P("TC-M1-033", "len2-min", 2, 201), P("TC-M1-033", "len3-min+1", 3, 201),
    P("TC-M1-033", "len49-max-1", 49, 201), P("TC-M1-033", "len50-max", 50, 201), P("TC-M1-033", "len51-max+1", 51, 422),
])
def test_name_length(length, status):
    r = register(name="A" * length)
    assert r.status_code == status, r.text
    if status == 422:
        assert "name" in field_names(r)


@pytest.mark.parametrize("length,status", [
    P("TC-M1-034", "len99-max-1", 99, 201), P("TC-M1-034", "len100-max", 100, 201), P("TC-M1-034", "len101-max+1", 101, 422),
])
def test_email_length(length, status):
    email = unique_email(length)
    assert len(email) == length
    r = register(email=email)
    assert r.status_code == status, r.text
    if status == 422:
        assert "email" in field_names(r)


@pytest.mark.parametrize("length,status", [
    P("TC-M1-035", "len7-min-1", 7, 422), P("TC-M1-035", "len8-min", 8, 201), P("TC-M1-035", "len9-min+1", 9, 201),
    P("TC-M1-035", "len19-max-1", 19, 201), P("TC-M1-035", "len20-max", 20, 201), P("TC-M1-035", "len21-max+1", 21, 422),
])
def test_password_length(length, status):
    r = register(password="a" * (length - 1) + "1")   # always one letter class and one digit
    assert r.status_code == status, r.text
    if status == 422:
        assert "password" in field_names(r)


@pytest.mark.parametrize("phone,status", [
    P("TC-M1-036", "9-digits-length-min-1", "912345678", 422),
    P("TC-M1-036", "10-digits-length-exact", "9123456780", 201),
    P("TC-M1-036", "11-digits-length-max+1", "91234567801", 422),
    P("TC-M1-036", "first-digit-5-min-1", "5123456789", 422),
    P("TC-M1-036", "first-digit-6-min", "6123456789", 201),
    P("TC-M1-036", "first-digit-7-min+1", "7123456789", 201),
    P("TC-M1-036", "first-digit-8-max-1", "8123456789", 201),
    P("TC-M1-036", "first-digit-9-max", "9123456789", 201),
])
def test_phone_length_and_first_digit(phone, status):
    r = register(phone=phone)
    assert r.status_code == status, r.text
    if status == 422:
        assert "phone" in field_names(r)


# ---- TC-M1-037: lockout threshold. State-changing, so each case starts from a clean database ----
BAD = {"email": helpers.CUSTOMER1[0], "password": "Wrong@1234"}
GOOD = {"email": helpers.CUSTOMER1[0], "password": helpers.CUSTOMER1[1]}


def _fail(n):
    return [helpers.rate_limited("POST", "/auth/login", json=BAD) for _ in range(n)]


@pytest.mark.parametrize("failures,locked", [
    P("TC-M1-037", "4-failures-max-1", 4, False),
    P("TC-M1-037", "5-failures-max", 5, True),
])
def test_lockout_threshold(fresh_db, failures, locked):
    attempts = _fail(failures)
    assert all(a.status_code == 401 for a in attempts)
    r = helpers.rate_limited("POST", "/auth/login", json=GOOD)
    if locked:
        assert r.status_code == 401 and "locked" in r.json()["message"].lower()
    else:
        assert r.status_code == 200


def test_lockout_counter_resets_after_success(fresh_db):
    """TC-M1-037: 4 failures, a success, then 4 more failures must not lock (the counter restarted)."""
    _fail(4)
    assert helpers.rate_limited("POST", "/auth/login", json=GOOD).status_code == 200
    _fail(4)
    assert helpers.rate_limited("POST", "/auth/login", json=GOOD).status_code == 200


def test_locked_account_stays_locked_for_correct_password(fresh_db):
    """TC-M1-037: the 6th attempt (max+1) is still refused even though it carries the right password."""
    _fail(5)
    for _ in range(2):
        r = helpers.rate_limited("POST", "/auth/login", json=GOOD)
        assert r.status_code == 401 and "locked" in r.json()["message"].lower()
