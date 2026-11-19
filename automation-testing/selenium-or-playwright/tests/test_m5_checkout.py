"""M5 — Checkout (R5.1-R5.5)."""
from conftest import login_as
from pages.cart_checkout_pages import CartPage, CheckoutPage
from pages.orders_pages import OrderDetailPage
from utils import api_client
from utils.config import CUSTOMER2, NON_SERVICEABLE_PINCODE, SERVICEABLE_PINCODE


def _cart_with_apple(token, qty=1):
    apple_id = api_client.product_id_by_name("Apple")
    return api_client.post("/cart/items", token=token, json={"product_id": apple_id, "quantity": qty})


def test_checkout_serviceable_pincode_succeeds(driver):
    """TC-M5-001 (R5.1): checkout with a serviceable pincode (560001-560100) succeeds."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    _cart_with_apple(token, 1)
    login_as(driver, CUSTOMER2["email"], CUSTOMER2["password"])

    page = CheckoutPage(driver).open()
    page.wait_visible("checkout-form")
    page.fill_address("123 MG Road, Indiranagar", "Bengaluru", SERVICEABLE_PINCODE)
    page.select_slot_by_index(1)
    page.pay_cod()
    page.submit()

    order = OrderDetailPage(driver)
    order.wait_visible("order-detail-number", timeout=10)
    assert order.order_number().startswith("FC-")


def test_checkout_non_serviceable_pincode_rejected(driver):
    """TC-M5-002 (R5.1, boundary): a pincode just outside 560001-560100 is rejected."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    _cart_with_apple(token, 1)
    login_as(driver, CUSTOMER2["email"], CUSTOMER2["password"])

    page = CheckoutPage(driver).open()
    page.wait_visible("checkout-form")
    page.fill_address("123 MG Road", "Bengaluru", NON_SERVICEABLE_PINCODE)
    page.select_slot_by_index(1)
    page.pay_cod()
    page.submit()
    assert "not available" in page.error_text().lower()


def test_checkout_short_address_line1_rejected(driver):
    """TC-M5-003 (R5.1, boundary): an address line1 shorter than 5 chars is rejected."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    _cart_with_apple(token, 1)
    login_as(driver, CUSTOMER2["email"], CUSTOMER2["password"])

    page = CheckoutPage(driver).open()
    page.wait_visible("checkout-form")
    page.fill("checkout-line1-input", "Flat")
    page.fill("checkout-city-input", "Bengaluru")
    page.fill("checkout-pincode-input", SERVICEABLE_PINCODE)
    # HTML5 'required'/minlength is not enforced client-side here; submit relies on backend 422.
    page.select_slot_by_index(1)
    page.pay_cod()
    page.submit()
    page.wait_visible("checkout-form-error", timeout=10)


def test_checkout_slot_less_than_2h_away_rejected(driver):
    """TC-M5-004 (R5.2, boundary): a slot under 2 hours away is rejected by the API even if
    forced directly (the UI itself only ever offers valid slots)."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    _cart_with_apple(token, 1)
    r = api_client.post(
        "/checkout",
        token=token,
        json={
            "address": {"line1": "123 MG Road", "city": "Bengaluru", "pincode": SERVICEABLE_PINCODE},
            "slot_start": "2026-11-10T10:00:00",
            "payment": {"method": "COD"},
        },
    )
    assert r.status_code == 400
    assert "2 hours" in r.json()["message"]


def test_full_slot_rejects_6th_order(driver):
    """TC-M5-006 (R5.2, boundary): a slot already holding 5 orders rejects a 6th."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    banana_id = api_client.product_id_by_name("Banana")
    slot = "2026-11-10T14:00:00"
    statuses = []
    for _ in range(6):
        api_client.post("/cart/items", token=token, json={"product_id": banana_id, "quantity": 1})
        r = api_client.post(
            "/checkout",
            token=token,
            json={
                "address": {"line1": "123 MG Road", "city": "Bengaluru", "pincode": SERVICEABLE_PINCODE},
                "slot_start": slot,
                "payment": {"method": "COD"},
            },
        )
        statuses.append(r.status_code)
    assert statuses[:5] == [201] * 5
    assert statuses[5] == 400


def test_cod_rejected_above_5000(driver):
    """TC-M5-007 (R5.3, boundary): COD is rejected for an order total above 5000."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    cake_id = api_client.product_id_by_name("Chocolate Cake")  # 350.00
    api_client.post("/cart/items", token=token, json={"product_id": cake_id, "quantity": 10})  # 3500
    coffee_id = api_client.product_id_by_name("Instant Coffee")  # 250.00
    api_client.post("/cart/items", token=token, json={"product_id": coffee_id, "quantity": 7})  # +1750 = 5250
    r = api_client.post(
        "/checkout",
        token=token,
        json={
            "address": {"line1": "123 MG Road", "city": "Bengaluru", "pincode": SERVICEABLE_PINCODE},
            "slot_start": "2026-11-10T12:00:00",
            "payment": {"method": "COD"},
        },
    )
    assert r.status_code == 400
    assert "5000" in r.json()["message"]


def test_upi_invalid_format_rejected(driver):
    """TC-M5-008 (R5.3): a malformed UPI id is rejected."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    _cart_with_apple(token, 1)
    login_as(driver, CUSTOMER2["email"], CUSTOMER2["password"])

    page = CheckoutPage(driver).open()
    page.wait_visible("checkout-form")
    page.fill_address("123 MG Road", "Bengaluru", SERVICEABLE_PINCODE)
    page.select_slot_by_index(1)
    page.pay_upi("notanupi")
    page.submit()
    page.wait_visible("checkout-form-error", timeout=10)


def test_card_valid_luhn_succeeds(driver):
    """TC-M5-009 (R5.3): a syntactically valid card (passes Luhn) is accepted."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    _cart_with_apple(token, 1)
    login_as(driver, CUSTOMER2["email"], CUSTOMER2["password"])

    page = CheckoutPage(driver).open()
    page.wait_visible("checkout-form")
    page.fill_address("123 MG Road", "Bengaluru", SERVICEABLE_PINCODE)
    page.select_slot_by_index(1)
    page.pay_card("4111111111111111", "12/30", "123")
    page.submit()
    order = OrderDetailPage(driver)
    order.wait_visible("order-detail-number", timeout=10)


def test_declined_test_card_rejected(driver):
    """TC-M5-010 (R5.3): the designated always-declined test card is rejected."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    _cart_with_apple(token, 1)
    login_as(driver, CUSTOMER2["email"], CUSTOMER2["password"])

    page = CheckoutPage(driver).open()
    page.wait_visible("checkout-form")
    page.fill_address("123 MG Road", "Bengaluru", SERVICEABLE_PINCODE)
    page.select_slot_by_index(1)
    page.pay_card("4000000000000002", "12/30", "123")
    page.submit()
    assert "declined" in page.error_text().lower()


def test_expired_card_rejected(driver):
    """TC-M5-011 (R5.3, boundary): a card with a past expiry is rejected."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    _cart_with_apple(token, 1)
    r = api_client.post(
        "/checkout",
        token=token,
        json={
            "address": {"line1": "123 MG Road", "city": "Bengaluru", "pincode": SERVICEABLE_PINCODE},
            "slot_start": "2026-11-10T12:00:00",
            "payment": {"method": "CARD", "card_number": "4111111111111111", "card_expiry": "01/20", "cvv": "123"},
        },
    )
    assert r.status_code == 400
    assert "expired" in r.json()["message"].lower()


def test_successful_checkout_decrements_stock_and_clears_cart(driver):
    """TC-M5-012 (R5.4, critical): placing an order decrements stock, clears the cart,
    and returns a 4-digit OTP."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    apple_id = api_client.product_id_by_name("Apple")
    before = api_client.get(f"/catalog/products/{apple_id}").json()["stock"]
    api_client.post("/cart/items", token=token, json={"product_id": apple_id, "quantity": 2})

    r = api_client.post(
        "/checkout",
        token=token,
        json={
            "address": {"line1": "123 MG Road", "city": "Bengaluru", "pincode": SERVICEABLE_PINCODE},
            "slot_start": "2026-11-10T12:00:00",
            "payment": {"method": "COD"},
        },
    )
    assert r.status_code == 201
    order = r.json()
    assert len(order["delivery_otp"]) == 4

    after = api_client.get(f"/catalog/products/{apple_id}").json()["stock"]
    assert after == before - 2

    cart = api_client.get("/cart", token=token).json()
    assert cart["items"] == []


def test_order_number_format(driver):
    """TC-M5-013 (R5.4): order_number matches FC-YYYYMMDD-NNNN with the FIXED_NOW date."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    _cart_with_apple(token, 1)
    r = api_client.post(
        "/checkout",
        token=token,
        json={
            "address": {"line1": "123 MG Road", "city": "Bengaluru", "pincode": SERVICEABLE_PINCODE},
            "slot_start": "2026-11-10T12:00:00",
            "payment": {"method": "COD"},
        },
    )
    assert r.status_code == 201
    import re

    assert re.match(r"^FC-20261110-\d{4}$", r.json()["order_number"])


def test_checkout_empty_cart_rejected(driver):
    """TC-M5-014 (R5.4): checking out with an empty cart is rejected."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    r = api_client.post(
        "/checkout",
        token=token,
        json={
            "address": {"line1": "123 MG Road", "city": "Bengaluru", "pincode": SERVICEABLE_PINCODE},
            "slot_start": "2026-11-10T12:00:00",
            "payment": {"method": "COD"},
        },
    )
    assert r.status_code == 400
    assert "empty" in r.json()["message"].lower()
