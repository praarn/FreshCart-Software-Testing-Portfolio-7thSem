"""Shared order read helpers, used by checkout (M5) and the order lifecycle (M6)."""
from app.models.order import Order
from app.services.pricing_service import round2


def to_order_dict(order: Order, include_otp: bool = True) -> dict:
    items = [
        {
            "product_id": item.product_id,
            "product_name": item.product_name,
            "unit": item.product.unit,
            "unit_price": item.unit_price,
            "quantity": item.quantity,
            "line_total": round2(item.unit_price * item.quantity),
        }
        for item in order.items
    ]
    return {
        "id": order.id,
        "order_number": order.order_number,
        "status": order.status,
        "subtotal": order.subtotal,
        "discount": order.discount,
        "delivery_fee": order.delivery_fee,
        "total": order.total,
        "coupon_code": order.coupon_code,
        "address_line1": order.address_line1,
        "address_city": order.address_city,
        "address_pincode": order.address_pincode,
        "slot_start": order.slot_start,
        "slot_end": order.slot_end,
        "payment_method": order.payment_method,
        "payment_reference": order.payment_reference,
        "delivery_otp": order.delivery_otp if include_otp else None,
        "delivery_partner_id": order.delivery_partner_id,
        "items": items,
        "created_at": order.created_at,
    }
