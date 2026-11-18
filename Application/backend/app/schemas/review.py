from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {"product_id": 1, "rating": 5, "comment": "Fresh and tasty!"}
    })

    product_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = Field(default=None, max_length=300)


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    user_id: int
    user_name: str
    rating: int
    comment: str | None
    created_at: datetime
