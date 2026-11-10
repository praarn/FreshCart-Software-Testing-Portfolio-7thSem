"""White-box tests for app/services/checkout_service.py (R5.1-R5.3)."""
from datetime import datetime
from decimal import Decimal

import pytest

from app.core.errors import BadRequestError
from app.models.enums import OrderStatus
from app.schemas.order import AddressIn, PaymentIn
from app.services.checkout_service import _luhn_ok, _validate_address, _validate_payment, _validate_slot
from tests.unit.conftest import NOW, make_order, make_user

D = Decimal


# ---- _luhn_ok ----
@pytest.mark.parametrize("number,ok", [
    ("4111111111111111", True), ("4000000000000002", True), ("4111111111111112", False),
    ("0000000000000000", True), ("5500000000000004", True), ("4539578763621486", True),
])
def test_luhn(number, ok):
    assert _luhn_ok(number) is ok


# ---- _validate_address (R5.1) ----
@pytest.mark.parametrize("pin,ok", [("560001", True), ("560100", True), ("560050", True), ("560000", False), ("560101", False)])
def test_pincode_boundaries(pin, ok):  # TC-M5-001/002
    addr = AddressIn(line1="12 Test Road", city="Bengaluru", pincode=pin)
    if ok:
        _validate_address(addr)
    else:
        with pytest.raises(BadRequestError, match="Delivery not available"):
            _validate_address(addr)


# ---- _validate_payment (R5.3): every path ----
def pay(**kw) -> PaymentIn:
    return PaymentIn(**kw)


def test_cod_at_limit_accepted():  # TC-M5-016
    assert _validate_payment(pay(method="COD"), D("5000.00"), NOW) is None


def test_cod_over_limit_rejected():  # TC-M5-007
    with pytest.raises(BadRequestError, match="Cash on Delivery"):
        _validate_payment(pay(method="COD"), D("5000.01"), NOW)


def test_upi_returns_reference():  # TC-M5-017
    assert _validate_payment(pay(method="UPI", upi_id="jane@okbank"), D("1"), NOW) == "jane@okbank"


def test_card_declined():  # TC-M5-010
    p = pay(method="CARD", card_number="4000000000000002", card_expiry="12/30", cvv="123")
    with pytest.raises(BadRequestError, match="declined"):
        _validate_payment(p, D("1"), NOW)


def test_card_fails_luhn():  # TC-M5-018
    p = pay(method="CARD", card_number="4111111111111112", card_expiry="12/30", cvv="123")
    with pytest.raises(BadRequestError, match="Invalid card number"):
        _validate_payment(p, D("1"), NOW)


def test_card_expired_previous_month():  # TC-M5-011 boundary: October 2026 when now is November 2026
    p = pay(method="CARD", card_number="4111111111111111", card_expiry="10/26", cvv="123")
    with pytest.raises(BadRequestError, match="expired"):
        _validate_payment(p, D("1"), NOW)


def test_card_valid_in_current_month():
    p = pay(method="CARD", card_number="4111111111111111", card_expiry="11/26", cvv="123")
    assert _validate_payment(p, D("1"), NOW) == "**** **** **** 1111"


def test_card_valid_december():
    p = pay(method="CARD", card_number="4111111111111111", card_expiry="12/26", cvv="123")
    assert _validate_payment(p, D("1"), datetime(2026, 12, 31, 23, 0)) == "**** **** **** 1111"


# ---- _validate_slot (R5.2) ----
def S(day, hour):
    return datetime(2026, 11, day, hour)


async def test_slot_valid(db):
    assert await _validate_slot(db, S(10, 12), NOW) == S(10, 14)


@pytest.mark.parametrize("slot", [datetime(2026, 11, 10, 12, 30), datetime(2026, 11, 10, 12, 0, 1), S(11, 9), S(11, 20)])
async def test_slot_must_be_on_fixed_grid(db, slot):
    with pytest.raises(BadRequestError, match="Invalid delivery slot"):
        await _validate_slot(db, slot, NOW)


async def test_slot_lead_time_boundary(db):  # TC-M5-004; now = 09:00
    with pytest.raises(BadRequestError, match="at least 2 hours"):
        await _validate_slot(db, S(10, 10), NOW)       # 1 h ahead
    assert await _validate_slot(db, S(10, 12), NOW)    # 3 h ahead
    assert await _validate_slot(db, S(10, 12), datetime(2026, 11, 10, 10, 0))   # exactly now + 2 h: accepted
    with pytest.raises(BadRequestError, match="at least 2 hours"):
        await _validate_slot(db, S(10, 12), datetime(2026, 11, 10, 10, 0, 1))  # 1 s short of 2 h


async def test_slot_max_advance_boundary(db):  # TC-M5-005; now + 3 d = 13 Nov 09:00
    assert await _validate_slot(db, S(13, 8), NOW)
    with pytest.raises(BadRequestError, match="within the next 3 days"):
        await _validate_slot(db, S(13, 10), NOW)
    with pytest.raises(BadRequestError, match="within the next 3 days"):
        await _validate_slot(db, S(14, 8), NOW)


async def test_slot_capacity_5_ok_6_rejected(db):  # TC-M5-006
    user = await make_user(db)
    slot = S(11, 10)
    for i in range(4):
        await make_order(db, user.id, slot_start=slot, number=f"FC-{i}")
    assert await _validate_slot(db, slot, NOW)          # 4 existing -> 5th accepted
    await make_order(db, user.id, slot_start=slot, number="FC-4")
    with pytest.raises(BadRequestError, match="slot is full"):   # 5 existing -> 6th rejected
        await _validate_slot(db, slot, NOW)


async def test_cancelled_orders_do_not_count_toward_capacity(db):
    user = await make_user(db)
    slot = S(11, 10)
    for i in range(5):
        await make_order(db, user.id, status=OrderStatus.CANCELLED, slot_start=slot, number=f"FC-{i}")
    assert await _validate_slot(db, slot, NOW)
