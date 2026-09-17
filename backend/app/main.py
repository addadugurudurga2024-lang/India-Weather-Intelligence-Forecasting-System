"""FastAPI Main Entrypoint for India Weather Forecasting & Intelligence System."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from backend.app.config import settings
from backend.app.services.data_service import load_stations
from backend.app.routers import (
    health,
    stations,
    analytics,
    forecast,
    intelligence,
    long_term_predictor,
    models,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("weather_backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for application startup and shutdown."""
    logger.info("Starting up %s backend...", settings.PROJECT_NAME)
    # Warm up station registry cache (413 canonical stations)
    stations_cache = load_stations()
    logger.info("Loaded %d canonical stations into memory cache.", len(stations_cache))
    yield
    logger.info("Shutting down %s backend.", settings.PROJECT_NAME)


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Unified API backend for India Weather Forecasting & Intelligence System.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handles schema validation errors with structured JSON output."""
    logger.warning("Validation error on %s: %s", request.url.path, exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT if hasattr(status, "HTTP_422_UNPROCESSABLE_CONTENT") else 422,
        content={
            "error": "Validation Error",
            "message": "Malformed request parameters or body.",
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global unhandled exception handler to prevent unformatted 500 dumps."""
    logger.exception("Unhandled server error on %s: %s", request.url.path, str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred while processing the request.",
            "detail": str(exc),
        },
    )


# Register API v1 Routers
api_v1 = settings.API_V1_STR
app.include_router(health.router, prefix=api_v1)
app.include_router(stations.router, prefix=api_v1)
app.include_router(analytics.router, prefix=api_v1)
app.include_router(forecast.router, prefix=api_v1)
app.include_router(intelligence.router, prefix=api_v1)
app.include_router(long_term_predictor.router, prefix=api_v1)
app.include_router(models.router, prefix=api_v1)


@app.get("/")
def root_redirect():
    """Root redirect / ping to API info."""
    return {
        "name": settings.PROJECT_NAME,
        "status": "ONLINE",
        "api_docs": f"{settings.API_V1_STR}/docs",
        "health": f"{settings.API_V1_STR}/health",
    }
