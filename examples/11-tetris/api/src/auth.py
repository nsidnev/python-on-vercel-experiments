"""GitHub OAuth authentication"""

from typing import Optional
from datetime import datetime, timedelta, timezone
import jwt
from authlib.integrations.starlette_client import OAuth
from fastapi import Request, HTTPException, status

from api.src.settings import settings

# OAuth setup
oauth = OAuth()
oauth.register(
    name="github",
    client_id=settings.github_client_id,
    client_secret=settings.github_client_secret,
    authorize_url="https://github.com/login/oauth/authorize",
    authorize_params=None,
    access_token_url="https://github.com/login/oauth/access_token",
    access_token_params=None,
    userinfo_endpoint="https://api.github.com/user",
    client_kwargs={"scope": "user:email"},
)


def create_session_token(user_data: dict) -> str:
    """Create a JWT session token with 30 day expiry"""
    now = datetime.now(timezone.utc)
    payload = {
        **user_data,
        "exp": now + timedelta(days=30),
        "iat": now,
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_session_token(token: str) -> Optional[dict]:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


async def get_current_user(request: Request) -> Optional[dict]:
    """Get current user from session cookie"""
    session_token = request.cookies.get("auth_token")
    if not session_token:
        return None
    return decode_session_token(session_token)


async def require_auth(request: Request) -> dict:
    """Require authentication, raise 401 if not authenticated"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user
