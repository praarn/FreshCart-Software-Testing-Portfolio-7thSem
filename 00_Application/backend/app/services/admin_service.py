"""M8 admin business logic: R8.1-R8.5."""
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import BadRequestError, NotFoundError
from app.models.catalog import Category, Product
from app.models.coupon import Coupon
from app.models.enums import OrderStatus, UserStatus
from app.models.order import Order, OrderAudit, OrderItem
from app.models.user import User

# --- R8.1 product management -------------------------------------------------


async def create_product(db: AsyncSession, name: str, description: str | None, price: Decimal, stock: int, unit, category_id: int, active: bool, now: datetime) -> Product:
    category = await db.get(Category, category_id)
    if category is None:
        raise BadRequestError("Category not found.", field_errors=[{"field": "category_id", "message": "Category not found."}])
    product = Product(
        name=name, description=description, price=price, stock=stock, unit=unit,
        category_id=category_id, active=active, created_at=now, updated_at=now,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product, attribute_names=["category"])
    return product


async def update_product(db: AsyncSession, product_id: int, updates: dict, now: datetime) -> Product:
    product = await db.scalar(select(Product).options(selectinload(Product.category)).where(Product.id == product_id))
    if product is None:
        raise NotFoundError("Product not found.")
    if "category_id" in updates and updates["category_id"] is not None:
        category = await db.get(Category, updates["category_id"])
        if category is None:
            raise BadRequestError("Category not found.", field_errors=[{"field": "category_id", "message": "Category not found."}])
    for field, value in updates.items():
        if value is not None:
            setattr(product, field, value)
    product.updated_at = now
    await db.commit()
    await db.refresh(product, attribute_names=["category"])
    return product


async def update_stock(db: AsyncSession, product_id: int, stock: int, now: datetime) -> Product:
    product = await db.scalar(select(Product).options(selectinload(Product.category)).where(Product.id == product_id))
    if product is None:
        raise NotFoundError("Product not found.")
    product.stock = stock
    product.updated_at = now
    await db.commit()
    await db.refresh(product, attribute_names=["category"])
    return product


async def set_product_active(db: AsyncSession, product_id: int, active: bool, now: datetime) -> Product:
    product = await db.scalar(select(Product).options(selectinload(Product.category)).where(Product.id == product_id))
    if product is None:
        raise NotFoundError("Product not found.")
    product.active = active
    product.updated_at = now
    await db.commit()
    await db.refresh(product, attribute_names=["category"])
    return product


# --- R8.2 order management ----------------------------------------------------


async def list_orders(db: AsyncSession, status_filter: OrderStatus | None, order_date: date | None) -> list[Order]:
    query = select(Order).options(selectinload(Order.items).selectinload(OrderItem.product))
    if status_filter is not None:
        query = query.where(Order.status == status_filter)
    if order_date is not None:
        start = datetime(order_date.year, order_date.month, order_date.day)
        query = query.where(Order.created_at >= start, Order.created_at < start + timedelta(days=1))
    query = query.order_by(Order.created_at.desc())
    result = await db.scalars(query)
    return list(result.all())


# --- R8.3 coupons & users ------------------------------------------------------


async def list_coupons(db: AsyncSession) -> list[Coupon]:
    result = await db.scalars(select(Coupon).order_by(Coupon.code))
    return list(result.all())


async def set_coupon_active(db: AsyncSession, coupon_id: int, active: bool) -> Coupon:
    coupon = await db.get(Coupon, coupon_id)
    if coupon is None:
        raise NotFoundError("Coupon not found.")
    coupon.active = active
    await db.commit()
    return coupon


async def list_users(db: AsyncSession) -> list[User]:
    result = await db.scalars(select(User).order_by(User.id))
    return list(result.all())


async def lock_user(db: AsyncSession, user_id: int) -> User:
    user = await db.get(User, user_id)
    if user is None:
        raise NotFoundError("User not found.")
    user.status = UserStatus.LOCKED
    user.locked_until = None  # admin lock has no auto-expiry
    await db.commit()
    return user


async def unlock_user(db: AsyncSession, user_id: int) -> User:
    user = await db.get(User, user_id)
    if user is None:
        raise NotFoundError("User not found.")
    user.status = UserStatus.ACTIVE
    user.failed_login_count = 0
    user.locked_until = None
    await db.commit()
    return user


# --- R8.4 dashboard -------------------------------------------------------------


async def dashboard(db: AsyncSession, now: datetime) -> dict:
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)

    orders_today = await db.scalar(
        select(func.count()).select_from(Order).where(Order.created_at >= start, Order.created_at < end)
    )
    revenue_today = await db.scalar(
        select(func.coalesce(func.sum(Order.total), 0)).where(
            Order.created_at >= start, Order.created_at < end, Order.status != OrderStatus.CANCELLED
        )
    )
    low_stock = await db.scalars(select(Product).where(Product.stock < 10).order_by(Product.stock))
    return {
        "orders_today": orders_today or 0,
        "revenue_today": Decimal(revenue_today or 0),
        "low_stock_products": [{"id": p.id, "name": p.name, "stock": p.stock} for p in low_stock.all()],
    }


# --- R8.5 audit log --------------------------------------------------------------


async def list_audit_logs(db: AsyncSession, order_id: int | None, actor_id: int | None) -> list[OrderAudit]:
    query = select(OrderAudit)
    if order_id is not None:
        query = query.where(OrderAudit.order_id == order_id)
    if actor_id is not None:
        query = query.where(OrderAudit.actor_id == actor_id)
    query = query.order_by(OrderAudit.timestamp.desc())
    result = await db.scalars(query)
    return list(result.all())
