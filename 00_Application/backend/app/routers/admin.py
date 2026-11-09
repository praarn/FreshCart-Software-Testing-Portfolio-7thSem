"""M8 admin endpoints: order-lifecycle actions (R6.x) plus product/order/coupon/user
management, dashboard and audit log (R8.1-R8.5)."""
from datetime import date, datetime

from fastapi import APIRouter, Depends, Query

from app.database import get_db
from app.deps import get_now, require_admin
from app.models.enums import OrderStatus
from app.schemas.admin import ActiveUpdateRequest, AuditLogOut, DashboardOut, StockUpdateRequest
from app.schemas.banner import BannerCreate, BannerOut, BannerUpdate
from app.schemas.catalog import ProductCreate, ProductOut, ProductUpdate
from app.schemas.coupon import CouponOut, CouponUpdate
from app.schemas.order import AssignPartnerRequest, OrderOut, UpdateOrderStatusRequest
from app.schemas.user import UserOut
from app.services import admin_service, banner_service, catalog_service, order_service

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


# --- order lifecycle (R6.1-R6.4) ---------------------------------------------


@router.get("/orders", response_model=list[OrderOut], summary="List orders, filterable by status/date (R8.2)")
async def list_orders(
    status: OrderStatus | None = Query(default=None),
    order_date: date | None = Query(default=None, alias="date"),
    db=Depends(get_db),
):
    orders = await admin_service.list_orders(db, status, order_date)
    return [order_service.to_order_dict(o) for o in orders]


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


# --- products (R8.1) -----------------------------------------------------------


@router.get("/products", response_model=list[ProductOut], summary="List all products, including inactive (R8.1)")
async def list_products(
    search: str | None = Query(default=None),
    category_id: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    db=Depends(get_db),
):
    items, _total = await catalog_service.list_products(db, search, category_id, None, page, include_inactive=True)
    return items


@router.post("/products", response_model=ProductOut, status_code=201, summary="Create a product (R2.2, R8.1)")
async def create_product(payload: ProductCreate, db=Depends(get_db), now: datetime = Depends(get_now)):
    product = await admin_service.create_product(
        db, payload.name, payload.description, payload.price, payload.stock, payload.unit, payload.category_id, payload.active, now
    )
    return catalog_service.to_product_dict(product, None)


@router.put("/products/{product_id}", response_model=ProductOut, summary="Update a product (R2.2, R8.1)")
async def update_product(product_id: int, payload: ProductUpdate, db=Depends(get_db), now: datetime = Depends(get_now)):
    product = await admin_service.update_product(db, product_id, payload.model_dump(exclude_unset=True), now)
    return catalog_service.to_product_dict(product, None)


@router.patch("/products/{product_id}/stock", response_model=ProductOut, summary="Update stock (R8.1)")
async def update_stock(product_id: int, payload: StockUpdateRequest, db=Depends(get_db), now: datetime = Depends(get_now)):
    product = await admin_service.update_stock(db, product_id, payload.stock, now)
    return catalog_service.to_product_dict(product, None)


@router.patch("/products/{product_id}/active", response_model=ProductOut, summary="Activate/deactivate a product (R8.1)")
async def set_product_active(product_id: int, payload: ActiveUpdateRequest, db=Depends(get_db), now: datetime = Depends(get_now)):
    product = await admin_service.set_product_active(db, product_id, payload.active, now)
    return catalog_service.to_product_dict(product, None)


# --- coupons (R8.3) -------------------------------------------------------------


@router.get("/coupons", response_model=list[CouponOut], summary="List all coupons (R8.3)")
async def list_coupons(db=Depends(get_db)):
    return await admin_service.list_coupons(db)


@router.patch("/coupons/{coupon_id}", response_model=CouponOut, summary="Enable/disable a coupon (R8.3)")
async def update_coupon(coupon_id: int, payload: CouponUpdate, db=Depends(get_db)):
    return await admin_service.set_coupon_active(db, coupon_id, payload.active)


# --- users (R8.3) ---------------------------------------------------------------


@router.get("/users", response_model=list[UserOut], summary="List all users (R8.3)")
async def list_users(db=Depends(get_db)):
    return await admin_service.list_users(db)


@router.post("/users/{user_id}/lock", response_model=UserOut, summary="Lock a user account (R8.3)")
async def lock_user(user_id: int, db=Depends(get_db)):
    return await admin_service.lock_user(db, user_id)


@router.post("/users/{user_id}/unlock", response_model=UserOut, summary="Unlock a user account (R1.5, R8.3)")
async def unlock_user(user_id: int, db=Depends(get_db)):
    return await admin_service.unlock_user(db, user_id)


# --- banners -----------------------------------------------------------------------


@router.get("/banners", response_model=list[BannerOut], summary="List all banners, including inactive")
async def list_all_banners(db=Depends(get_db)):
    return await banner_service.list_all_banners(db)


@router.post("/banners", response_model=BannerOut, status_code=201, summary="Create a promotional banner")
async def create_banner(payload: BannerCreate, db=Depends(get_db), now: datetime = Depends(get_now)):
    return await banner_service.create_banner(
        db, payload.title, payload.image_url, payload.link_url, payload.display_order, payload.active, now
    )


@router.put("/banners/{banner_id}", response_model=BannerOut, summary="Update a banner")
async def update_banner(banner_id: int, payload: BannerUpdate, db=Depends(get_db), now: datetime = Depends(get_now)):
    return await banner_service.update_banner(db, banner_id, payload.model_dump(exclude_unset=True), now)


@router.delete("/banners/{banner_id}", status_code=204, summary="Delete a banner")
async def delete_banner(banner_id: int, db=Depends(get_db)):
    await banner_service.delete_banner(db, banner_id)


# --- dashboard (R8.4) ------------------------------------------------------------


@router.get("/dashboard", response_model=DashboardOut, summary="Admin dashboard metrics (R8.4)")
async def get_dashboard(db=Depends(get_db), now: datetime = Depends(get_now)):
    return await admin_service.dashboard(db, now)


# --- audit log (R8.5) ------------------------------------------------------------


@router.get("/audit-log", response_model=list[AuditLogOut], summary="Audit log, filterable by order/actor (R8.5)")
async def audit_log(order_id: int | None = Query(default=None), actor_id: int | None = Query(default=None), db=Depends(get_db)):
    return await admin_service.list_audit_logs(db, order_id, actor_id)
