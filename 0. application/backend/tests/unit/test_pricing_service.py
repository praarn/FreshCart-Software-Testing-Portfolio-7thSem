"""White-box tests for app/services/pricing_service.py (R4.1-R4.4).
Branch and condition coverage targets are annotated; see 6. white-box-testing/Basis_Path_Testing.md.

White-box method 1, basis path testing: TC-M4-022 (validate_coupon, V(G) = 10, one test per path).
White-box method 2, statement/branch/condition coverage: TC-M4-023 (validate_coupon, compute_discount, compute_delivery_fee)."""
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from app.core.errors import BadRequestError
from app.models.coupon import Coupon
from app.models.enums import CouponType
from app.services.pricing_service import compute_delivery_fee, compute_discount, round2, validate_coupon

TUE = datetime(2026, 11, 10, 9, 0)
SAT = datetime(2026, 11, 14, 9, 0)
D = Decimal


def coupon(**kw) -> Coupon:
    base = dict(code="TEST", type=CouponType.PERCENT, value=D("10.00"), min_subtotal=D("200.00"),
                max_discount=None, first_order_only=False, valid_weekdays=None, active=True, expires_at=None)
    base.update(kw)
    return Coupon(**base)


# ---- round2 / compute_delivery_fee (R4.3, R4.4) ----
@pytest.mark.parametrize("raw,expected", [("0.005", "0.01"), ("0.004", "0.00"), ("2.675", "2.68"), ("10", "10.00")])
def test_round2_half_up(raw, expected):  # TC-M4-012
    assert round2(D(raw)) == D(expected)


@pytest.mark.parametrize("amount,fee", [("0.00", "40.00"), ("298.99", "40.00"), ("299.00", "0.00"), ("299.01", "0.00"), ("5000", "0.00")])
def test_delivery_fee_boundary(amount, fee):  # TC-M4-013, TC-M4-014
    assert compute_delivery_fee(D(amount)) == D(fee)


# ---- validate_coupon: one test per path / condition outcome ----
def test_unknown_coupon_none():  # line 24: A=T
    with pytest.raises(BadRequestError, match="not a valid coupon code"):
        validate_coupon(None, "NOPE", D("500"), True, TUE)


def test_disabled_coupon():  # line 24: A=F, B=T  (condition coverage)
    with pytest.raises(BadRequestError, match="not a valid coupon code"):
        validate_coupon(coupon(active=False), "TEST", D("500"), True, TUE)


def test_expired_coupon():  # line 26: C1=T, C2=T
    with pytest.raises(BadRequestError, match="has expired"):
        validate_coupon(coupon(expires_at=TUE - timedelta(seconds=1)), "TEST", D("500"), True, TUE)


def test_coupon_valid_at_expiry_instant():  # C1=T, C2=F (now == expires_at is still valid)
    assert validate_coupon(coupon(expires_at=TUE), "TEST", D("500"), True, TUE)


def test_below_minimum():  # line 28 TRUE; TC-M4-003
    with pytest.raises(BadRequestError, match="minimum order value"):
        validate_coupon(coupon(), "TEST", D("199.99"), True, TUE)


def test_exactly_minimum_is_accepted():  # line 28 FALSE at the boundary
    assert validate_coupon(coupon(), "TEST", D("200.00"), True, TUE)


def test_first_order_violation():  # line 30: P=T, Q=T; TC-M4-004
    with pytest.raises(BadRequestError, match="first-time orders only"):
        validate_coupon(coupon(first_order_only=True), "TEST", D("500"), False, TUE)


def test_first_order_coupon_for_first_order_customer():  # P=T, Q=F
    assert validate_coupon(coupon(first_order_only=True), "TEST", D("500"), True, TUE)


def test_non_first_order_coupon_for_returning_customer():  # P=F
    assert validate_coupon(coupon(first_order_only=False), "TEST", D("500"), False, TUE)


def test_weekday_rejected_on_saturday():  # line 34 TRUE; TC-M4-015
    with pytest.raises(BadRequestError, match="Monday to Friday"):
        validate_coupon(coupon(valid_weekdays="1,2,3,4,5"), "TEST", D("500"), True, SAT)


def test_weekday_accepted_on_tuesday():  # line 32 TRUE, line 34 FALSE
    assert validate_coupon(coupon(valid_weekdays="1,2,3,4,5"), "TEST", D("500"), True, TUE)


def test_no_weekday_limit_accepts_saturday():  # line 32 FALSE
    assert validate_coupon(coupon(valid_weekdays=None), "TEST", D("500"), True, SAT)


def test_precedence_minimum_before_first_order():  # TC-M4-016
    with pytest.raises(BadRequestError, match="minimum order value"):
        validate_coupon(coupon(first_order_only=True), "TEST", D("100"), False, TUE)


def test_precedence_expired_before_minimum():
    with pytest.raises(BadRequestError, match="has expired"):
        validate_coupon(coupon(expires_at=TUE - timedelta(days=1)), "TEST", D("1"), True, TUE)


# ---- compute_discount ----
def test_flat_discount():
    assert compute_discount(coupon(type=CouponType.FLAT, value=D("50.00")), D("500")) == D("50.00")


def test_flat_discount_never_exceeds_subtotal():  # min(raw, subtotal)
    assert compute_discount(coupon(type=CouponType.FLAT, value=D("50.00")), D("30")) == D("30.00")


def test_percent_discount():
    assert compute_discount(coupon(), D("300")) == D("30.00")


def test_percent_discount_capped():  # TC-M4-002
    assert compute_discount(coupon(max_discount=D("100.00")), D("2000")) == D("100.00")


def test_percent_discount_below_cap_not_raised():  # max_discount present but not binding
    assert compute_discount(coupon(max_discount=D("100.00")), D("500")) == D("50.00")


def test_percent_discount_rounds_half_up():  # TC-M4-012: 10% of 0.05 = 0.005 -> 0.01
    assert compute_discount(coupon(), D("0.05")) == D("0.01")
