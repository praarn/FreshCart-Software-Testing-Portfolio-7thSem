"""Shared order read helpers (M5) plus the M6 order lifecycle state machine."""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import BadRequestError, ConflictError, ForbiddenError, NotFoundError
from app.core.ws_manager import manager as ws_manager
from app.models.enums import OrderStatus, Role
from app.models.order import Order, OrderAudit, OrderItem
from app.models.user import User
from app.services.pricing_service import round2

MAX_OTP_ATTEMPTS = 3


async def _load_order(db: AsyncSession, order_id: int, *, with_audits: bool = False) -> Order:
    options = [selectinload(Order.items).selectinload(OrderItem.product)]
    if with_audits:
        options.append(selectinload(Order.audits))
    order = await db.scalar(
        select(Order).options(*options).where(Order.id == order_id).execution_options(populate_existing=True)
    )
    if order is None:
        raise NotFoundError("Order not found.")
    return order


async def _transition(db: AsyncSession, order: Order, to_status: OrderStatus, actor: User, now: datetime) -> None:
    from_status = order.status
    order.status = to_status
    order.updated_at = now
    db.add(OrderAudit(
        order_id=order.id, from_state=from_status.value, to_state=to_status.value,
        actor_id=actor.id, actor_role=actor.role.value, timestamp=now,
    ))
    await db.commit()
    await ws_manager.broadcast(order.id, {"order_id": order.id, "status": to_status.value, "timestamp": now.isoformat()})


async def get_order_for_customer(db: AsyncSession, order_id: int, user: User) -> Order:
    order = await _load_order(db, order_id, with_audits=True)
    if order.user_id != user.id:
        raise ForbiddenError("This order does not belong to you.")  # R6.6
    return order


async def list_orders_for_customer(db: AsyncSession, user: User) -> list[Order]:
    result = await db.scalars(
        select(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
        .where(Order.user_id == user.id)
        .order_by(Order.created_at.desc())
    )
    return list(result.all())


async def cancel_order(db: AsyncSession, order_id: int, actor: User, now: datetime, *, is_admin: bool = False) -> Order:
    order = await _load_order(db, order_id)
    if not is_admin and order.user_id != actor.id:
        raise ForbiddenError("This order does not belong to you.")
    if order.status not in (OrderStatus.PLACED, OrderStatus.CONFIRMED):
        raise ConflictError(f"Order cannot be cancelled from status {order.status.value}.")  # R6.2

    for item in order.items:
        item.product.stock += item.quantity
    order.cancelled_at = now
    await _transition(db, order, OrderStatus.CANCELLED, actor, now)
    return order


_ADMIN_TRANSITIONS = {
    (OrderStatus.PLACED, OrderStatus.CONFIRMED),
    (OrderStatus.CONFIRMED, OrderStatus.PACKED),
}


async def admin_advance_status(db: AsyncSession, order_id: int, to_status: OrderStatus, admin: User, now: datetime) -> Order:
    order = await _load_order(db, order_id)
    if (order.status, to_status) not in _ADMIN_TRANSITIONS:
        raise ConflictError(f"Cannot move order from {order.status.value} to {to_status.value}.")  # R6.1/R6.3
    await _transition(db, order, to_status, admin, now)
    return order


async def assign_delivery_partner(db: AsyncSession, order_id: int, partner_id: int, admin: User, now: datetime) -> Order:
    order = await _load_order(db, order_id)
    if order.status != OrderStatus.PACKED:
        raise ConflictError("A delivery partner can only be assigned once the order is PACKED.")  # R6.3
    partner = await db.get(User, partner_id)
    if partner is None or partner.role != Role.DELIVERY_PARTNER:
        raise BadRequestError("The given user is not a delivery partner.")
    order.delivery_partner_id = partner.id
    order.updated_at = now
    await db.commit()
    return order


async def reset_otp_attempts(db: AsyncSession, order_id: int, admin: User, now: datetime) -> Order:
    order = await _load_order(db, order_id)
    order.otp_attempts = 0
    order.otp_blocked = False
    order.updated_at = now
    await db.commit()
    return order


async def list_orders_for_partner(db: AsyncSession, partner: User) -> list[Order]:
    result = await db.scalars(
        select(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
        .where(Order.delivery_partner_id == partner.id)
        .order_by(Order.created_at.desc())
    )
    return list(result.all())  # R6.4: delivery partner sees only assigned orders


async def start_delivery(db: AsyncSession, order_id: int, partner: User, now: datetime) -> Order:
    order = await _load_order(db, order_id)
    if order.delivery_partner_id != partner.id:
        raise ForbiddenError("This order is not assigned to you.")
    if order.status != OrderStatus.PACKED:
        raise ConflictError(f"Cannot dispatch an order from status {order.status.value}.")
    await _transition(db, order, OrderStatus.OUT_FOR_DELIVERY, partner, now)
    return order


async def complete_delivery(db: AsyncSession, order_id: int, partner: User, otp: str, now: datetime) -> Order:
    order = await _load_order(db, order_id)
    if order.delivery_partner_id != partner.id:
        raise ForbiddenError("This order is not assigned to you.")
    if order.status != OrderStatus.OUT_FOR_DELIVERY:
        raise ConflictError(f"Cannot deliver an order from status {order.status.value}.")
    if order.otp_blocked:
        raise ConflictError("Too many incorrect OTP attempts. Ask an admin to reset this order.")  # R6.4

    if otp != order.delivery_otp:
        order.otp_attempts += 1
        if order.otp_attempts >= MAX_OTP_ATTEMPTS:
            order.otp_blocked = True
        await db.commit()
        if order.otp_blocked:
            raise ConflictError("Incorrect OTP. No attempts remaining; ask an admin to reset this order.")
        raise BadRequestError(f"Incorrect OTP. {MAX_OTP_ATTEMPTS - order.otp_attempts} attempt(s) remaining.")

    order.delivered_at = now
    await _transition(db, order, OrderStatus.DELIVERED, partner, now)
    return order


def to_order_dict(order: Order, include_otp: bool = True, include_audits: bool = False) -> dict:
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
        "audits": (
            [
                {"from_state": a.from_state, "to_state": a.to_state, "actor_role": a.actor_role, "timestamp": a.timestamp}
                for a in order.audits
            ]
            if include_audits
            else []
        ),
    }
