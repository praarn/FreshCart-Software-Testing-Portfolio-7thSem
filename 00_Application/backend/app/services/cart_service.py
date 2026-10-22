"""M3 cart business logic: R3.1-R3.5."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import BadRequestError, NotFoundError
from app.models.cart import Cart, CartItem
from app.models.catalog import Product
from app.models.user import User
from app.services.pricing_service import ZERO, compute_delivery_fee, round2

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


def build_cart_view(cart: Cart) -> dict:
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
    subtotal = round2(subtotal)
    discount = ZERO  # R4 coupon discount applied in M4
    after_discount = subtotal - discount
    delivery_fee = compute_delivery_fee(after_discount) if subtotal > ZERO else ZERO
    total = round2(after_discount + delivery_fee)
    return {
        "items": item_dicts,
        "coupon_code": None,
        "subtotal": subtotal,
        "discount": discount,
        "delivery_fee": delivery_fee,
        "total": total,
    }


async def get_cart(db: AsyncSession, user: User) -> dict:
    cart = await _get_or_create_cart(db, user)
    return build_cart_view(cart)


async def add_item(db: AsyncSession, user: User, product_id: int, quantity: int) -> dict:
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
    return build_cart_view(cart)


async def update_item(db: AsyncSession, user: User, item_id: int, quantity: int) -> dict:
    cart = await _get_or_create_cart(db, user)
    item = next((i for i in cart.items if i.id == item_id), None)
    if item is None:
        raise NotFoundError("Cart item not found.")
    if quantity > item.product.stock:
        raise BadRequestError(f"Only {item.product.stock} unit(s) of '{item.product.name}' are available.")
    item.quantity = quantity
    await db.commit()
    cart = await _get_or_create_cart(db, user)
    return build_cart_view(cart)


async def remove_item(db: AsyncSession, user: User, item_id: int) -> dict:
    cart = await _get_or_create_cart(db, user)
    item = next((i for i in cart.items if i.id == item_id), None)
    if item is None:
        raise NotFoundError("Cart item not found.")
    await db.delete(item)
    await db.commit()
    cart = await _get_or_create_cart(db, user)
    return build_cart_view(cart)


async def clear_cart(db: AsyncSession, user: User) -> dict:
    cart = await _get_or_create_cart(db, user)
    for item in list(cart.items):
        await db.delete(item)
    await db.commit()
    cart = await _get_or_create_cart(db, user)
    return build_cart_view(cart)
