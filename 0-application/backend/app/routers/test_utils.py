"""Only mounted when APP_ENV=test (see app.main). Lets automated test runs reset to a known state."""
from fastapi import APIRouter

from app.core.rate_limit import reset_rate_limits
from app.database import Base, engine
from app.seed import seed

router = APIRouter(tags=["testing"])


@router.post("/test/reset", summary="Wipe and reseed the database, clear rate limits (test mode only)")
async def reset_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await seed()
    reset_rate_limits()  # fast automated runs would otherwise hit the login limit (R1.7)
    return {"status": "ok", "message": "Database reset and reseeded."}
