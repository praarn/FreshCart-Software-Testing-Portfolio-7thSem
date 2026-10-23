from datetime import datetime

from fastapi import APIRouter, Depends

from app.database import get_db
from app.deps import get_now, require_customer
from app.schemas.order import CheckoutRequest, OrderOut, SlotOut
from app.services import checkout_service, order_service

router = APIRouter(prefix="/checkout", tags=["checkout"])


@router.get("/slots", response_model=list[SlotOut], summary="List available delivery slots (R5.2)")
async def list_slots(db=Depends(get_db), now: datetime = Depends(get_now)):
    return await checkout_service.list_available_slots(db, now)


@router.post("", response_model=OrderOut, status_code=201, summary="Place an order from the cart (R5.1-R5.5)")
async def place_order(
    payload: CheckoutRequest, db=Depends(get_db), user=Depends(require_customer), now: datetime = Depends(get_now)
):
    order = await checkout_service.checkout(db, user, now, payload.address, payload.slot_start, payload.payment)
    return order_service.to_order_dict(order, include_otp=True)
