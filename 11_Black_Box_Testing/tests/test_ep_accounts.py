"""Equivalence partitioning, M1 (registration, login, role checks). One representative per class.

TC-M1-027 name (R1.1)     TC-M1-028 email (R1.2)    TC-M1-029 password (R1.3)
TC-M1-030 phone (R1.4)    TC-M1-031 login credentials (R1.5)    TC-M1-032 caller role and token (R1.6)
"""
import pytest

import helpers
from helpers import call, field_names, register


def P(tc, cls, *values):
    return pytest.param(*values, id=f"{tc}-{cls}")


# ---- TC-M1-027: name ------------------------------------------------------------------------
@pytest.mark.parametrize("name,status", [
    P("TC-M1-027", "EP1-valid-letters-and-space", "Jane Doe", 201),
    P("TC-M1-027", "EP2-too-short", "A", 422),
    P("TC-M1-027", "EP3-too-long", "A" * 51, 422),
    P("TC-M1-027", "EP4-digit", "Jane2", 422),
    P("TC-M1-027", "EP5-symbol", "Jane@Doe", 422),
    P("TC-M1-027", "EP6-empty", "", 422),
])
def test_name_classes(name, status):
    r = register(name=name)
    assert r.status_code == status, r.text
    if status == 422:
        assert "name" in field_names(r)


# ---- TC-M1-028: email -----------------------------------------------------------------------
@pytest.mark.parametrize("email,status", [
    P("TC-M1-028", "EP1-valid-unused", None, 201),
    P("TC-M1-028", "EP2-no-at-sign", "not-an-email", 422),
    P("TC-M1-028", "EP3-no-domain-dot", "user@host", 422),
    P("TC-M1-028", "EP4-already-registered-any-case", "CUSTOMER2@FRESHCART.TEST", 409),
    P("TC-M1-028", "EP5-longer-than-100", "a" * 100 + "@x.co", 422),
    P("TC-M1-028", "EP6-empty", "", 422),
])
def test_email_classes(email, status):
    r = register() if email is None else register(email=email)
    assert r.status_code == status, r.text
    if status == 422:
        assert "email" in field_names(r)


# ---- TC-M1-029: password --------------------------------------------------------------------
@pytest.mark.parametrize("password,status", [
    P("TC-M1-029", "EP1-valid", "Pasw0rd1", 201),
    P("TC-M1-029", "EP2-too-short", "Pas1abc", 422),
    P("TC-M1-029", "EP3-too-long", "Pasw0rd1" * 3, 422),
    P("TC-M1-029", "EP4-no-digit", "Passwordonly", 422),
    P("TC-M1-029", "EP5-no-letter", "12345678", 422),
    P("TC-M1-029", "EP6-empty", "", 422),
])
def test_password_classes(password, status):
    r = register(password=password)
    assert r.status_code == status, r.text
    if status == 422:
        assert "password" in field_names(r)


# ---- TC-M1-030: phone -----------------------------------------------------------------------
@pytest.mark.parametrize("phone,status", [
    P("TC-M1-030", "EP1-valid", "9123456780", 201),
    P("TC-M1-030", "EP2-first-digit-0-5", "5123456789", 422),
    P("TC-M1-030", "EP3-too-few-digits", "912345678", 422),
    P("TC-M1-030", "EP4-too-many-digits", "91234567801", 422),
    P("TC-M1-030", "EP5-non-digits", "91234abcde", 422),
    P("TC-M1-030", "EP6-empty", "", 422),
])
def test_phone_classes(phone, status):
    r = register(phone=phone)
    assert r.status_code == status, r.text
    if status == 422:
        assert "phone" in field_names(r)


# ---- TC-M1-031: login credentials -----------------------------------------------------------
@pytest.mark.parametrize("email,password,status", [
    P("TC-M1-031", "EP1-registered-correct", helpers.CUSTOMER1[0], helpers.CUSTOMER1[1], 200),
    P("TC-M1-031", "EP2-registered-wrong-password", helpers.CUSTOMER1[0], "Wrong@1234", 401),
    P("TC-M1-031", "EP3-unknown-email", "nobody@freshcart.test", "Customer@1234", 401),
    P("TC-M1-031", "EP4-malformed-email", "not-an-email", "Customer@1234", 422),
    P("TC-M1-031", "EP5-email-case-insensitive", "CUSTOMER1@FRESHCART.TEST", helpers.CUSTOMER1[1], 200),
])
def test_login_classes(email, password, status):
    r = helpers.rate_limited("POST", "/auth/login", json={"email": email, "password": password})
    assert r.status_code == status, r.text
    if status == 200:
        assert r.json()["token_type"] == "bearer" and r.json()["access_token"]
    if status == 401:   # no hint about which half was wrong
        assert r.json()["message"] == "Invalid email or password."


# ---- TC-M1-032: caller role and token -------------------------------------------------------
@pytest.mark.parametrize("who,method,path,status", [
    P("TC-M1-032", "EP1-no-token", None, "GET", "/cart", 401),
    P("TC-M1-032", "EP2-garbage-token", "garbage", "GET", "/cart", 401),
    P("TC-M1-032", "EP3-customer-on-customer-endpoint", "customer1", "GET", "/cart", 200),
    P("TC-M1-032", "EP4-customer-on-admin-endpoint", "customer1", "GET", "/admin/dashboard", 403),
    P("TC-M1-032", "EP5-customer-on-delivery-endpoint", "customer1", "GET", "/delivery/orders", 403),
    P("TC-M1-032", "EP6-admin-on-admin-endpoint", "admin", "GET", "/admin/dashboard", 200),
    P("TC-M1-032", "EP7-admin-on-delivery-endpoint", "admin", "GET", "/delivery/orders", 403),
    P("TC-M1-032", "EP8-driver-on-delivery-endpoint", "driver", "GET", "/delivery/orders", 200),
    P("TC-M1-032", "EP9-driver-on-admin-endpoint", "driver", "GET", "/admin/orders", 403),
    P("TC-M1-032", "EP10-no-token-on-admin-endpoint", None, "GET", "/admin/orders", 401),
])
def test_role_and_token_classes(request, who, method, path, status):
    token = who if who in (None, "garbage") else request.getfixturevalue(who)
    r = call(method, path, token)
    assert r.status_code == status, r.text
