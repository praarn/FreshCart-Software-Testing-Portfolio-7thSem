from pydantic import BaseModel, ConfigDict


class ApplyCouponRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"code": "WELCOME10"}})

    code: str
