"""
Users router - handles all user-related endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime

from app.models import User, UserCreate
from app.dependencies import get_users_db, verify_api_key

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=list[User])
async def list_users(
    active_only: bool = False,
    db: list[dict] = Depends(get_users_db),
    api_key: Optional[str] = Depends(verify_api_key),
):
    """
    Get all users

    - **active_only**: Only return active users
    """
    if active_only:
        return [u for u in db if u.get("is_active", True)]
    return db


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: list[dict] = Depends(get_users_db),
    api_key: Optional[str] = Depends(verify_api_key),
):
    """Get a specific user by ID"""
    user = next((u for u in db if u["id"] == user_id), None)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    return user


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: list[dict] = Depends(get_users_db),
    api_key: Optional[str] = Depends(verify_api_key),
):
    """
    Create a new user

    - **username**: Username (3-50 chars, alphanumeric + underscore/hyphen)
    - **email**: Email address
    - **full_name**: Full name (optional)
    - **password**: Password (min 8 chars) - not stored in this demo
    """
    # Check if username already exists
    if any(u["username"] == user.username for u in db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    # Check if email already exists
    if any(u["email"] == user.email for u in db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
        )

    new_id = max([u["id"] for u in db]) + 1 if db else 1

    # In production, hash the password!
    # For demo, we don't store it at all
    new_user = {
        "id": new_id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": True,
        "created_at": datetime.now(),
    }

    db.append(new_user)
    return new_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: list[dict] = Depends(get_users_db),
    api_key: Optional[str] = Depends(verify_api_key),
):
    """Delete a user by ID"""
    user = next((u for u in db if u["id"] == user_id), None)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    db.remove(user)
    return None
