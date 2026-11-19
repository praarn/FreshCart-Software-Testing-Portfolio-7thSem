from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", summary="Health check", responses={200: {"content": {"application/json": {"example": {"status": "ok"}}}}})
async def health():
    """Trivial smoke endpoint used by CI to confirm the API process is up."""
    return {"status": "ok"}
