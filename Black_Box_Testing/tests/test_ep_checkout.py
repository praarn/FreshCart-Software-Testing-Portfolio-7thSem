"""Equivalence partitioning, M5 checkout and M6 delivery OTP.

TC-M5-019 pincode classes (R5.1)     TC-M5-022 delivery slot classes (R5.2)
TC-M5-024 payment method classes (R5.3)     TC-M5-027 checkout precondition and effect classes (R5.4, R5.5)
TC-M6-018 delivery OTP classes (R6.4)
"""
from decimal import Decimal

import pytest

import helpers
from helpers import (GOOD_ADDRESS, add_to_cart, advance_to_out_for_delivery, call, cart_with_subtotal, checkout,
                     clear_cart, make_product, place_order, slot_at)


pytestmark = pytest.mark.usefixtures("clean_module")


def P(tc, cls, *values):
    return pytest.param(*values, id=f"{tc}-{cls}")


@pytest.fixture
def ready_cart(admin, customer1):
    """customer1 with a single 100.00 item in the cart (so total 140.00, COD allowed)."""
    cart_with_subtotal(admin, customer1, "100.00")
    return customer1


# ---- TC-M5-019: pincode --------------------------------------------------------------------
@pytest.mark.parametrize("pincode,status,fragment", [
    P("TC-M5-019", "EP1-serviceable", "560050", 201, None),
    P("TC-M5-019", "EP2-six-digits-above-range", "560101", 400, "delivery not available"),
    P("TC-M5-019", "EP3-six-digits-below-range", "560000", 400, "delivery not available"),
    P("TC-M5-019", "EP4-too-short", "5600", 422, None),
    P("TC-M5-019", "EP5-too-long", "5600500", 422, None),
    P("TC-M5-019", "EP6-non-digit", "56005a", 422, None),
    P("TC-M5-019", "EP7-empty", "", 422, None),
])
def test_pincode_classes(ready_cart, pincode, status, fragment):
    r = checkout(ready_cart, address={**GOOD_ADDRESS, "pincode": pincode})
    assert r.status_code == status, r.text
    if fragment:
        assert fragment in r.json()["message"].lower()


# ---- TC-M5-022: delivery slot --------------------------------------------------------------
@pytest.mark.parametrize("slot,status,fragment", [
    P("TC-M5-022", "EP1-valid-grid-slot-3h-ahead", slot_at(0, 12), 201, None),
    P("TC-M5-022", "EP2-minutes-off-grid", slot_at(1, 12, 30), 400, "invalid delivery slot"),
    P("TC-M5-022", "EP3-hour-after-last-slot", slot_at(1, 20), 400, "invalid delivery slot"),
    P("TC-M5-022", "EP4-hour-before-first-slot", slot_at(1, 6), 400, "invalid delivery slot"),
    P("TC-M5-022", "EP5-starts-too-soon", slot_at(0, 10), 400, "at least 2 hours"),
    P("TC-M5-022", "EP6-in-the-past", slot_at(-1, 12), 400, "at least 2 hours"),
    P("TC-M5-022", "EP7-too-far-ahead", slot_at(5, 12), 400, "within the next 3 days"),
])
def test_slot_classes(ready_cart, slot, status, fragment):
    r = checkout(ready_cart, slot=slot)
    assert r.status_code == status, r.text
    if fragment:
        assert fragment in r.json()["message"].lower()


def test_slot_must_be_a_real_datetime(ready_cart):
    r = checkout(ready_cart, slot="tomorrow-morning")      # TC-M5-022 EP8
    assert r.status_code == 422


# ---- TC-M5-024: payment --------------------------------------------------------------------
GOOD_CARD = {"method": "CARD", "card_number": "4111111111111111", "card_expiry": "12/30", "cvv": "123"}


@pytest.mark.parametrize("payment,status,fragment", [
    P("TC-M5-024", "EP1-cod-within-limit", {"method": "COD"}, 201, None),
    P("TC-M5-024", "EP2-upi-valid", {"method": "UPI", "upi_id": "jane@okbank"}, 201, None),
    P("TC-M5-024", "EP3-upi-bad-format", {"method": "UPI", "upi_id": "notanupi"}, 422, None),
    P("TC-M5-024", "EP4-upi-missing-id", {"method": "UPI"}, 422, None),
    P("TC-M5-024", "EP5-card-valid", GOOD_CARD, 201, None),
    P("TC-M5-024", "EP6-card-always-declined", {**GOOD_CARD, "card_number": "4000000000000002"}, 400, "declined"),
    P("TC-M5-024", "EP7-card-expired", {**GOOD_CARD, "card_expiry": "01/20"}, 400, "expired"),
    P("TC-M5-024", "EP8-card-fails-luhn", {**GOOD_CARD, "card_number": "4111111111111112"}, 400, "invalid card number"),
    P("TC-M5-024", "EP9-card-non-digits", {**GOOD_CARD, "card_number": "4111-1111-1111-11"}, 422, None),
    P("TC-M5-024", "EP10-card-missing-cvv", {k: v for k, v in GOOD_CARD.items() if k != "cvv"}, 422, None),
    P("TC-M5-024", "EP11-unknown-method", {"method": "BITCOIN"}, 422, None),
])
def test_payment_classes(ready_cart, payment, status, fragment):
    r = checkout(ready_cart, payment=payment)
    assert r.status_code == status, r.text
    if fragment:
        assert fragment in r.json()["message"].lower()
    if status == 201 and payment["method"] == "CARD":
        assert r.json()["payment_reference"] == "**** **** **** 1111"      # full number never echoed
    if status == 201 and payment["method"] == "UPI":
        assert r.json()["payment_reference"] == "jane@okbank"


# ---- TC-M5-027: precondition and effect classes --------------------------------------------
def test_empty_cart_cannot_check_out(customer1):
    # TC-M5-027
    clear_cart(customer1)
    r = checkout(customer1)
    assert r.status_code == 400 and "empty" in r.json()["message"].lower()


def test_successful_checkout_effects(admin, customer1):
    # TC-M5-027
    pid = make_product(admin, price="150.00", stock=10)
    clear_cart(customer1)
    add_to_cart(customer1, pid, 2)
    order = checkout(customer1)
    assert order.status_code == 201
    body = order.json()
    assert body["status"] == "PLACED" and Decimal(body["subtotal"]) == Decimal("300.00")
    assert body["order_number"].startswith("FC-20261110-") and len(body["delivery_otp"]) == 4
    assert call("GET", f"/catalog/products/{pid}").json()["stock"] == 8             # stock decremented
    assert call("GET", "/cart", customer1).json()["items"] == []                      # cart cleared


def test_failed_checkout_changes_nothing(admin, customer1):
    # TC-M5-027
    pid = make_product(admin, price="150.00", stock=10)
    clear_cart(customer1)
    add_to_cart(customer1, pid, 2)
    assert checkout(customer1, address={**GOOD_ADDRESS, "pincode": "560101"}).status_code == 400
    assert call("GET", f"/catalog/products/{pid}").json()["stock"] == 10
    assert len(call("GET", "/cart", customer1).json()["items"]) == 1


def test_line_that_became_unavailable_blocks_the_whole_order(admin, customer1):
    # TC-M5-027
    ok, gone = make_product(admin, stock=10), make_product(admin, stock=10)
    clear_cart(customer1)
    add_to_cart(customer1, ok, 1)
    add_to_cart(customer1, gone, 1)
    assert call("PATCH", f"/admin/products/{gone}/active", admin, json={"active": False}).status_code == 200
    r = checkout(customer1)
    assert r.status_code == 409
    assert call("GET", f"/catalog/products/{ok}").json()["stock"] == 10              # nothing partially committed


# ---- TC-M6-018: delivery OTP ---------------------------------------------------------------
@pytest.fixture
def out_for_delivery(admin, driver, customer1):
    order = place_order(admin, customer1)
    advance_to_out_for_delivery(admin, driver, order["id"])
    return order


def deliver(driver, order, otp):
    return call("POST", f"/delivery/orders/{order['id']}/deliver", driver, json={"otp": otp})


def wrong_otp(order):
    return "0000" if order["delivery_otp"] != "0000" else "1111"


def test_correct_otp_delivers(driver, out_for_delivery):
    r = deliver(driver, out_for_delivery, out_for_delivery["delivery_otp"])
    assert r.status_code == 200 and r.json()["status"] == "DELIVERED"      # TC-M6-018 EP1


def test_wrong_four_digit_otp_is_refused(driver, out_for_delivery):
    # TC-M6-018
    r = deliver(driver, out_for_delivery, wrong_otp(out_for_delivery))
    assert r.status_code == 400 and "incorrect otp" in r.json()["message"].lower()    # EP2


@pytest.mark.parametrize("otp", [
    P("TC-M6-018", "EP3-too-short", "123"), P("TC-M6-018", "EP4-too-long", "12345"), P("TC-M6-018", "EP5-empty", ""),
])
def test_malformed_otp_is_a_validation_error(driver, out_for_delivery, otp):
    assert deliver(driver, out_for_delivery, otp).status_code == 422


def test_non_numeric_four_character_otp_counts_as_wrong(driver, out_for_delivery):
    # TC-M6-018
    assert deliver(driver, out_for_delivery, "abcd").status_code == 400           # EP6


def test_order_not_assigned_to_this_driver_or_not_dispatched(admin, driver, customer1):
    # TC-M6-018
    order = place_order(admin, customer1)                                         # still PLACED, unassigned
    assert deliver(driver, order, order["delivery_otp"]).status_code in (403, 409)   # EP7
