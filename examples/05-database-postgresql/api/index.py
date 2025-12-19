"""
FastAPI application with PostgreSQL database

This example demonstrates:
- SQLAlchemy ORM with PostgreSQL
- Connection pooling for serverless
- CRUD operations
- Database migrations
"""

from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import logging

from app.database import get_db_dependency, test_connection
from app import models, schemas

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PostgreSQL on Vercel",
    description="FastAPI with PostgreSQL database and connection pooling",
    version="1.0.0",
)


@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to PostgreSQL on Vercel!",
        "framework": "FastAPI + SQLAlchemy",
        "database": "PostgreSQL (Neon)",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "/": "This endpoint",
            "/api/health": "Database health check",
            "/api/tasks": "Task management (CRUD)",
            "/api/products": "Product management (CRUD)",
            "/docs": "Interactive API documentation",
        },
    }


@app.get("/api/health", response_model=schemas.DatabaseHealth)
async def health_check(db: Session = Depends(get_db_dependency)):
    """
    Health check endpoint with database connection test

    Returns database connection status and record counts.
    """
    try:
        db_connected = test_connection()

        # Get record counts
        tasks_count = db.query(models.Task).count()
        products_count = db.query(models.Product).count()

        return schemas.DatabaseHealth(
            status="healthy" if db_connected else "unhealthy",
            database_connected=db_connected,
            timestamp=datetime.now(),
            total_tasks=tasks_count,
            total_products=products_count,
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}",
        )


# ===== TASKS ENDPOINTS =====


@app.get("/api/tasks", response_model=list[schemas.Task])
async def list_tasks(
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    priority: Optional[str] = Query(None, description="Filter by priority (low/medium/high)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db_dependency),
):
    """
    Get all tasks with optional filters

    - **completed**: Filter by completion status
    - **priority**: Filter by priority level
    - **skip**: Pagination offset
    - **limit**: Maximum records to return
    """
    query = db.query(models.Task)

    if completed is not None:
        query = query.filter(models.Task.completed == completed)

    if priority:
        query = query.filter(models.Task.priority == priority)

    tasks = query.order_by(models.Task.created_at.desc()).offset(skip).limit(limit).all()

    return tasks


@app.get("/api/tasks/{task_id}", response_model=schemas.Task)
async def get_task(task_id: int, db: Session = Depends(get_db_dependency)):
    """Get a specific task by ID"""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with id {task_id} not found"
        )

    return task


@app.post("/api/tasks", response_model=schemas.Task, status_code=status.HTTP_201_CREATED)
async def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db_dependency)):
    """
    Create a new task

    - **title**: Task title (required)
    - **description**: Task description
    - **priority**: Priority level (low/medium/high)
    """
    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    logger.info(f"Created task: {db_task.id} - {db_task.title}")
    return db_task


@app.put("/api/tasks/{task_id}", response_model=schemas.Task)
async def update_task(
    task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db_dependency)
):
    """
    Update an existing task (partial updates supported)

    Only provided fields will be updated.
    """
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with id {task_id} not found"
        )

    # Update only provided fields
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    logger.info(f"Updated task: {task.id} - {task.title}")
    return task


@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: Session = Depends(get_db_dependency)):
    """Delete a task by ID"""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with id {task_id} not found"
        )

    db.delete(task)
    db.commit()

    logger.info(f"Deleted task: {task_id}")
    return None


# ===== PRODUCTS ENDPOINTS =====


@app.get("/api/products", response_model=list[schemas.Product])
async def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock availability"),
    active_only: bool = Query(True, description="Only return active products"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db_dependency),
):
    """
    Get all products with optional filters

    - **category**: Filter by product category
    - **in_stock**: Filter by stock availability
    - **active_only**: Only show active products
    - **skip**: Pagination offset
    - **limit**: Maximum records to return
    """
    query = db.query(models.Product)

    if active_only:
        query = query.filter(models.Product.is_active == True)

    if category:
        query = query.filter(models.Product.category == category)

    if in_stock is not None:
        if in_stock:
            query = query.filter(models.Product.stock_quantity > 0)
        else:
            query = query.filter(models.Product.stock_quantity == 0)

    products = query.order_by(models.Product.created_at.desc()).offset(skip).limit(limit).all()

    return products


@app.get("/api/products/{product_id}", response_model=schemas.Product)
async def get_product(product_id: int, db: Session = Depends(get_db_dependency)):
    """Get a specific product by ID"""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found",
        )

    return product


@app.post("/api/products", response_model=schemas.Product, status_code=status.HTTP_201_CREATED)
async def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db_dependency)):
    """
    Create a new product

    - **name**: Product name (required)
    - **description**: Product description
    - **price**: Product price (must be positive)
    - **sku**: Stock keeping unit (must be unique)
    - **stock_quantity**: Initial stock quantity
    - **category**: Product category
    """
    # Check if SKU already exists
    existing = db.query(models.Product).filter(models.Product.sku == product.sku).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with SKU '{product.sku}' already exists",
        )

    db_product = models.Product(**product.model_dump(), is_active=True)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    logger.info(f"Created product: {db_product.id} - {db_product.name} ({db_product.sku})")
    return db_product


@app.put("/api/products/{product_id}", response_model=schemas.Product)
async def update_product(
    product_id: int, product_update: schemas.ProductUpdate, db: Session = Depends(get_db_dependency)
):
    """
    Update an existing product (partial updates supported)

    Only provided fields will be updated.
    """
    product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found",
        )

    # Update only provided fields
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    logger.info(f"Updated product: {product.id} - {product.name}")
    return product


@app.delete("/api/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: Session = Depends(get_db_dependency)):
    """Delete a product by ID"""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found",
        )

    db.delete(product)
    db.commit()

    logger.info(f"Deleted product: {product_id}")
    return None
