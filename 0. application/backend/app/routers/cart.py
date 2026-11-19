from datetime import datetime

from fastapi import APIRouter, Depends

from app.database import get_db
from app.deps import get_now, require_customer
from app.schemas.cart import AddToCartRequest, CartOut, UpdateCartItemRequest
from app.schemas.coupon import ApplyCouponRequest
from app.services import cart_service

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("", response_model=CartOut, summary="Get the current user's cart (R3.5)")
async def get_cart(db=Depends(get_db), user=Depends(require_customer), now: datetime = Depends(get_now)):
    return await cart_service.get_cart(db, user, now)


@router.post("/items", response_model=CartOut, summary="Add a product to the cart (R3.1-R3.3)")
async def add_item(
    payload: AddToCartRequest, db=Depends(get_db), user=Depends(require_customer), now: datetime = Depends(get_now)
):
    return await cart_service.add_item(db, user, payload.product_id, payload.quantity, now)


@router.put("/items/{item_id}", response_model=CartOut, summary="Update a cart item's quantity (R3.4)")
async def update_item(
    item_id: int,
    payload: UpdateCartItemRequest,
    db=Depends(get_db),
    user=Depends(require_customer),
    now: datetime = Depends(get_now),
):
    return await cart_service.update_item(db, user, item_id, payload.quantity, now)


@router.delete("/items/{item_id}", response_model=CartOut, summary="Remove an item from the cart (R3.4)")
async def remove_item(item_id: int, db=Depends(get_db), user=Depends(require_customer), now: datetime = Depends(get_now)):
    return await cart_service.remove_item(db, user, item_id, now)


@router.delete("", response_model=CartOut, summary="Clear the cart (R3.4)")
async def clear_cart(db=Depends(get_db), user=Depends(require_customer), now: datetime = Depends(get_now)):
    return await cart_service.clear_cart(db, user, now)


@router.post("/coupon", response_model=CartOut, summary="Apply a coupon code to the cart (R4.1-R4.2)")
async def apply_coupon(
    payload: ApplyCouponRequest, db=Depends(get_db), user=Depends(require_customer), now: datetime = Depends(get_now)
):
    return await cart_service.apply_coupon(db, user, payload.code, now)


@router.delete("/coupon", response_model=CartOut, summary="Remove the coupon applied to the cart")
async def remove_coupon(db=Depends(get_db), user=Depends(require_customer), now: datetime = Depends(get_now)):
    return await cart_service.remove_coupon(db, user, now)
