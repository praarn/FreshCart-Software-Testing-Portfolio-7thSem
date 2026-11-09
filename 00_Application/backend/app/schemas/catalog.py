from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ProductUnit


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, json_schema_extra={"example": {"id": 1, "name": "Fruits"}})

    id: int
    name: str


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "id": 1, "name": "Apple", "description": None, "price": "180.00", "stock": 150,
            "unit": "kg", "category_id": 1, "category_name": "Fruits", "active": True, "avg_rating": 4.5,
        }
    })

    id: int
    name: str
    description: str | None
    price: Decimal
    stock: int
    unit: ProductUnit
    category_id: int
    category_name: str
    active: bool
    avg_rating: float | None = None


class ProductListOut(BaseModel):
    items: list[ProductOut]
    page: int
    page_size: int
    total: int
    total_pages: int


class ProductCreate(BaseModel):
    """R2.2 validation, used by admin product CRUD (M8)."""

    name: str = Field(..., min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=2000)
    price: Decimal = Field(..., ge=Decimal("0.01"), le=Decimal("10000.00"))
    stock: int = Field(..., ge=0, le=1000)
    unit: ProductUnit
    category_id: int
    active: bool = True


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=2000)
    price: Decimal | None = Field(default=None, ge=Decimal("0.01"), le=Decimal("10000.00"))
    stock: int | None = Field(default=None, ge=0, le=1000)
    unit: ProductUnit | None = None
    category_id: int | None = None
    active: bool | None = None
