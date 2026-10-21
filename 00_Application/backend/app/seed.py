"""Idempotent seed script: `python -m app.seed`.

Creates seed users, categories, products and coupons if they don't already exist,
plus one past DELIVERED order for customer1 so R4.1's "first order only" rule has
a non-eligible customer to test against. Safe to re-run.
"""
import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select

from app.core.security import hash_password
from app.database import AsyncSessionLocal, Base, engine
from app.models import (
    Cart,
    Category,
    Coupon,
    CouponType,
    Order,
    OrderAudit,
    OrderItem,
    OrderStatus,
    PaymentMethod,
    Product,
    ProductUnit,
    Role,
    User,
)

CATEGORIES = ["Fruits", "Vegetables", "Dairy", "Bakery", "Beverages", "Snacks"]

# name, category, price, stock, unit
PRODUCTS = [
    # Fruits
    ("Apple", "Fruits", "180.00", 150, ProductUnit.kg),
    ("Banana", "Fruits", "60.00", 200, ProductUnit.kg),
    ("Orange", "Fruits", "120.00", 100, ProductUnit.kg),
    ("Mango", "Fruits", "220.00", 2, ProductUnit.kg),
    ("Grapes", "Fruits", "140.00", 80, ProductUnit.kg),
    ("Watermelon", "Fruits", "45.00", 0, ProductUnit.pc),
    # Vegetables
    ("Potato", "Vegetables", "35.00", 300, ProductUnit.kg),
    ("Onion", "Vegetables", "40.00", 250, ProductUnit.kg),
    ("Tomato", "Vegetables", "50.00", 180, ProductUnit.kg),
    ("Carrot", "Vegetables", "60.00", 120, ProductUnit.kg),
    ("Spinach", "Vegetables", "30.00", 90, ProductUnit.pack),
    ("Cauliflower", "Vegetables", "40.00", 0, ProductUnit.pc),
    # Dairy
    ("Milk", "Dairy", "58.00", 200, ProductUnit.l),
    ("Curd", "Dairy", "45.00", 150, ProductUnit.pack),
    ("Paneer", "Dairy", "90.00", 1, ProductUnit.pack),
    ("Butter", "Dairy", "55.00", 100, ProductUnit.pack),
    ("Cheese Slices", "Dairy", "120.00", 70, ProductUnit.pack),
    ("Yogurt", "Dairy", "35.00", 110, ProductUnit.pack),
    # Bakery
    ("White Bread", "Bakery", "45.00", 100, ProductUnit.pack),
    ("Burger Buns", "Bakery", "55.00", 80, ProductUnit.pack),
    ("Croissant", "Bakery", "40.00", 3, ProductUnit.pc),
    ("Chocolate Cake", "Bakery", "350.00", 15, ProductUnit.pc),
    ("Cookies", "Bakery", "90.00", 120, ProductUnit.pack),
    ("Blueberry Muffin", "Bakery", "60.00", 40, ProductUnit.pc),
    # Beverages
    ("Orange Juice", "Beverages", "110.00", 90, ProductUnit.l),
    ("Cola", "Beverages", "45.00", 200, ProductUnit.ml),
    ("Mineral Water", "Beverages", "20.00", 500, ProductUnit.l),
    ("Green Tea", "Beverages", "150.00", 60, ProductUnit.pack),
    ("Instant Coffee", "Beverages", "250.00", 70, ProductUnit.pack),
    ("Energy Drink", "Beverages", "95.00", 3, ProductUnit.ml),
    # Snacks
    ("Potato Chips", "Snacks", "20.00", 300, ProductUnit.pack),
    ("Chocolate Bar", "Snacks", "40.00", 250, ProductUnit.pc),
    ("Namkeen Mix", "Snacks", "55.00", 140, ProductUnit.pack),
    ("Popcorn", "Snacks", "35.00", 160, ProductUnit.pack),
    ("Digestive Biscuits", "Snacks", "30.00", 220, ProductUnit.pack),
    ("Granola Bar", "Snacks", "25.00", 1, ProductUnit.pc),
]

COUPONS = [
    dict(code="WELCOME10", type=CouponType.PERCENT, value=Decimal("10.00"), min_subtotal=Decimal("200.00"),
         max_discount=Decimal("100.00"), first_order_only=True, valid_weekdays=None, active=True, expires_at=None),
    dict(code="FLAT50", type=CouponType.FLAT, value=Decimal("50.00"), min_subtotal=Decimal("500.00"),
         max_discount=None, first_order_only=False, valid_weekdays=None, active=True, expires_at=None),
    dict(code="FRESH15", type=CouponType.PERCENT, value=Decimal("15.00"), min_subtotal=Decimal("800.00"),
         max_discount=Decimal("150.00"), first_order_only=False, valid_weekdays="1,2,3,4,5", active=True, expires_at=None),
    dict(code="OLD20", type=CouponType.PERCENT, value=Decimal("20.00"), min_subtotal=Decimal("0.00"),
         max_discount=None, first_order_only=False, valid_weekdays=None, active=True,
         expires_at=datetime(2020, 1, 1)),
]


async def _get_or_create_category(db, name: str) -> Category:
    cat = await db.scalar(select(Category).where(Category.name == name))
    if cat:
        return cat
    cat = Category(name=name)
    db.add(cat)
    await db.flush()
    return cat


async def _get_or_create_product(db, name: str, category: Category, price: str, stock: int, unit: ProductUnit, now: datetime):
    product = await db.scalar(select(Product).where(Product.name == name))
    if product:
        return product
    product = Product(
        name=name,
        price=Decimal(price),
        stock=stock,
        unit=unit,
        category_id=category.id,
        active=True,
        created_at=now,
        updated_at=now,
    )
    db.add(product)
    await db.flush()
    return product


async def _get_or_create_coupon(db, **kwargs):
    coupon = await db.scalar(select(Coupon).where(Coupon.code == kwargs["code"]))
    if coupon:
        return coupon
    coupon = Coupon(**kwargs)
    db.add(coupon)
    await db.flush()
    return coupon


async def _get_or_create_user(db, name: str, email: str, password: str, phone: str, role: Role, now: datetime) -> User:
    user = await db.scalar(select(User).where(User.email == email))
    if user:
        return user
    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        phone=phone,
        role=role,
        created_at=now,
        updated_at=now,
    )
    db.add(user)
    await db.flush()
    db.add(Cart(user_id=user.id))
    return user


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        admin = await _get_or_create_user(db, "Admin User", "admin@freshcart.test", "Admin@1234", "9000000001", Role.ADMIN, now)
        driver1 = await _get_or_create_user(db, "Driver One", "driver1@freshcart.test", "Driver@1234", "9000000002", Role.DELIVERY_PARTNER, now)
        await _get_or_create_user(db, "Driver Two", "driver2@freshcart.test", "Driver@1234", "9000000003", Role.DELIVERY_PARTNER, now)
        customer1 = await _get_or_create_user(db, "Customer One", "customer1@freshcart.test", "Customer@1234", "9000000004", Role.CUSTOMER, now)
        await _get_or_create_user(db, "Customer Two", "customer2@freshcart.test", "Customer@1234", "9000000005", Role.CUSTOMER, now)

        categories = {name: await _get_or_create_category(db, name) for name in CATEGORIES}

        products_by_name = {}
        for name, cat_name, price, stock, unit in PRODUCTS:
            products_by_name[name] = await _get_or_create_product(db, name, categories[cat_name], price, stock, unit, now)

        for coupon in COUPONS:
            await _get_or_create_coupon(db, **coupon)

        existing_order = await db.scalar(
            select(Order).where(Order.user_id == customer1.id, Order.status == OrderStatus.DELIVERED)
        )
        if existing_order is None:
            apple = products_by_name["Apple"]
            placed_at = now - timedelta(days=10)
            order = Order(
                order_number=f"FC-{placed_at:%Y%m%d}-0001",
                user_id=customer1.id,
                status=OrderStatus.DELIVERED,
                subtotal=Decimal("180.00"),
                discount=Decimal("0.00"),
                delivery_fee=Decimal("40.00"),
                total=Decimal("220.00"),
                coupon_code=None,
                address_line1="123 MG Road",
                address_city="Bengaluru",
                address_pincode="560001",
                slot_start=placed_at.replace(hour=10, minute=0, second=0, microsecond=0),
                slot_end=placed_at.replace(hour=12, minute=0, second=0, microsecond=0),
                payment_method=PaymentMethod.COD,
                payment_reference=None,
                delivery_otp="1234",
                delivery_partner_id=driver1.id,
                delivered_at=placed_at + timedelta(hours=3),
                created_at=placed_at,
                updated_at=placed_at + timedelta(hours=3),
            )
            db.add(order)
            await db.flush()
            db.add(OrderItem(order_id=order.id, product_id=apple.id, product_name=apple.name, unit_price=apple.price, quantity=1))

            transitions = [
                (None, OrderStatus.PLACED.value),
                (OrderStatus.PLACED.value, OrderStatus.CONFIRMED.value),
                (OrderStatus.CONFIRMED.value, OrderStatus.PACKED.value),
                (OrderStatus.PACKED.value, OrderStatus.OUT_FOR_DELIVERY.value),
                (OrderStatus.OUT_FOR_DELIVERY.value, OrderStatus.DELIVERED.value),
            ]
            for i, (frm, to) in enumerate(transitions):
                actor_id = admin.id if to != OrderStatus.DELIVERED.value else driver1.id
                actor_role = Role.ADMIN.value if to != OrderStatus.DELIVERED.value else Role.DELIVERY_PARTNER.value
                db.add(OrderAudit(
                    order_id=order.id,
                    from_state=frm,
                    to_state=to,
                    actor_id=actor_id,
                    actor_role=actor_role,
                    timestamp=placed_at + timedelta(hours=i),
                ))

        await db.commit()
    print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
