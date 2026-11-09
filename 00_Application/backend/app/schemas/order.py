import re
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums import OrderStatus, PaymentMethod, ProductUnit

PINCODE_RE = re.compile(r"^\d{6}$")
UPI_RE = re.compile(r"^[\w.\-]+@[\w]+$")
CARD_EXPIRY_RE = re.compile(r"^(0[1-9]|1[0-2])/\d{2}$")


class AddressIn(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {"line1": "123 MG Road, Indiranagar", "city": "Bengaluru", "pincode": "560001"}
    })

    line1: str = Field(..., min_length=5, max_length=100)
    city: str = Field(..., min_length=2, max_length=50)
    pincode: str

    @field_validator("pincode")
    @classmethod
    def _check_pincode(cls, v: str) -> str:
        if not PINCODE_RE.match(v):
            raise ValueError("Pincode must be exactly 6 digits.")
        return v


class PaymentIn(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {"method": "UPI", "upi_id": "jane@upi", "card_number": None, "card_expiry": None, "cvv": None}
    })

    method: PaymentMethod
    upi_id: str | None = None
    card_number: str | None = None
    card_expiry: str | None = None
    cvv: str | None = None

    @model_validator(mode="after")
    def _check_method_fields(self) -> "PaymentIn":
        if self.method == PaymentMethod.UPI:
            if not self.upi_id or not UPI_RE.match(self.upi_id):
                raise ValueError("A valid UPI id (name@bank) is required for UPI payment.")
        elif self.method == PaymentMethod.CARD:
            if not self.card_number or not re.match(r"^\d{16}$", self.card_number):
                raise ValueError("Card number must be exactly 16 digits.")
            if not self.card_expiry or not CARD_EXPIRY_RE.match(self.card_expiry):
                raise ValueError("Card expiry must be in MM/YY format.")
            if not self.cvv or not re.match(r"^\d{3}$", self.cvv):
                raise ValueError("CVV must be exactly 3 digits.")
        return self


class CheckoutRequest(BaseModel):
    address: AddressIn
    slot_start: datetime
    payment: PaymentIn


class OrderItemOut(BaseModel):
    product_id: int
    product_name: str
    unit: ProductUnit
    unit_price: Decimal
    quantity: int
    line_total: Decimal


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "id": 1, "order_number": "FC-20261110-0001", "status": "PLACED",
            "subtotal": "360.00", "discount": "36.00", "delivery_fee": "40.00", "total": "364.00",
            "coupon_code": "WELCOME10", "address_line1": "123 MG Road", "address_city": "Bengaluru",
            "address_pincode": "560001", "slot_start": "2026-11-10T10:00:00", "slot_end": "2026-11-10T12:00:00",
            "payment_method": "UPI", "payment_reference": "jane@upi", "delivery_otp": "4821",
            "delivery_partner_id": None, "items": [], "created_at": "2026-11-10T09:00:00",
        }
    })

    id: int
    order_number: str
    status: OrderStatus
    subtotal: Decimal
    discount: Decimal
    delivery_fee: Decimal
    total: Decimal
    coupon_code: str | None
    address_line1: str
    address_city: str
    address_pincode: str
    slot_start: datetime
    slot_end: datetime
    payment_method: PaymentMethod
    payment_reference: str | None
    delivery_otp: str | None = None
    delivery_partner_id: int | None
    items: list[OrderItemOut]
    created_at: datetime


class SlotOut(BaseModel):
    slot_start: datetime
    slot_end: datetime
    available: bool
    remaining_capacity: int
