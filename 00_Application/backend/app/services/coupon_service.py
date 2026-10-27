"""Public-facing coupon listing (e.g. the homepage "Special Offers" section)."""
from datetime import datetime

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.coupon import Coupon


async def list_active_public_coupons(db: AsyncSession, now: datetime) -> list[Coupon]:
    result = await db.scalars(
        select(Coupon)
        .where(Coupon.active.is_(True), or_(Coupon.expires_at.is_(None), Coupon.expires_at > now))
        .order_by(Coupon.min_subtotal)
    )
    return list(result.all())
