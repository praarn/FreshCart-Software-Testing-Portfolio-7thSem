"""M1 — Registration and login (R1.1-R1.8). See ../../4-test-cases/Test_Cases.csv
for the full case list; TC IDs are referenced in each test's docstring."""
import time

import pytest

from conftest import login_as
from pages.auth_pages import LoginPage, RegisterPage
from utils import api_client
from utils.config import BASE_URL, CUSTOMER2


def unique_email():
    return f"newuser{int(time.time() * 1000)}@example.com"


def test_register_valid_name(driver):
    """TC-M1-001 (R1.1): a valid registration succeeds and logs the user in."""
    page = RegisterPage(driver).open()
    page.register("Jane Doe", unique_email(), "Passw0rd1", "9876543210")
    page.wait_visible("catalog-product-grid", timeout=10)


def test_register_one_char_name_rejected(driver):
    """TC-M1-002 (R1.1, boundary): a 1-character name is rejected."""
    page = RegisterPage(driver).open()
    page.register("A", unique_email(), "Passw0rd1", "9876543210")
    assert "2-50" in page.field_error("name") or "letters" in page.field_error("name")


def test_register_name_with_digits_rejected(driver):
    """TC-M1-003 (R1.1): a name containing digits is rejected."""
    page = RegisterPage(driver).open()
    page.register("Jane2", unique_email(), "Passw0rd1", "9876543210")
    assert page.field_error("name") != ""


def test_register_duplicate_email_rejected(driver):
    """TC-M1-004 (R1.2): registering with an already-used email (any case) is rejected."""
    page = RegisterPage(driver).open()
    page.register("Dup User", "CUSTOMER2@FRESHCART.TEST", "Passw0rd1", "9876543210")
    assert "registered" in page.text("register-form-error").lower()


def test_register_invalid_email_format_rejected(driver):
    """TC-M1-005 (R1.2): a malformed email is rejected. Uses 'foo@bar' (no TLD) rather than
    e.g. 'not-an-email' (no @ at all) — the latter is blocked by the <input type="email">'s
    native browser validation before the form ever submits, which would test Chrome's
    validator instead of the application's. 'foo@bar' passes native HTML5 email validation
    (which only requires one non-empty label after @) but fails the backend's stricter
    `local@domain.tld` regex, so it correctly reaches the server and exercises R1.2."""
    page = RegisterPage(driver).open()
    page.register("Jane Doe", "foo@bar", "Passw0rd1", "9876543210")
    assert page.field_error("email") != ""


def test_register_7_char_password_rejected(driver):
    """TC-M1-006 (R1.3, boundary): a 7-character password is rejected."""
    page = RegisterPage(driver).open()
    page.register("Jane Doe", unique_email(), "Pas1abc", "9876543210")
    assert page.field_error("password") != ""


def test_register_8_char_password_accepted(driver):
    """TC-M1-007 (R1.3, boundary): an 8-character valid password is accepted."""
    page = RegisterPage(driver).open()
    page.register("Jane Doe", unique_email(), "Pasw0rd1", "9876543210")
    page.wait_visible("catalog-product-grid", timeout=10)


def test_register_21_char_password_rejected(driver):
    """TC-M1-008 (R1.3, boundary): a 21-character password is rejected."""
    page = RegisterPage(driver).open()
    page.register("Jane Doe", unique_email(), "Aa1aaaaaaaaaaaaaaaaaa", "9876543210")
    assert page.field_error("password") != ""


def test_register_password_without_digit_rejected(driver):
    """TC-M1-009 (R1.3): a password with no digit is rejected."""
    page = RegisterPage(driver).open()
    page.register("Jane Doe", unique_email(), "Passwordonly", "9876543210")
    assert page.field_error("password") != ""


def test_register_phone_starting_5_rejected(driver):
    """TC-M1-010 (R1.4): a phone number starting with 5 is rejected."""
    page = RegisterPage(driver).open()
    page.register("Jane Doe", unique_email(), "Passw0rd1", "5123456789")
    assert page.field_error("phone") != ""


def test_register_9_digit_phone_rejected(driver):
    """TC-M1-011 (R1.4, boundary): a 9-digit phone number is rejected."""
    page = RegisterPage(driver).open()
    page.register("Jane Doe", unique_email(), "Passw0rd1", "912345678")
    assert page.field_error("phone") != ""


def test_login_valid_credentials(driver):
    """TC-M1-012 (R1.5): logging in with valid credentials reaches the catalog logged in."""
    page = LoginPage(driver).open()
    page.login(CUSTOMER2["email"], CUSTOMER2["password"])
    page.wait_visible("nav-cart", timeout=10)


def test_login_wrong_password_rejected(driver):
    """TC-M1-013 (R1.5): a wrong password is rejected with a generic message."""
    page = LoginPage(driver).open()
    page.login(CUSTOMER2["email"], "WrongPass1")
    assert "invalid" in page.error_text().lower()


def test_login_lockout_after_5_failed_attempts(driver):
    """TC-M1-014 (R1.5, critical boundary): the 5th consecutive failed login locks the
    account; even the correct password is then rejected with a locked message."""
    page = LoginPage(driver).open()
    for _ in range(5):
        page.login(CUSTOMER2["email"], "WrongPass1")
        page.wait_visible("login-form-error")
    page.login(CUSTOMER2["email"], CUSTOMER2["password"])
    assert "locked" in page.error_text().lower()


def test_customer_endpoint_requires_auth(driver):
    """TC-M1-016 (R1.6): calling a customer endpoint with no token returns 401."""
    r = api_client.get("/cart")
    assert r.status_code == 401


def test_customer_cannot_access_admin_ui(driver):
    """TC-M1-017 (R1.6): a logged-in customer is denied access to /admin."""
    login_as(driver, CUSTOMER2["email"], CUSTOMER2["password"])
    driver.get(f"{BASE_URL}/admin")
    from pages.base_page import BasePage

    page = BasePage(driver)
    page.wait_visible("role-guard-denied", timeout=10)


def test_logout_revokes_token(driver):
    """TC-M1-019 (R1.8): a token is rejected after logout (denylisted)."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    r = api_client.get("/auth/me", token=token)
    assert r.status_code == 200

    driver.get(BASE_URL)
    driver.execute_script("window.localStorage.setItem('fc_token', arguments[0]);", token)
    driver.get(BASE_URL)
    from pages.base_page import BasePage

    BasePage(driver).click("nav-logout-button")

    # The logout click fires an async request; poll until the token is rejected instead of racing it.
    import time

    deadline = time.time() + 10
    r2 = api_client.get("/auth/me", token=token)
    while r2.status_code != 401 and time.time() < deadline:
        time.sleep(0.25)
        r2 = api_client.get("/auth/me", token=token)
    assert r2.status_code == 401
