"""
Pydantic models for request/response validation
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ProductBase(BaseModel):
    """Base product schema"""

    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    description: Optional[str] = Field(None, max_length=1000, description="Product description")
    price: float = Field(..., gt=0, description="Product price (must be positive)")
    category: str = Field(..., min_length=1, max_length=50, description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")


class ProductCreate(ProductBase):
    """Schema for creating a product"""

    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product (all fields optional)"""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    in_stock: Optional[bool] = None


class Product(ProductBase):
    """Full product schema with ID and timestamps"""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    """Base user schema"""

    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    email: str = Field(..., max_length=100, description="User email address")
    full_name: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """Schema for creating a user"""

    password: str = Field(..., min_length=8, max_length=100)


class User(UserBase):
    """Full user schema (without password)"""

    id: int
    is_active: bool = True
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HealthCheck(BaseModel):
    """Health check response"""

    status: str
    timestamp: datetime
    version: str
    environment: str


class ErrorResponse(BaseModel):
    """Standard error response"""

    error: str
    detail: Optional[str] = None
    timestamp: datetime
