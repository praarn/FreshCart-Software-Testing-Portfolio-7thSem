from enum import Enum


class Role(str, Enum):
    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"
    DELIVERY_PARTNER = "DELIVERY_PARTNER"


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"


class ProductUnit(str, Enum):
    kg = "kg"
    g = "g"
    l = "l"
    ml = "ml"
    pc = "pc"
    pack = "pack"


class OrderStatus(str, Enum):
    PLACED = "PLACED"
    CONFIRMED = "CONFIRMED"
    PACKED = "PACKED"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class PaymentMethod(str, Enum):
    COD = "COD"
    UPI = "UPI"
    CARD = "CARD"


class CouponType(str, Enum):
    PERCENT = "PERCENT"
    FLAT = "FLAT"
