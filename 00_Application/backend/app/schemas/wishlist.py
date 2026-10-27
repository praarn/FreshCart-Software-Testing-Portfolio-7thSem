from pydantic import BaseModel, ConfigDict

from app.schemas.catalog import ProductOut


class WishlistAddRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"product_id": 1}})

    product_id: int


class WishlistItemOut(BaseModel):
    id: int
    product: ProductOut
