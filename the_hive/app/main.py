from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.db import check_db_connection, init_db
from app.core.logging import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting application", extra={"extra_fields": {"app_name": settings.APP_NAME}})
    init_db()  # Create database tables on startup
    yield
    logger.info("Shutting down application")


app = FastAPI(
    title=settings.APP_NAME,
    description="RESTful backend API for the_hive",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz", tags=["Health"])
async def health_check() -> JSONResponse:
    db_status = "connected" if check_db_connection() else "disconnected"
    
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": "0.1.0",
            "database": db_status,
        },
    )


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "docs": "/docs",
        "health": "/healthz",
    }


from app.api.auth import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.forum import router as forum_router
from app.api.handshake import router as handshake_router
from app.api.map import router as map_router
from app.api.needs import router as needs_router
from app.api.notifications import router as notifications_router
from app.api.offers import router as offers_router
from app.api.participants import router as participants_router
from app.api.ratings import router as ratings_router
from app.api.search import router as search_router
from app.api.users import router as users_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(offers_router, prefix="/api/v1")
app.include_router(needs_router, prefix="/api/v1")
app.include_router(participants_router, prefix="/api/v1")
app.include_router(handshake_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(ratings_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(map_router, prefix="/api/v1")
app.include_router(forum_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")

