"""M2 catalog business logic: search/filter/sort/pagination, R2.4 visibility rules."""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import NotFoundError
from app.models.catalog import Category, Product
from app.models.review import Review

PAGE_SIZE = 10


async def list_categories(db: AsyncSession) -> list[Category]:
    result = await db.scalars(select(Category).order_by(Category.name))
    return list(result.all())


async def _avg_ratings(db: AsyncSession, product_ids: list[int]) -> dict[int, float]:
    if not product_ids:
        return {}
    rows = await db.execute(
        select(Review.product_id, func.avg(Review.rating)).where(Review.product_id.in_(product_ids)).group_by(Review.product_id)
    )
    return {pid: round(float(avg), 1) for pid, avg in rows.all()}


def to_product_dict(product: Product, avg_rating: float | None) -> dict:
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "unit": product.unit,
        "category_id": product.category_id,
        "category_name": product.category.name,
        "active": product.active,
        "avg_rating": avg_rating,
    }


async def list_products(
    db: AsyncSession,
    search: str | None,
    category_id: int | None,
    sort: str | None,
    page: int,
    include_inactive: bool = False,
) -> tuple[list[dict], int]:
    filters = select(Product.id)
    if not include_inactive:
        filters = filters.where(Product.active.is_(True))
    if search:
        filters = filters.where(func.lower(Product.name).like(f"%{search.strip().lower()}%"))
    if category_id is not None:
        filters = filters.where(Product.category_id == category_id)

    total = await db.scalar(select(func.count()).select_from(filters.subquery()))

    base = select(Product).options(selectinload(Product.category)).where(Product.id.in_(filters))
    if sort == "price_asc":
        base = base.order_by(Product.price.asc(), Product.id.asc())
    elif sort == "price_desc":
        base = base.order_by(Product.price.desc(), Product.id.asc())
    else:
        base = base.order_by(Product.id.asc())

    page = max(1, page)
    base = base.offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE)

    result = await db.scalars(base)
    products = list(result.all())

    ratings = await _avg_ratings(db, [p.id for p in products])
    items = [to_product_dict(p, ratings.get(p.id)) for p in products]
    return items, total or 0


async def get_product(db: AsyncSession, product_id: int, include_inactive: bool = False) -> dict:
    product = await db.scalar(
        select(Product).options(selectinload(Product.category)).where(Product.id == product_id)
    )
    if product is None or (not include_inactive and not product.active):
        raise NotFoundError("Product not found.")
    ratings = await _avg_ratings(db, [product.id])
    return to_product_dict(product, ratings.get(product.id))
