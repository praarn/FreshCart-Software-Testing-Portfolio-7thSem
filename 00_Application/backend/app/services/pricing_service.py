"""R4.1-R4.4 shared money math: cart (M3), coupons (M4) and checkout (M5)."""
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from app.core.errors import BadRequestError
from app.models.coupon import Coupon

FREE_DELIVERY_THRESHOLD = Decimal("299.00")
DELIVERY_FEE = Decimal("40.00")
ZERO = Decimal("0.00")


def round2(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def compute_delivery_fee(amount_after_discount: Decimal) -> Decimal:
    """R4.3: free delivery once the post-discount subtotal reaches 299.00."""
    return ZERO if amount_after_discount >= FREE_DELIVERY_THRESHOLD else DELIVERY_FEE


def validate_coupon(coupon: Coupon | None, code: str, subtotal: Decimal, is_first_order: bool, now: datetime) -> Coupon:
    """R4.1/R4.2: each failure case gets its own distinct message."""
    if coupon is None or not coupon.active:
        raise BadRequestError(f"'{code}' is not a valid coupon code.")
    if coupon.expires_at is not None and now > coupon.expires_at:
        raise BadRequestError(f"Coupon '{coupon.code}' has expired.")
    if subtotal < coupon.min_subtotal:
        raise BadRequestError(f"Coupon '{coupon.code}' requires a minimum order value of {coupon.min_subtotal}.")
    if coupon.first_order_only and not is_first_order:
        raise BadRequestError(f"Coupon '{coupon.code}' is valid for first-time orders only.")
    if coupon.valid_weekdays:
        allowed = {int(d) for d in coupon.valid_weekdays.split(",")}
        if now.isoweekday() not in allowed:
            raise BadRequestError(f"Coupon '{coupon.code}' is only valid Monday to Friday.")
    return coupon


def compute_discount(coupon: Coupon, subtotal: Decimal) -> Decimal:
    if coupon.type.value == "FLAT":
        raw = coupon.value
    else:  # PERCENT
        raw = subtotal * coupon.value / Decimal("100")
    if coupon.max_discount is not None:
        raw = min(raw, coupon.max_discount)
    return round2(min(raw, subtotal))
