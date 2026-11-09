from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.errors import register_error_handlers
from app.routers import auth, cart, catalog, health

settings = get_settings()

app = FastAPI(
    title="FreshCart API",
    description="Online grocery shopping and delivery system — REST API.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)

app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(catalog.router, prefix="/api")
app.include_router(cart.router, prefix="/api")

if settings.APP_ENV == "test":
    from app.routers import test_utils

    app.include_router(test_utils.router, prefix="/api")
