from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.enums import CouponType


class ApplyCouponRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"code": "WELCOME10"}})

    code: str


class CouponOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    type: CouponType
    value: Decimal
    min_subtotal: Decimal
    max_discount: Decimal | None
    first_order_only: bool
    valid_weekdays: str | None
    active: bool
    expires_at: datetime | None


class CouponUpdate(BaseModel):
    active: bool


class PublicCouponOut(BaseModel):
    """Minimal coupon info surfaced to customers (e.g. the homepage offers section)."""

    model_config = ConfigDict(from_attributes=True)

    code: str
    type: CouponType
    value: Decimal
    min_subtotal: Decimal
    max_discount: Decimal | None
    first_order_only: bool
