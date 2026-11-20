from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class LowStockProduct(BaseModel):
    id: int
    name: str
    stock: int


class DashboardOut(BaseModel):
    orders_today: int
    revenue_today: Decimal
    low_stock_products: list[LowStockProduct]


class AuditLogOut(BaseModel):
    id: int
    order_id: int
    from_state: str | None
    to_state: str
    actor_id: int | None
    actor_role: str
    timestamp: datetime


class StockUpdateRequest(BaseModel):
    stock: int = Field(..., ge=0, le=1000)


class ActiveUpdateRequest(BaseModel):
    active: bool
