from pydantic import BaseModel, ConfigDict


class FieldError(BaseModel):
    field: str
    message: str


class ErrorResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "status": 422,
            "error": "VALIDATION_ERROR",
            "message": "Validation failed.",
            "field_errors": [{"field": "email", "message": "Invalid email format."}],
        }
    })

    status: int
    error: str
    message: str
    field_errors: list[FieldError] = []
