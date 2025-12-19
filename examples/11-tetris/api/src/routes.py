"""API routes"""

from typing import List, Optional

from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.database import get_db
from api.src.schemas import HighScoreCreateRequest, HighScoreResponse
from api.src.service import get_high_scores, create_high_score
from api.src.auth import (
    oauth,
    create_session_token,
    get_current_user,
    require_auth,
)
from api.src.settings import settings

router = APIRouter()

@router.get("/api/auth/login")
async def login(request: Request):
    """Initiate GitHub OAuth flow"""
    base_url = settings.base_url or str(request.base_url).rstrip("/")
    print(f"[LOGIN] settings.base_url: {settings.base_url}")
    print(f"[LOGIN] request.base_url: {request.base_url}")
    print(f"[LOGIN] Using base_url: {base_url}")
    print(f"[LOGIN] Headers: {dict(request.headers)}")
    redirect_uri = f"{base_url}/api/auth/callback"
    return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get("/api/auth/callback")
async def auth_callback(request: Request):
    """Handle GitHub OAuth callback"""
    # Exchange code for token and get user info
    token = await oauth.github.authorize_access_token(request)

    # Use userinfo endpoint configured in OAuth setup
    user_info = await oauth.github.userinfo(token=token)

    base_url = settings.base_url or str(request.base_url).rstrip("/")
    print(f"[CALLBACK] settings.base_url: {settings.base_url}")
    print(f"[CALLBACK] request.base_url: {request.base_url}")
    print(f"[CALLBACK] Using base_url: {base_url}")
    print(f"[CALLBACK] Headers: {dict(request.headers)}")

    if not user_info or not user_info.get("login"):
        return RedirectResponse(url=f"{base_url}?error=auth_failed")

    # Create session token with user info
    user_data = {
        "username": user_info.get("login"),
        "name": user_info.get("name") or user_info.get("login"),
        "avatar": user_info.get("avatar_url"),
    }

    print(user_data)

    session_token = create_session_token(user_data)

    # Redirect to home with session cookie
    response = RedirectResponse(url=base_url)
    response.set_cookie(
        key="auth_token",
        value=session_token,
        httponly=True,
        secure=settings.environment != "dev",  # False in dev, True in production
        samesite="lax",
        max_age=86400 * 30,  # 30 days
        path="/",
    )
    return response


@router.get("/api/auth/logout")
async def logout(request: Request):
    """Logout and clear session"""
    base_url = settings.base_url or str(request.base_url).rstrip("/")
    response = RedirectResponse(url=base_url)
    response.delete_cookie("auth_token", path="/")
    return response


@router.get("/api/auth/me")
async def get_me(user: Optional[dict] = Depends(get_current_user)):
    """Get current user info"""
    if not user:
        return {"authenticated": False}
    return {"authenticated": True, "user": user}


@router.get("/api/high-scores", response_model=List[HighScoreResponse])
async def list_high_scores(limit: int = 10, db: AsyncSession = Depends(get_db)):
    """Get top high scores"""
    if limit > 100:
        limit = 100
    scores = await get_high_scores(db, limit=limit)
    return scores


@router.post("/api/high-scores", response_model=HighScoreResponse, status_code=status.HTTP_201_CREATED)
async def submit_high_score(
    request: HighScoreCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth),
):
    """Submit a new high score (requires authentication)"""
    # Use authenticated user's username
    high_score = await create_high_score(
        db,
        player_name=user["username"],
        score=request.score,
        level=request.level,
        lines=request.lines,
    )
    return high_score
