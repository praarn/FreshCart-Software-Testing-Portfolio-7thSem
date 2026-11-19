"""M4 — Coupons and pricing (R4.1-R4.4)."""
from conftest import login_as
from pages.cart_checkout_pages import CartPage
from utils import api_client
from utils.config import CUSTOMER1, CUSTOMER2


def _add(token, product_id, qty):
    r = api_client.post("/cart/items", token=token, json={"product_id": product_id, "quantity": qty})
    assert r.status_code == 200
    return r.json()


def test_welcome10_applies_for_first_order(driver):
    """TC-M4-001 (R4.1/R4.2): WELCOME10 gives 10% off for an eligible first-time order."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    apple_id = api_client.product_id_by_name("Apple")  # 180.00
    _add(token, apple_id, 2)  # subtotal 360.00

    login_as(driver, CUSTOMER2["email"], CUSTOMER2["password"])
    cart = CartPage(driver).open()
    cart.wait_visible("cart-summary")
    cart.apply_coupon("WELCOME10")
    cart.wait_text_contains("cart-discount", "36.00")


def test_welcome10_capped_at_100(driver):
    """TC-M4-002 (R4.1, boundary): WELCOME10's discount is capped at 100 regardless of subtotal."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    carrot_id = api_client.product_id_by_name("Carrot")  # 60.00; qty up to 10 -> 600 (need >1000, use multiple products)
    apple_id = api_client.product_id_by_name("Apple")
    _add(token, apple_id, 10)  # 1800
    _add(token, carrot_id, 10)  # +600 = 2400
    r = api_client.post("/cart/coupon", token=token, json={"code": "WELCOME10"})
    assert r.status_code == 200
    assert r.json()["discount"] == "100.00"


def test_coupon_below_minimum_rejected(driver):
    """TC-M4-003 (R4.2): a coupon applied below its minimum subtotal is rejected."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    carrot_id = api_client.product_id_by_name("Carrot")
    _add(token, carrot_id, 1)  # subtotal 60.00, below FLAT50's 500 minimum
    r = api_client.post("/cart/coupon", token=token, json={"code": "FLAT50"})
    assert r.status_code == 400
    assert "minimum" in r.json()["message"].lower()


def test_welcome10_rejected_for_non_first_order(driver):
    """TC-M4-004 (R4.2): WELCOME10 is rejected for a customer with a prior order."""
    token = api_client.login(CUSTOMER1["email"], CUSTOMER1["password"])
    apple_id = api_client.product_id_by_name("Apple")
    _add(token, apple_id, 2)
    r = api_client.post("/cart/coupon", token=token, json={"code": "WELCOME10"})
    assert r.status_code == 400
    assert "first-time" in r.json()["message"].lower() or "first order" in r.json()["message"].lower()


def test_fresh15_accepted_on_allowed_weekday(driver):
    """TC-M4-005 (R4.1/R4.2): FRESH15 is accepted when FIXED_NOW falls on a weekday
    and the subtotal meets its minimum (assumes the backend is started with
    FIXED_NOW=2026-11-10, a Tuesday)."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    cake_id = api_client.product_id_by_name("Chocolate Cake")  # 350.00
    _add(token, cake_id, 3)  # 1050.00 >= 800
    r = api_client.post("/cart/coupon", token=token, json={"code": "FRESH15"})
    assert r.status_code == 200
    assert r.json()["discount"] == "150.00"  # 15% of 1050 = 157.50, capped at 150


def test_expired_coupon_rejected(driver):
    """TC-M4-006 (R4.2): OLD20 is always rejected (expired)."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    apple_id = api_client.product_id_by_name("Apple")
    _add(token, apple_id, 1)
    r = api_client.post("/cart/coupon", token=token, json={"code": "OLD20"})
    assert r.status_code == 400
    assert "expired" in r.json()["message"].lower()


def test_unknown_coupon_rejected(driver):
    """TC-M4-007 (R4.2): an unknown coupon code is rejected with a distinct message."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    apple_id = api_client.product_id_by_name("Apple")
    _add(token, apple_id, 1)
    r = api_client.post("/cart/coupon", token=token, json={"code": "NOTREAL"})
    assert r.status_code == 400
    assert "not a valid" in r.json()["message"].lower()


def test_coupon_code_case_insensitive(driver):
    """TC-M4-008 (R4.2): coupon codes are case-insensitive."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    apple_id = api_client.product_id_by_name("Apple")
    _add(token, apple_id, 2)
    r = api_client.post("/cart/coupon", token=token, json={"code": "welcome10"})
    assert r.status_code == 200
    assert r.json()["coupon_code"] == "WELCOME10"


def test_delivery_fee_free_at_threshold(driver):
    """TC-M4-010 (R4.3, boundary): delivery fee is free once the subtotal reaches 299.00.
    All seeded product prices are multiples of 5, so an exact 299.00 subtotal cannot be
    built from the catalog (299 is not a multiple of 5) — 300.00 is the nearest achievable
    value at/above the threshold, which still exercises the ">=299.00 -> free" branch."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    apple_id = api_client.product_id_by_name("Apple")  # 180.00
    orange_id = api_client.product_id_by_name("Orange")  # 120.00
    _add(token, apple_id, 1)
    r = _add(token, orange_id, 1)  # subtotal = 300.00
    assert r["subtotal"] == "300.00"
    assert r["delivery_fee"] == "0.00"


def test_delivery_fee_charged_below_threshold(driver):
    """TC-M4-011 (R4.3, boundary): delivery fee is 40.00 just below the threshold — 295.00
    is the nearest achievable value below 299.00 given the seeded (multiple-of-5) prices."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    apple_id = api_client.product_id_by_name("Apple")  # 180.00
    banana_id = api_client.product_id_by_name("Banana")  # 60.00
    butter_id = api_client.product_id_by_name("Butter")  # 55.00
    _add(token, apple_id, 1)
    _add(token, banana_id, 1)
    r = _add(token, butter_id, 1)  # subtotal = 295.00
    assert r["subtotal"] == "295.00"
    assert r["delivery_fee"] == "40.00"
