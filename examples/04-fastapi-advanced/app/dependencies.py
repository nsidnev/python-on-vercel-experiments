"""
Shared dependencies for dependency injection
"""

from typing import Optional
from fastapi import Header, HTTPException, status
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# In-memory storage (resets between deployments)
products_db: list[dict] = [
    {
        "id": 1,
        "name": "Wireless Keyboard",
        "description": "Mechanical keyboard with RGB lighting",
        "price": 89.99,
        "category": "Electronics",
        "in_stock": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    },
    {
        "id": 2,
        "name": "USB-C Hub",
        "description": "7-in-1 USB-C adapter",
        "price": 49.99,
        "category": "Electronics",
        "in_stock": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    },
    {
        "id": 3,
        "name": "Desk Lamp",
        "description": "LED desk lamp with adjustable brightness",
        "price": 34.99,
        "category": "Furniture",
        "in_stock": False,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    },
]

users_db: list[dict] = [
    {
        "id": 1,
        "username": "demo_user",
        "email": "demo@example.com",
        "full_name": "Demo User",
        "is_active": True,
        "created_at": datetime.now(),
    }
]


async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> Optional[str]:
    """
    Verify API key from header (example dependency)

    In production, you would validate against a database or service.
    This is a simple example for demonstration.
    """
    # For demo purposes, we don't require an API key
    # In production, you would check x_api_key against valid keys
    if x_api_key:
        logger.info(f"API key provided: {x_api_key[:8]}...")
    return x_api_key


async def get_current_user(x_user_id: Optional[str] = Header(None)) -> Optional[dict]:
    """
    Get current user from header (example dependency)

    In production, you would decode JWT token or validate session.
    """
    if not x_user_id:
        return None

    try:
        user_id = int(x_user_id)
        user = next((u for u in users_db if u["id"] == user_id), None)
        if user:
            logger.info(f"User authenticated: {user['username']}")
        return user
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format"
        )


def get_products_db() -> list[dict]:
    """Get products database (for dependency injection)"""
    return products_db


def get_users_db() -> list[dict]:
    """Get users database (for dependency injection)"""
    return users_db
