"""
Application factory for FastAPI Advanced Example

This module demonstrates production-ready patterns:
- Application factory pattern
- Router organization
- Middleware configuration
- Dependency injection
- Environment-based configuration
"""

import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime

from app.config import settings
from app.routers import products, users
from app.middleware import RequestLoggingMiddleware, setup_cors_middleware
from app.models import HealthCheck, ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Application factory function

    Returns:
        FastAPI: Configured FastAPI application instance
    """
    # Create FastAPI instance with configuration
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Production-ready FastAPI application with advanced patterns",
        docs_url="/docs" if settings.ENABLE_DOCS else None,
        redoc_url="/redoc" if settings.ENABLE_DOCS else None,
        openapi_url="/openapi.json" if settings.ENABLE_DOCS else None,
    )

    # Setup CORS middleware
    setup_cors_middleware(app, settings.ALLOWED_ORIGINS)

    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Include routers
    app.include_router(products.router, prefix=settings.API_PREFIX)
    app.include_router(users.router, prefix=settings.API_PREFIX)

    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        """Welcome endpoint"""
        return {
            "message": f"Welcome to {settings.APP_NAME}",
            "version": settings.APP_VERSION,
            "timestamp": datetime.now().isoformat(),
            "docs": "/docs" if settings.ENABLE_DOCS else "disabled",
            "endpoints": {
                "/": "This endpoint",
                f"{settings.API_PREFIX}/products": "Product management",
                f"{settings.API_PREFIX}/users": "User management",
                f"{settings.API_PREFIX}/health": "Health check",
            },
        }

    # Health check endpoint
    @app.get(
        f"{settings.API_PREFIX}/health",
        response_model=HealthCheck,
        tags=["monitoring"],
    )
    async def health_check():
        """Application health check"""
        return HealthCheck(
            status="healthy",
            timestamp=datetime.now(),
            version=settings.APP_VERSION,
            environment="production" if not settings.DEBUG else "development",
        )

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Handle all unhandled exceptions"""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)

        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="Internal server error",
                detail=str(exc) if settings.DEBUG else None,
                timestamp=datetime.now(),
            ).model_dump(),
        )

    logger.info(f"Application created: {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"API documentation: {'enabled' if settings.ENABLE_DOCS else 'disabled'}")

    return app


# Create application instance for Vercel
# Vercel looks for 'app' or 'handler' variable in app/main.py
app = create_app()
