"""
Main FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.db import check_db_connection
from app.core.logging import get_logger, setup_logging

# Initialize logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(
        "Starting application",
        extra={
            "extra_fields": {
                "app_name": settings.APP_NAME,
                "app_env": settings.APP_ENV,
                "debug": settings.DEBUG,
            }
        },
    )
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="RESTful backend API for the_hive",
    version="0.1.0",
    debug=settings.DEBUG,
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
    """
    Health check endpoint.
    
    Returns the application status and basic information.
    Useful for container orchestration and monitoring.
    """
    # Check database connection
    db_status = "connected" if check_db_connection() else "disconnected"
    
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "app": settings.APP_NAME,
            "environment": settings.APP_ENV,
            "version": "0.1.0",
            "database": db_status,
        },
    )


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """
    Root endpoint.
    
    Returns basic API information.
    """
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "docs": "/docs",
        "health": "/healthz",
    }


# Include API routers
from app.api.auth import router as auth_router
from app.api.users import router as users_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")

