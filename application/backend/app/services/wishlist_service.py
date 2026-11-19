"""Wishlist: customer-only saved-for-later products."""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import ConflictError, NotFoundError
from app.models.catalog import Product
from app.models.user import User
from app.models.wishlist import WishlistItem


async def list_wishlist(db: AsyncSession, user: User) -> list[WishlistItem]:
    result = await db.scalars(
        select(WishlistItem)
        .options(selectinload(WishlistItem.product).selectinload(Product.category))
        .where(WishlistItem.user_id == user.id)
        .order_by(WishlistItem.created_at.desc())
    )
    return list(result.all())


async def add_to_wishlist(db: AsyncSession, user: User, product_id: int, now: datetime) -> WishlistItem:
    product = await db.get(Product, product_id)
    if product is None or not product.active:
        raise NotFoundError("Product not found.")

    existing = await db.scalar(
        select(WishlistItem).where(WishlistItem.user_id == user.id, WishlistItem.product_id == product_id)
    )
    if existing is not None:
        raise ConflictError("This product is already in your wishlist.")

    item = WishlistItem(user_id=user.id, product_id=product_id, created_at=now)
    db.add(item)
    await db.commit()
    await db.refresh(item, attribute_names=["product"])
    await db.refresh(item.product, attribute_names=["category"])
    return item


async def remove_from_wishlist(db: AsyncSession, user: User, product_id: int) -> None:
    item = await db.scalar(
        select(WishlistItem).where(WishlistItem.user_id == user.id, WishlistItem.product_id == product_id)
    )
    if item is None:
        raise NotFoundError("This product is not in your wishlist.")
    await db.delete(item)
    await db.commit()
