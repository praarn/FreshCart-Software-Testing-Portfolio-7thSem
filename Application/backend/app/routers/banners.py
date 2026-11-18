from fastapi import APIRouter, Depends

from app.database import get_db
from app.schemas.banner import BannerOut
from app.services import banner_service

router = APIRouter(prefix="/banners", tags=["banners"])


@router.get("", response_model=list[BannerOut], summary="List active promotional banners")
async def list_banners(db=Depends(get_db)):
    return await banner_service.list_active_banners(db)
