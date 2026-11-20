from datetime import datetime

from fastapi import APIRouter, Depends

from app.database import get_db
from app.deps import get_now, require_customer
from app.schemas.review import ReviewCreate, ReviewOut
from app.services import review_service

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=ReviewOut, status_code=201, summary="Review a delivered product (R7.1)")
async def create_review(
    payload: ReviewCreate, db=Depends(get_db), user=Depends(require_customer), now: datetime = Depends(get_now)
):
    review = await review_service.create_review(db, user, payload.product_id, payload.rating, payload.comment, now)
    return ReviewOut(
        id=review.id, product_id=review.product_id, user_id=review.user_id,
        user_name=review.user.name, rating=review.rating, comment=review.comment, created_at=review.created_at,
    )


@router.get("", response_model=list[ReviewOut], summary="List reviews for a product")
async def list_reviews(product_id: int, db=Depends(get_db)):
    reviews = await review_service.list_reviews_for_product(db, product_id)
    return [
        ReviewOut(
            id=r.id, product_id=r.product_id, user_id=r.user_id,
            user_name=r.user.name, rating=r.rating, comment=r.comment, created_at=r.created_at,
        )
        for r in reviews
    ]
