from datetime import datetime

from fastapi import APIRouter, Depends

from app.database import get_db
from app.deps import get_now, require_customer
from app.schemas.order import OrderOut
from app.services import order_service

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=list[OrderOut], summary="List the current customer's orders (R6.6)")
async def list_orders(db=Depends(get_db), user=Depends(require_customer)):
    orders = await order_service.list_orders_for_customer(db, user)
    return [order_service.to_order_dict(o) for o in orders]


@router.get("/{order_id}", response_model=OrderOut, summary="Get order detail with status timeline (R6.5, R6.6)")
async def get_order(order_id: int, db=Depends(get_db), user=Depends(require_customer)):
    order = await order_service.get_order_for_customer(db, order_id, user)
    return order_service.to_order_dict(order, include_audits=True)


@router.post("/{order_id}/cancel", response_model=OrderOut, summary="Cancel an order (R6.2)")
async def cancel_order(order_id: int, db=Depends(get_db), user=Depends(require_customer), now: datetime = Depends(get_now)):
    order = await order_service.cancel_order(db, order_id, user, now)
    return order_service.to_order_dict(order)
