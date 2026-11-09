from datetime import datetime

from fastapi import APIRouter, Depends

from app.database import get_db
from app.deps import get_now, require_delivery_partner
from app.schemas.order import DeliverRequest, OrderOut
from app.services import order_service

router = APIRouter(prefix="/delivery", tags=["delivery"], dependencies=[Depends(require_delivery_partner)])


@router.get("/orders", response_model=list[OrderOut], summary="List orders assigned to the current delivery partner (R6.4)")
async def list_my_orders(db=Depends(get_db), partner=Depends(require_delivery_partner)):
    orders = await order_service.list_orders_for_partner(db, partner)
    return [order_service.to_order_dict(o, include_otp=False) for o in orders]


@router.post("/orders/{order_id}/dispatch", response_model=OrderOut, summary="Mark an order OUT_FOR_DELIVERY (R6.4)")
async def dispatch_order(
    order_id: int, db=Depends(get_db), partner=Depends(require_delivery_partner), now: datetime = Depends(get_now)
):
    order = await order_service.start_delivery(db, order_id, partner, now)
    return order_service.to_order_dict(order, include_otp=False)


@router.post("/orders/{order_id}/deliver", response_model=OrderOut, summary="Complete delivery by entering the customer OTP (R6.4)")
async def deliver_order(
    order_id: int,
    payload: DeliverRequest,
    db=Depends(get_db),
    partner=Depends(require_delivery_partner),
    now: datetime = Depends(get_now),
):
    order = await order_service.complete_delivery(db, order_id, partner, payload.otp, now)
    return order_service.to_order_dict(order, include_otp=False)
