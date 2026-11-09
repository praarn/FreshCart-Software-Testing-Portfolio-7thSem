"""Admin endpoints. This phase adds only the order-lifecycle actions needed to drive
M6 (R6.3) end-to-end; the rest of M8 (product/coupon/user management, dashboard,
audit viewer) is added in a later phase."""
from datetime import datetime

from fastapi import APIRouter, Depends

from app.database import get_db
from app.deps import get_now, require_admin
from app.models.enums import OrderStatus
from app.schemas.order import AssignPartnerRequest, OrderOut, UpdateOrderStatusRequest
from app.services import order_service

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.patch("/orders/{order_id}/status", response_model=OrderOut, summary="Advance an order's status (R6.1, R6.3)")
async def update_order_status(
    order_id: int, payload: UpdateOrderStatusRequest, db=Depends(get_db), admin=Depends(require_admin), now: datetime = Depends(get_now)
):
    order = await order_service.admin_advance_status(db, order_id, payload.to_status, admin, now)
    return order_service.to_order_dict(order)


@router.post("/orders/{order_id}/assign-partner", response_model=OrderOut, summary="Assign a delivery partner (R6.3)")
async def assign_partner(
    order_id: int, payload: AssignPartnerRequest, db=Depends(get_db), admin=Depends(require_admin), now: datetime = Depends(get_now)
):
    order = await order_service.assign_delivery_partner(db, order_id, payload.delivery_partner_id, admin, now)
    return order_service.to_order_dict(order)


@router.post("/orders/{order_id}/reset-otp", response_model=OrderOut, summary="Reset OTP attempts on an order (R6.4, R8.2)")
async def reset_otp(order_id: int, db=Depends(get_db), admin=Depends(require_admin), now: datetime = Depends(get_now)):
    order = await order_service.reset_otp_attempts(db, order_id, admin, now)
    return order_service.to_order_dict(order)


@router.post("/orders/{order_id}/cancel", response_model=OrderOut, summary="Admin-cancel an order (R6.2)")
async def admin_cancel_order(order_id: int, db=Depends(get_db), admin=Depends(require_admin), now: datetime = Depends(get_now)):
    order = await order_service.cancel_order(db, order_id, admin, now, is_admin=True)
    return order_service.to_order_dict(order)
