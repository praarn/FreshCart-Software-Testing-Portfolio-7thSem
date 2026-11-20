"""M5 checkout: R5.1-R5.5."""
import random
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import BadRequestError, ConflictError
from app.models.cart import Cart, CartItem
from app.models.coupon import Coupon
from app.models.enums import OrderStatus, PaymentMethod, Role
from app.models.order import Order, OrderAudit, OrderItem
from app.models.user import User
from app.schemas.order import AddressIn, PaymentIn
from app.services.cart_service import is_first_order
from app.services.pricing_service import ZERO, compute_delivery_fee, compute_discount, round2, validate_coupon

SERVICEABLE_PINCODE_MIN = 560001
SERVICEABLE_PINCODE_MAX = 560100
SLOT_START_HOURS = [8, 10, 12, 14, 16, 18]
SLOT_LENGTH_HOURS = 2
MIN_LEAD_TIME = timedelta(hours=2)
MAX_ADVANCE = timedelta(days=3)
MAX_ORDERS_PER_SLOT = 5
COD_LIMIT = Decimal("5000.00")
DECLINED_TEST_CARD = "4000000000000002"


def _validate_address(address: AddressIn) -> None:
    pincode = int(address.pincode)
    if not (SERVICEABLE_PINCODE_MIN <= pincode <= SERVICEABLE_PINCODE_MAX):
        raise BadRequestError("Delivery not available for this pincode.")  # R5.1


async def _validate_slot(db: AsyncSession, slot_start: datetime, now: datetime) -> datetime:
    if slot_start.minute != 0 or slot_start.second != 0 or slot_start.microsecond != 0 or slot_start.hour not in SLOT_START_HOURS:
        raise BadRequestError("Invalid delivery slot. Choose one of the fixed 2-hour slots between 08:00 and 20:00.")
    if slot_start < now + MIN_LEAD_TIME:
        raise BadRequestError("Delivery slot must start at least 2 hours from now.")
    if slot_start > now + MAX_ADVANCE:
        raise BadRequestError("Delivery slot must be within the next 3 days.")

    slot_end = slot_start + timedelta(hours=SLOT_LENGTH_HOURS)
    count = await db.scalar(
        select(func.count()).select_from(Order).where(Order.slot_start == slot_start, Order.status != OrderStatus.CANCELLED)
    )
    if (count or 0) >= MAX_ORDERS_PER_SLOT:
        raise BadRequestError("This delivery slot is full. Please choose another slot.")  # R5.2
    return slot_end


def _luhn_ok(card_number: str) -> bool:
    digits = [int(d) for d in card_number]
    checksum = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


def _validate_payment(payment: PaymentIn, total: Decimal, now: datetime) -> str | None:
    """R5.3. Returns a payment_reference to store, or raises on rejection."""
    if payment.method == PaymentMethod.COD:
        if total > COD_LIMIT:
            raise BadRequestError(f"Cash on Delivery is only available for orders up to {COD_LIMIT}.")
        return None

    if payment.method == PaymentMethod.UPI:
        return payment.upi_id

    # CARD
    if payment.card_number == DECLINED_TEST_CARD:
        raise BadRequestError("Card declined. Please try a different payment method.")
    if not _luhn_ok(payment.card_number):
        raise BadRequestError("Invalid card number.")
    month_str, year_str = payment.card_expiry.split("/")
    month, year = int(month_str), 2000 + int(year_str)
    expiry_end = datetime(year, month, 1) + timedelta(days=31)
    if expiry_end.replace(day=1) <= now.replace(day=1, hour=0, minute=0, second=0, microsecond=0):
        raise BadRequestError("Card has expired.")
    return f"**** **** **** {payment.card_number[-4:]}"


async def _generate_order_number(db: AsyncSession, now: datetime) -> str:
    prefix = f"FC-{now:%Y%m%d}-"
    count = await db.scalar(select(func.count()).select_from(Order).where(Order.order_number.like(f"{prefix}%")))
    return f"{prefix}{(count or 0) + 1:04d}"


async def list_available_slots(db: AsyncSession, now: datetime) -> list[dict]:
    """Helper for the frontend's slot picker; mirrors the R5.2 rules."""
    slots = []
    day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    for day_offset in range(0, 4):
        for hour in SLOT_START_HOURS:
            slot_start = day.replace(hour=hour) + timedelta(days=day_offset)
            if slot_start < now + MIN_LEAD_TIME or slot_start > now + MAX_ADVANCE:
                continue
            slot_end = slot_start + timedelta(hours=SLOT_LENGTH_HOURS)
            count = await db.scalar(
                select(func.count()).select_from(Order).where(Order.slot_start == slot_start, Order.status != OrderStatus.CANCELLED)
            )
            remaining = MAX_ORDERS_PER_SLOT - (count or 0)
            slots.append({
                "slot_start": slot_start,
                "slot_end": slot_end,
                "available": remaining > 0,
                "remaining_capacity": max(0, remaining),
            })
    return slots


async def checkout(db: AsyncSession, user: User, now: datetime, address: AddressIn, slot_start: datetime, payment: PaymentIn) -> Order:
    cart = await db.scalar(
        select(Cart)
        .options(selectinload(Cart.items).selectinload(CartItem.product))
        .where(Cart.user_id == user.id)
        .execution_options(populate_existing=True)
    )
    if cart is None or not cart.items:
        raise BadRequestError("Your cart is empty.")  # R5.4

    _validate_address(address)
    slot_end = await _validate_slot(db, slot_start, now)

    # R5.4/R5.5: re-validate stock/prices now, before mutating anything.
    for item in cart.items:
        product = item.product
        if not product.active or item.quantity > product.stock:
            raise ConflictError(f"'{product.name}' is no longer available in the requested quantity.")

    subtotal = round2(sum((item.product.price * item.quantity for item in cart.items), ZERO))

    discount = ZERO
    coupon_code = None
    if cart.coupon_code:
        coupon = await db.scalar(select(Coupon).where(Coupon.code == cart.coupon_code))
        first_order = await is_first_order(db, user)
        validate_coupon(coupon, cart.coupon_code, subtotal, first_order, now)
        discount = compute_discount(coupon, subtotal)
        coupon_code = coupon.code

    after_discount = subtotal - discount
    delivery_fee = compute_delivery_fee(after_discount)
    total = round2(after_discount + delivery_fee)

    payment_reference = _validate_payment(payment, total, now)

    for item in cart.items:
        item.product.stock -= item.quantity

    order_number = await _generate_order_number(db, now)
    delivery_otp = f"{random.randint(0, 9999):04d}"

    order = Order(
        order_number=order_number,
        user_id=user.id,
        status=OrderStatus.PLACED,
        subtotal=subtotal,
        discount=discount,
        delivery_fee=delivery_fee,
        total=total,
        coupon_code=coupon_code,
        address_line1=address.line1,
        address_city=address.city,
        address_pincode=address.pincode,
        slot_start=slot_start,
        slot_end=slot_end,
        payment_method=payment.method,
        payment_reference=payment_reference,
        delivery_otp=delivery_otp,
        created_at=now,
        updated_at=now,
    )
    db.add(order)
    await db.flush()

    for item in cart.items:
        db.add(OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            product_name=item.product.name,
            unit_price=item.product.price,
            quantity=item.quantity,
        ))

    db.add(OrderAudit(
        order_id=order.id, from_state=None, to_state=OrderStatus.PLACED.value,
        actor_id=user.id, actor_role=Role.CUSTOMER.value, timestamp=now,
    ))

    for item in list(cart.items):
        await db.delete(item)
    cart.coupon_code = None

    await db.commit()
    order = await db.scalar(
        select(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
        .where(Order.id == order.id)
        .execution_options(populate_existing=True)
    )
    return order
