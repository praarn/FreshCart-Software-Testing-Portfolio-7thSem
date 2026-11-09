import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import Role, UserStatus

NAME_RE = re.compile(r"^[A-Za-z ]{2,50}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^[6-9]\d{9}$")


def validate_name(v: str) -> str:
    if not NAME_RE.match(v):
        raise ValueError("Name must be 2-50 characters, letters and spaces only.")
    return v


def validate_email(v: str) -> str:
    v = v.strip().lower()
    if len(v) > 100 or not EMAIL_RE.match(v):
        raise ValueError("Enter a valid email address (max 100 characters).")
    return v


def validate_password(v: str) -> str:
    if not (8 <= len(v) <= 20):
        raise ValueError("Password must be 8-20 characters.")
    if not re.search(r"[A-Za-z]", v) or not re.search(r"\d", v):
        raise ValueError("Password must contain at least 1 letter and 1 digit.")
    return v


def validate_phone(v: str) -> str:
    if not PHONE_RE.match(v):
        raise ValueError("Phone must be exactly 10 digits, starting with 6-9.")
    return v


class RegisterRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {"name": "Jane Doe", "email": "jane.doe@example.com", "password": "Passw0rd1", "phone": "9876543210"}
    })

    name: str = Field(..., examples=["Jane Doe"])
    email: str = Field(..., examples=["jane.doe@example.com"])
    password: str = Field(..., examples=["Passw0rd1"])
    phone: str = Field(..., examples=["9876543210"])

    _v_name = field_validator("name")(validate_name)
    _v_email = field_validator("email")(validate_email)
    _v_password = field_validator("password")(validate_password)
    _v_phone = field_validator("phone")(validate_phone)


class LoginRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {"email": "customer1@freshcart.test", "password": "Customer@1234"}
    })

    email: str
    password: str

    _v_email = field_validator("email")(validate_email)


class TokenResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {"access_token": "eyJhbGciOiJIUzI1NiIs...", "token_type": "bearer", "expires_in": 1800}
    })

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    phone: str
    role: Role
    status: UserStatus
