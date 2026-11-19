"""M7 reviews: R7.1."""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import BadRequestError, ConflictError
from app.models.enums import OrderStatus
from app.models.order import Order, OrderItem
from app.models.review import Review
from app.models.user import User


async def create_review(db: AsyncSession, user: User, product_id: int, rating: int, comment: str | None, now: datetime) -> Review:
    delivered_order_item = await db.scalar(
        select(OrderItem)
        .join(Order, Order.id == OrderItem.order_id)
        .where(Order.user_id == user.id, Order.status == OrderStatus.DELIVERED, OrderItem.product_id == product_id)
        .limit(1)
    )
    if delivered_order_item is None:
        raise BadRequestError("You can only review products from an order that has been delivered to you.")  # R7.1

    existing = await db.scalar(select(Review).where(Review.product_id == product_id, Review.user_id == user.id))
    if existing is not None:
        raise ConflictError("You have already reviewed this product.")

    review = Review(
        product_id=product_id,
        user_id=user.id,
        order_id=delivered_order_item.order_id,
        rating=rating,
        comment=comment,
        created_at=now,
    )
    db.add(review)
    await db.commit()
    await db.refresh(review, attribute_names=["user"])
    return review


async def list_reviews_for_product(db: AsyncSession, product_id: int) -> list[Review]:
    result = await db.scalars(
        select(Review).options(selectinload(Review.user)).where(Review.product_id == product_id).order_by(Review.created_at.desc())
    )
    return list(result.all())
