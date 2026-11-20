"""Isolated in-memory SQLite database for DB-backed service tests (never touches data/freshcart.db)."""
from datetime import datetime
from decimal import Decimal

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  (register all tables on Base.metadata)
from app.database import Base
from app.models.enums import OrderStatus, PaymentMethod, Role, UserStatus
from app.models.order import Order
from app.models.user import User

NOW = datetime(2026, 11, 10, 9, 0, 0)  # Tuesday, same as FIXED_NOW in the Selenium/API runs


@pytest_asyncio.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
    async with maker() as session:
        yield session
    await engine.dispose()


async def make_user(db: AsyncSession, role=Role.CUSTOMER, email="u@x.test", password_hash="x", **kw) -> User:
    user = User(name="Test User", email=email, password_hash=password_hash, phone="9000000000", role=role,
                status=kw.pop("status", UserStatus.ACTIVE), created_at=NOW, updated_at=NOW, **kw)
    db.add(user)
    await db.commit()
    return user


async def make_order(db: AsyncSession, user_id: int, status=OrderStatus.PLACED, slot_start=NOW, number="FC-1", **kw) -> Order:
    order = Order(
        order_number=number, user_id=user_id, status=status, subtotal=Decimal("100.00"), discount=Decimal("0.00"),
        delivery_fee=Decimal("40.00"), total=Decimal("140.00"), address_line1="12 Test Road", address_city="Bengaluru",
        address_pincode="560001", slot_start=slot_start, slot_end=slot_start, payment_method=PaymentMethod.COD,
        delivery_otp=kw.pop("delivery_otp", "1234"), created_at=NOW, updated_at=NOW, **kw,
    )
    db.add(order)
    await db.commit()
    return order
