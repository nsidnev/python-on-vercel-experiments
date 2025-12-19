"""FastAPI application factory"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from api.src.settings import settings
from api.src.routes import router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(title=settings.app_name, debug=settings.debug)

    # Session middleware for OAuth (stores temp state during OAuth flow)
    app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

    # CORS middleware with environment-based origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routes
    app.include_router(router)

    return app
