"""R6.7: token-authenticated WebSocket pushing live order-status changes."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.core.security import decode_access_token
from app.core.ws_manager import manager
from app.database import AsyncSessionLocal
from app.models.enums import Role
from app.models.order import Order
from app.models.token_denylist import TokenDenylist

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/orders/{order_id}")
async def order_status_ws(websocket: WebSocket, order_id: int, token: str):
    try:
        payload = decode_access_token(token)
    except ValueError:
        await websocket.close(code=4401)
        return

    async with AsyncSessionLocal() as db:
        denylisted = await db.scalar(select(TokenDenylist).where(TokenDenylist.jti == payload.get("jti")))
        if denylisted is not None:
            await websocket.close(code=4401)
            return

        order = await db.get(Order, order_id)
        if order is None:
            await websocket.close(code=4404)
            return

        user_id = int(payload["sub"])
        role = payload.get("role")
        is_owner = role == Role.CUSTOMER.value and order.user_id == user_id
        is_partner = role == Role.DELIVERY_PARTNER.value and order.delivery_partner_id == user_id
        is_admin = role == Role.ADMIN.value
        if not (is_owner or is_partner or is_admin):
            await websocket.close(code=4403)
            return

    await websocket.accept()
    manager.connect(order_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(order_id, websocket)
