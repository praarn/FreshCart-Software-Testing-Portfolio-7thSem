from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin
from app.models.enums import OrderStatus, PaymentMethod


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, native_enum=False, length=20), nullable=False, default=OrderStatus.PLACED
    )

    subtotal: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    discount: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    delivery_fee: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    total: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    coupon_code: Mapped[str | None] = mapped_column(String(20), nullable=True)

    address_line1: Mapped[str] = mapped_column(String(100), nullable=False)
    address_city: Mapped[str] = mapped_column(String(50), nullable=False)
    address_pincode: Mapped[str] = mapped_column(String(6), nullable=False)

    slot_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    slot_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    payment_method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod, native_enum=False, length=10), nullable=False)
    payment_reference: Mapped[str | None] = mapped_column(String(50), nullable=True)

    delivery_otp: Mapped[str] = mapped_column(String(4), nullable=False)
    otp_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    otp_blocked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    delivery_partner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user = relationship("User", back_populates="orders", foreign_keys=[user_id])
    delivery_partner = relationship("User", foreign_keys=[delivery_partner_id])
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    audits = relationship("OrderAudit", back_populates="order", cascade="all, delete-orphan", order_by="OrderAudit.timestamp")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    product_name: Mapped[str] = mapped_column(String(80), nullable=False)
    unit_price: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")


class OrderAudit(Base):
    """R6.5 audit log: one row per status change."""

    __tablename__ = "order_audits"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    from_state: Mapped[str | None] = mapped_column(String(20), nullable=True)
    to_state: Mapped[str] = mapped_column(String(20), nullable=False)
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    actor_role: Mapped[str] = mapped_column(String(20), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    order = relationship("Order", back_populates="audits")
