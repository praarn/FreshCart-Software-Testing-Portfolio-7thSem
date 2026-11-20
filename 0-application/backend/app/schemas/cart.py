from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ProductUnit


class AddToCartRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"product_id": 1, "quantity": 2}})

    product_id: int
    quantity: int = Field(..., ge=1, le=10)


class UpdateCartItemRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"quantity": 3}})

    quantity: int = Field(..., ge=1, le=10)


class CartItemOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    unit: ProductUnit
    unit_price: Decimal
    quantity: int
    stock: int
    line_total: Decimal


class CartOut(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "items": [{"id": 1, "product_id": 1, "product_name": "Apple", "unit": "kg", "unit_price": "180.00",
                       "quantity": 2, "stock": 150, "line_total": "360.00"}],
            "coupon_code": None, "subtotal": "360.00", "discount": "0.00", "delivery_fee": "40.00", "total": "400.00",
        }
    })

    items: list[CartItemOut]
    coupon_code: str | None = None
    subtotal: Decimal
    discount: Decimal
    delivery_fee: Decimal
    total: Decimal
