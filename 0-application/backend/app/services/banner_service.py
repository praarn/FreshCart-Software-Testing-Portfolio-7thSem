"""Admin-managed promotional banners shown on the storefront homepage."""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.models.banner import Banner


async def list_active_banners(db: AsyncSession) -> list[Banner]:
    result = await db.scalars(
        select(Banner).where(Banner.active.is_(True)).order_by(Banner.display_order, Banner.id)
    )
    return list(result.all())


async def list_all_banners(db: AsyncSession) -> list[Banner]:
    result = await db.scalars(select(Banner).order_by(Banner.display_order, Banner.id))
    return list(result.all())


async def create_banner(db: AsyncSession, title: str, image_url: str, link_url: str | None, display_order: int, active: bool, now: datetime) -> Banner:
    banner = Banner(
        title=title, image_url=image_url, link_url=link_url, display_order=display_order,
        active=active, created_at=now, updated_at=now,
    )
    db.add(banner)
    await db.commit()
    await db.refresh(banner)
    return banner


async def update_banner(db: AsyncSession, banner_id: int, updates: dict, now: datetime) -> Banner:
    banner = await db.get(Banner, banner_id)
    if banner is None:
        raise NotFoundError("Banner not found.")
    for field, value in updates.items():
        if value is not None:
            setattr(banner, field, value)
    banner.updated_at = now
    await db.commit()
    return banner


async def delete_banner(db: AsyncSession, banner_id: int) -> None:
    banner = await db.get(Banner, banner_id)
    if banner is None:
        raise NotFoundError("Banner not found.")
    await db.delete(banner)
    await db.commit()
