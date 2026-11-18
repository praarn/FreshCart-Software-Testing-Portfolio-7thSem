"""Boundary value analysis, M5 checkout and M6 OTP attempts.

TC-M5-020 pincode range 560001..560100 (R5.1)      TC-M5-021 address line and city length (R5.1)
TC-M5-023 slot lead time, 3-day window, capacity 5 (R5.2)    TC-M5-025 COD limit 5000.00 (R5.3)
TC-M5-026 card number, CVV and expiry (R5.3)       TC-M6-019 OTP attempts, 3 allowed (R6.4)

The frozen clock is 2026-11-10 09:00. Slots start on even hours from 08:00, so the exact 2-hour
lead-time boundary (11:00) is not a slot: the nearest probes are 10:00 (1 h) and 12:00 (3 h).
"""
import pytest

import helpers
from helpers import (GOOD_ADDRESS, advance_to_out_for_delivery, call, cart_with_subtotal, checkout, place_order,
                     slot_at)


pytestmark = pytest.mark.usefixtures("clean_module")


def P(tc, label, *values):
    return pytest.param(*values, id=f"{tc}-{label}")


@pytest.fixture
def ready_cart(admin, customer1):
    cart_with_subtotal(admin, customer1, "100.00")
    return customer1


# ---- TC-M5-020: pincode range --------------------------------------------------------------
@pytest.mark.parametrize("pincode,status", [
    P("TC-M5-020", "560000-min-1", "560000", 400), P("TC-M5-020", "560001-min", "560001", 201),
    P("TC-M5-020", "560002-min+1", "560002", 201), P("TC-M5-020", "560099-max-1", "560099", 201),
    P("TC-M5-020", "560100-max", "560100", 201), P("TC-M5-020", "560101-max+1", "560101", 400),
    P("TC-M5-020", "5-digits-length-min-1", "56000", 422), P("TC-M5-020", "7-digits-length-max+1", "5600010", 422),
])
def test_pincode_boundaries(ready_cart, pincode, status):
    assert checkout(ready_cart, address={**GOOD_ADDRESS, "pincode": pincode}).status_code == status


# ---- TC-M5-021: address field lengths ------------------------------------------------------
@pytest.mark.parametrize("field,length,status", [
    P("TC-M5-021", "line1-len4-min-1", "line1", 4, 422), P("TC-M5-021", "line1-len5-min", "line1", 5, 201),
    P("TC-M5-021", "line1-len100-max", "line1", 100, 201), P("TC-M5-021", "line1-len101-max+1", "line1", 101, 422),
    P("TC-M5-021", "city-len1-min-1", "city", 1, 422), P("TC-M5-021", "city-len2-min", "city", 2, 201),
    P("TC-M5-021", "city-len50-max", "city", 50, 201), P("TC-M5-021", "city-len51-max+1", "city", 51, 422),
])
def test_address_lengths(ready_cart, field, length, status):
    r = checkout(ready_cart, address={**GOOD_ADDRESS, field: "A" * length})
    assert r.status_code == status, r.text


# ---- TC-M5-023: slot boundaries ------------------------------------------------------------
@pytest.mark.parametrize("slot,status,fragment", [
    P("TC-M5-023", "10:00-today-1h-ahead-below-lead", slot_at(0, 10), 400, "at least 2 hours"),
    P("TC-M5-023", "12:00-today-3h-ahead-above-lead", slot_at(0, 12), 201, None),
    P("TC-M5-023", "08:00-day3-71h-ahead-inside-window", slot_at(3, 8), 201, None),
    P("TC-M5-023", "10:00-day3-73h-ahead-outside-window", slot_at(3, 10), 400, "within the next 3 days"),
    P("TC-M5-023", "08:00-day4-outside-window", slot_at(4, 8), 400, "within the next 3 days"),
    P("TC-M5-023", "18:00-last-slot-of-a-day", slot_at(1, 18), 201, None),
    P("TC-M5-023", "08:00-first-slot-of-a-day", slot_at(1, 8), 201, None),
])
def test_slot_lead_time_and_window(ready_cart, slot, status, fragment):
    r = checkout(ready_cart, slot=slot)
    assert r.status_code == status, r.text
    if fragment:
        assert fragment in r.json()["message"].lower()


def test_slot_capacity_five_orders(fresh_db, admin, customer1):
    # TC-M5-023
    """The 4th and 5th order fit; the 6th is rejected; the slot list shows remaining capacity."""
    slot = slot_at(2, 14)

    def remaining():
        listing = call("GET", "/checkout/slots", customer1).json()
        return next(s for s in listing if s["slot_start"] == slot)

    assert remaining()["remaining_capacity"] == 5
    for n in range(1, 6):
        cart_with_subtotal(admin, customer1, "100.00")
        assert checkout(customer1, slot=slot).status_code == 201, f"order {n} should fit"
    assert remaining()["remaining_capacity"] == 0 and remaining()["available"] is False
    cart_with_subtotal(admin, customer1, "100.00")
    r = checkout(customer1, slot=slot)
    assert r.status_code == 400 and "full" in r.json()["message"].lower()


# ---- TC-M5-025: COD limit ------------------------------------------------------------------
@pytest.mark.parametrize("price,method,status", [
    P("TC-M5-025", "COD-4999.99-max-1", "4999.99", "COD", 201),
    P("TC-M5-025", "COD-5000.00-max", "5000.00", "COD", 201),
    P("TC-M5-025", "COD-5000.01-max+1", "5000.01", "COD", 400),
    P("TC-M5-025", "UPI-5000.01-limit-is-COD-only", "5000.01", "UPI", 201),
])
def test_cod_limit(admin, customer1, price, method, status):
    cart_with_subtotal(admin, customer1, price)
    payment = {"method": "COD"} if method == "COD" else {"method": "UPI", "upi_id": "jane@okbank"}
    r = checkout(customer1, payment=payment)
    assert r.status_code == status, r.text
    if status == 400:
        assert "cash on delivery" in r.json()["message"].lower()


# ---- TC-M5-026: card number, CVV, expiry ---------------------------------------------------
CARD = {"method": "CARD", "card_number": "4111111111111111", "card_expiry": "12/30", "cvv": "123"}


@pytest.mark.parametrize("change,status", [
    P("TC-M5-026", "number-15-digits-min-1", {"card_number": "411111111111111"}, 422),
    P("TC-M5-026", "number-16-digits-exact", {}, 201),
    P("TC-M5-026", "number-17-digits-max+1", {"card_number": "41111111111111111"}, 422),
    P("TC-M5-026", "cvv-2-digits-min-1", {"cvv": "12"}, 422),
    P("TC-M5-026", "cvv-3-digits-exact", {"cvv": "000"}, 201),
    P("TC-M5-026", "cvv-4-digits-max+1", {"cvv": "1234"}, 422),
    P("TC-M5-026", "expiry-month-00-min-1", {"card_expiry": "00/30"}, 422),
    P("TC-M5-026", "expiry-month-01-min", {"card_expiry": "01/30"}, 201),
    P("TC-M5-026", "expiry-month-12-max", {"card_expiry": "12/30"}, 201),
    P("TC-M5-026", "expiry-month-13-max+1", {"card_expiry": "13/30"}, 422),
    P("TC-M5-026", "expiry-single-digit-month", {"card_expiry": "1/30"}, 422),
    P("TC-M5-026", "expiry-10/26-month-before-now", {"card_expiry": "10/26"}, 400),
    P("TC-M5-026", "expiry-11/26-current-month", {"card_expiry": "11/26"}, 201),
    P("TC-M5-026", "expiry-12/26-month-after-now", {"card_expiry": "12/26"}, 201),
])
def test_card_boundaries(ready_cart, change, status):
    r = checkout(ready_cart, payment={**CARD, **change})
    assert r.status_code == status, r.text


# ---- TC-M6-019: OTP attempts ---------------------------------------------------------------
@pytest.fixture
def out_for_delivery(admin, driver, customer1):
    order = place_order(admin, customer1)
    advance_to_out_for_delivery(admin, driver, order["id"])
    return order


def _wrong(order):
    return "0000" if order["delivery_otp"] != "0000" else "1111"


def _deliver(driver, order, otp):
    return call("POST", f"/delivery/orders/{order['id']}/deliver", driver, json={"otp": otp})


@pytest.mark.parametrize("wrong_attempts", [
    P("TC-M6-019", "after-1-wrong", 1), P("TC-M6-019", "after-2-wrong-max-1", 2),
])
def test_correct_otp_still_works_before_the_limit(driver, out_for_delivery, wrong_attempts):
    for _ in range(wrong_attempts):
        assert _deliver(driver, out_for_delivery, _wrong(out_for_delivery)).status_code == 400
    r = _deliver(driver, out_for_delivery, out_for_delivery["delivery_otp"])
    assert r.status_code == 200 and r.json()["status"] == "DELIVERED"


def test_third_wrong_otp_blocks_even_the_correct_otp_until_admin_reset(admin, driver, out_for_delivery):
    # TC-M6-019
    assert _deliver(driver, out_for_delivery, _wrong(out_for_delivery)).status_code == 400
    assert _deliver(driver, out_for_delivery, _wrong(out_for_delivery)).status_code == 400
    third = _deliver(driver, out_for_delivery, _wrong(out_for_delivery))
    assert third.status_code == 409                                                      # max: blocked
    blocked = _deliver(driver, out_for_delivery, out_for_delivery["delivery_otp"])
    assert blocked.status_code == 409 and "reset" in blocked.json()["message"].lower()  # max+1: right OTP refused
    assert call("POST", f"/admin/orders/{out_for_delivery['id']}/reset-otp", admin).status_code == 200
    assert _deliver(driver, out_for_delivery, out_for_delivery["delivery_otp"]).status_code == 200
