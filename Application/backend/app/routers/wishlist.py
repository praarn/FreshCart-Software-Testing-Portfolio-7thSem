from datetime import datetime

from fastapi import APIRouter, Depends

from app.database import get_db
from app.deps import get_now, require_customer
from app.schemas.wishlist import WishlistAddRequest, WishlistItemOut
from app.services import catalog_service, wishlist_service

router = APIRouter(prefix="/wishlist", tags=["wishlist"])


@router.get("", response_model=list[WishlistItemOut], summary="List the current customer's wishlist")
async def list_wishlist(db=Depends(get_db), user=Depends(require_customer)):
    items = await wishlist_service.list_wishlist(db, user)
    return [
        {"id": i.id, "product": catalog_service.to_product_dict(i.product, None)}
        for i in items
    ]


@router.post("/items", response_model=WishlistItemOut, status_code=201, summary="Add a product to the wishlist")
async def add_item(payload: WishlistAddRequest, db=Depends(get_db), user=Depends(require_customer), now: datetime = Depends(get_now)):
    item = await wishlist_service.add_to_wishlist(db, user, payload.product_id, now)
    return {"id": item.id, "product": catalog_service.to_product_dict(item.product, None)}


@router.delete("/items/{product_id}", status_code=204, summary="Remove a product from the wishlist")
async def remove_item(product_id: int, db=Depends(get_db), user=Depends(require_customer)):
    await wishlist_service.remove_from_wishlist(db, user, product_id)
