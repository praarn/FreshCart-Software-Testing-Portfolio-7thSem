import math

from fastapi import APIRouter, Depends, Query

from app.database import get_db
from app.schemas.catalog import CategoryOut, ProductListOut, ProductOut
from app.services import catalog_service

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/categories", response_model=list[CategoryOut], summary="List all categories (R2.1)")
async def list_categories(db=Depends(get_db)):
    return await catalog_service.list_categories(db)


@router.get("/products", response_model=ProductListOut, summary="Search/filter/sort/paginate products (R2.3, R2.4)")
async def list_products(
    search: str | None = Query(default=None, description="Case-insensitive partial name match"),
    category_id: int | None = Query(default=None),
    sort: str | None = Query(default=None, pattern="^(price_asc|price_desc)$"),
    page: int = Query(default=1, ge=1),
    db=Depends(get_db),
):
    items, total = await catalog_service.list_products(db, search, category_id, sort, page)
    total_pages = math.ceil(total / catalog_service.PAGE_SIZE) if total else 0
    return ProductListOut(items=items, page=page, page_size=catalog_service.PAGE_SIZE, total=total, total_pages=total_pages)


@router.get("/products/{product_id}", response_model=ProductOut, summary="Get a single product (R2.4 hides inactive)")
async def get_product(product_id: int, db=Depends(get_db)):
    return await catalog_service.get_product(db, product_id)
