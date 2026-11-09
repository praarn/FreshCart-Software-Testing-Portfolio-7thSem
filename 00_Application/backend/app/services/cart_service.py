"""M3 cart business logic (R3.1-R3.5) plus M4 coupon application (R4.1-R4.2)."""
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import BadRequestError, NotFoundError
from app.models.cart import Cart, CartItem
from app.models.catalog import Product
from app.models.coupon import Coupon
from app.models.order import Order
from app.models.user import User
from app.services.pricing_service import ZERO, compute_delivery_fee, compute_discount, round2, validate_coupon

MAX_DISTINCT_ITEMS = 20
MAX_QTY_PER_ITEM = 10


async def _get_or_create_cart(db: AsyncSession, user: User) -> Cart:
    cart = await db.scalar(
        select(Cart)
        .options(selectinload(Cart.items).selectinload(CartItem.product))
        .where(Cart.user_id == user.id)
        .execution_options(populate_existing=True)
    )
    if cart is None:
        cart = Cart(user_id=user.id)
        db.add(cart)
        await db.flush()
        await db.refresh(cart, attribute_names=["items"])
    return cart


async def is_first_order(db: AsyncSession, user: User) -> bool:
    count = await db.scalar(select(func.count()).select_from(Order).where(Order.user_id == user.id))
    return (count or 0) == 0


def _item_totals(cart: Cart) -> tuple[list[dict], "Decimal"]:  # noqa: F821
    item_dicts = []
    subtotal = ZERO
    for item in cart.items:
        line_total = round2(item.product.price * item.quantity)
        subtotal += line_total
        item_dicts.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": item.product.name,
            "unit": item.product.unit,
            "unit_price": item.product.price,
            "quantity": item.quantity,
            "stock": item.product.stock,
            "line_total": line_total,
        })
    return item_dicts, round2(subtotal)


async def _cart_view(db: AsyncSession, user: User, cart: Cart, now: datetime) -> dict:
    item_dicts, subtotal = _item_totals(cart)

    discount = ZERO
    coupon_code = cart.coupon_code
    if coupon_code:
        coupon = await db.scalar(select(Coupon).where(Coupon.code == coupon_code))
        try:
            first_order = await is_first_order(db, user)
            validate_coupon(coupon, coupon_code, subtotal, first_order, now)
            discount = compute_discount(coupon, subtotal)
        except BadRequestError:
            # The coupon no longer applies (e.g. cart total dropped, or day changed) -> drop it silently.
            cart.coupon_code = None
            coupon_code = None
            await db.commit()

    after_discount = subtotal - discount
    delivery_fee = compute_delivery_fee(after_discount) if subtotal > ZERO else ZERO
    total = round2(after_discount + delivery_fee)
    return {
        "items": item_dicts,
        "coupon_code": coupon_code,
        "subtotal": subtotal,
        "discount": discount,
        "delivery_fee": delivery_fee,
        "total": total,
    }


async def get_cart(db: AsyncSession, user: User, now: datetime) -> dict:
    cart = await _get_or_create_cart(db, user)
    return await _cart_view(db, user, cart, now)


async def add_item(db: AsyncSession, user: User, product_id: int, quantity: int, now: datetime) -> dict:
    product = await db.get(Product, product_id)
    if product is None or not product.active:
        raise NotFoundError("Product not found.")
    if product.stock == 0:
        raise BadRequestError("This product is out of stock.")  # R2.4
    if quantity > product.stock:
        raise BadRequestError(f"Only {product.stock} unit(s) of '{product.name}' are available.")

    cart = await _get_or_create_cart(db, user)
    existing = next((i for i in cart.items if i.product_id == product_id), None)

    if existing:
        new_qty = existing.quantity + quantity
        if new_qty > MAX_QTY_PER_ITEM:
            raise BadRequestError(f"Quantity per item cannot exceed {MAX_QTY_PER_ITEM}.")  # R3.1/R3.3
        if new_qty > product.stock:
            raise BadRequestError(f"Only {product.stock} unit(s) of '{product.name}' are available.")
        existing.quantity = new_qty
    else:
        if len(cart.items) >= MAX_DISTINCT_ITEMS:
            raise BadRequestError(f"Cart can contain at most {MAX_DISTINCT_ITEMS} distinct items.")  # R3.2
        db.add(CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity))

    await db.commit()
    cart = await _get_or_create_cart(db, user)
    return await _cart_view(db, user, cart, now)


async def update_item(db: AsyncSession, user: User, item_id: int, quantity: int, now: datetime) -> dict:
    cart = await _get_or_create_cart(db, user)
    item = next((i for i in cart.items if i.id == item_id), None)
    if item is None:
        raise NotFoundError("Cart item not found.")
    if quantity > item.product.stock:
        raise BadRequestError(f"Only {item.product.stock} unit(s) of '{item.product.name}' are available.")
    item.quantity = quantity
    await db.commit()
    cart = await _get_or_create_cart(db, user)
    return await _cart_view(db, user, cart, now)


async def remove_item(db: AsyncSession, user: User, item_id: int, now: datetime) -> dict:
    cart = await _get_or_create_cart(db, user)
    item = next((i for i in cart.items if i.id == item_id), None)
    if item is None:
        raise NotFoundError("Cart item not found.")
    await db.delete(item)
    await db.commit()
    cart = await _get_or_create_cart(db, user)
    return await _cart_view(db, user, cart, now)


async def clear_cart(db: AsyncSession, user: User, now: datetime) -> dict:
    cart = await _get_or_create_cart(db, user)
    for item in list(cart.items):
        await db.delete(item)
    cart.coupon_code = None
    await db.commit()
    cart = await _get_or_create_cart(db, user)
    return await _cart_view(db, user, cart, now)


async def apply_coupon(db: AsyncSession, user: User, code: str, now: datetime) -> dict:
    code = code.strip().upper()
    cart = await _get_or_create_cart(db, user)
    _items, subtotal = _item_totals(cart)
    if subtotal <= ZERO:
        raise BadRequestError("Your cart is empty.")

    coupon = await db.scalar(select(Coupon).where(Coupon.code == code))
    first_order = await is_first_order(db, user)
    validate_coupon(coupon, code, subtotal, first_order, now)  # R4.1/R4.2

    cart.coupon_code = coupon.code
    await db.commit()
    cart = await _get_or_create_cart(db, user)
    return await _cart_view(db, user, cart, now)


async def remove_coupon(db: AsyncSession, user: User, now: datetime) -> dict:
    cart = await _get_or_create_cart(db, user)
    cart.coupon_code = None
    await db.commit()
    cart = await _get_or_create_cart(db, user)
    return await _cart_view(db, user, cart, now)
