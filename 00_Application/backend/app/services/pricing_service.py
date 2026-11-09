"""R4.3/R4.4 shared money math, used by the cart (M3) and later checkout (M5)."""
from decimal import ROUND_HALF_UP, Decimal

FREE_DELIVERY_THRESHOLD = Decimal("299.00")
DELIVERY_FEE = Decimal("40.00")
ZERO = Decimal("0.00")


def round2(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def compute_delivery_fee(amount_after_discount: Decimal) -> Decimal:
    """R4.3: free delivery once the post-discount subtotal reaches 299.00."""
    return ZERO if amount_after_discount >= FREE_DELIVERY_THRESHOLD else DELIVERY_FEE
