from pydantic import BaseModel, ConfigDict, Field


class BannerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "id": 1, "title": "Fresh fruits, up to 20% off", "image_url": "https://example.com/banner1.jpg",
            "link_url": "/?category_id=1", "display_order": 1, "active": True,
        }
    })

    id: int
    title: str
    image_url: str
    link_url: str | None
    display_order: int
    active: bool


class BannerCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=100)
    image_url: str = Field(..., min_length=5, max_length=500)
    link_url: str | None = Field(default=None, max_length=500)
    display_order: int = 0
    active: bool = True


class BannerUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=100)
    image_url: str | None = Field(default=None, min_length=5, max_length=500)
    link_url: str | None = Field(default=None, max_length=500)
    display_order: int | None = None
    active: bool | None = None
