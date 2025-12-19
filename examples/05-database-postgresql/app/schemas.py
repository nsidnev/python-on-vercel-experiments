"""
Pydantic schemas for request/response validation
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# Task Schemas
class TaskBase(BaseModel):
    """Base task schema"""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    priority: str = Field("medium", pattern="^(low|medium|high)$", description="Task priority")


class TaskCreate(TaskBase):
    """Schema for creating a task"""

    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task (all fields optional)"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")


class Task(TaskBase):
    """Full task schema with database fields"""

    id: int
    completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Product Schemas
class ProductBase(BaseModel):
    """Base product schema"""

    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., gt=0, description="Product price (must be positive)")
    sku: str = Field(..., min_length=1, max_length=50, description="Stock keeping unit (SKU)")
    stock_quantity: int = Field(0, ge=0, description="Stock quantity")
    category: str = Field(..., min_length=1, max_length=100, description="Product category")


class ProductCreate(ProductBase):
    """Schema for creating a product"""

    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product (all fields optional)"""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None


class Product(ProductBase):
    """Full product schema with database fields"""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Health Check Schema
class DatabaseHealth(BaseModel):
    """Database health check response"""

    status: str
    database_connected: bool
    timestamp: datetime
    total_tasks: int
    total_products: int
