from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import CouponType


class Coupon(Base):
    """R4.1/R4.2 coupon rules. `valid_weekdays` is a comma-separated list of ISO weekdays
    (1=Mon .. 7=Sun) on which the coupon may be applied; null/empty means every day."""

    __tablename__ = "coupons"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    type: Mapped[CouponType] = mapped_column(Enum(CouponType, native_enum=False, length=10), nullable=False)
    value: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    min_subtotal: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    max_discount: Mapped[Numeric | None] = mapped_column(Numeric(10, 2), nullable=True)
    first_order_only: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    valid_weekdays: Mapped[str | None] = mapped_column(String(20), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
