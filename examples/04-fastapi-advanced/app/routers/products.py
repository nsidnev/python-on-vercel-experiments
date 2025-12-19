"""
Products router - handles all product-related endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from datetime import datetime

from app.models import Product, ProductCreate, ProductUpdate
from app.dependencies import get_products_db, verify_api_key

router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=list[Product])
async def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    in_stock: Optional[bool] = Query(None, description="Filter by availability"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    db: list[dict] = Depends(get_products_db),
    api_key: Optional[str] = Depends(verify_api_key),
):
    """
    Get all products with optional filters

    - **category**: Filter by product category
    - **in_stock**: Filter by stock availability
    - **min_price**: Minimum price filter
    - **max_price**: Maximum price filter
    """
    filtered = db

    if category:
        filtered = [p for p in filtered if p["category"].lower() == category.lower()]

    if in_stock is not None:
        filtered = [p for p in filtered if p["in_stock"] == in_stock]

    if min_price is not None:
        filtered = [p for p in filtered if p["price"] >= min_price]

    if max_price is not None:
        filtered = [p for p in filtered if p["price"] <= max_price]

    return filtered


@router.get("/{product_id}", response_model=Product)
async def get_product(
    product_id: int,
    db: list[dict] = Depends(get_products_db),
    api_key: Optional[str] = Depends(verify_api_key),
):
    """Get a specific product by ID"""
    product = next((p for p in db if p["id"] == product_id), None)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found",
        )

    return product


@router.post("", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: list[dict] = Depends(get_products_db),
    api_key: Optional[str] = Depends(verify_api_key),
):
    """
    Create a new product

    - **name**: Product name (required)
    - **description**: Product description
    - **price**: Product price (must be positive)
    - **category**: Product category (required)
    - **in_stock**: Whether product is in stock (default: true)
    """
    new_id = max([p["id"] for p in db]) + 1 if db else 1

    new_product = {
        "id": new_id,
        **product.model_dump(),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    db.append(new_product)
    return new_product


@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: list[dict] = Depends(get_products_db),
    api_key: Optional[str] = Depends(verify_api_key),
):
    """
    Update an existing product (partial updates supported)

    Only provided fields will be updated.
    """
    product = next((p for p in db if p["id"] == product_id), None)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found",
        )

    # Update only provided fields
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        product[field] = value

    product["updated_at"] = datetime.now()

    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: list[dict] = Depends(get_products_db),
    api_key: Optional[str] = Depends(verify_api_key),
):
    """Delete a product by ID"""
    product = next((p for p in db if p["id"] == product_id), None)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found",
        )

    db.remove(product)
    return None


@router.get("/search/query", response_model=list[Product])
async def search_products(
    q: str = Query(..., min_length=1, description="Search query"),
    db: list[dict] = Depends(get_products_db),
    api_key: Optional[str] = Depends(verify_api_key),
):
    """
    Search products by name or description

    - **q**: Search query (searches in name and description)
    """
    query_lower = q.lower()
    results = [
        p
        for p in db
        if query_lower in p["name"].lower()
        or (p.get("description") and query_lower in p["description"].lower())
    ]

    return results
