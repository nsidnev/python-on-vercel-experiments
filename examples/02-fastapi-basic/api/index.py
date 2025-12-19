"""
FastAPI Basic Example

Demonstrates FastAPI on Vercel with:
- Automatic OpenAPI documentation
- Request/response validation with Pydantic
- Path and query parameters
- Modern Python type hints
"""

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="FastAPI on Vercel",
    description="A simple FastAPI application demonstrating Vercel deployment",
    version="1.0.0"
)


# Pydantic models for request/response validation
class Item(BaseModel):
    """Item model with automatic validation"""
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=100, description="Item name")
    description: Optional[str] = Field(None, max_length=500, description="Item description")
    price: float = Field(..., gt=0, description="Item price (must be positive)")
    in_stock: bool = Field(True, description="Whether item is in stock")
    created_at: Optional[str] = None


class Message(BaseModel):
    """Simple message response"""
    message: str
    timestamp: str


# In-memory storage (resets between deployments)
items_db: List[Item] = [
    Item(id=1, name="Laptop", description="High-performance laptop", price=999.99, in_stock=True, created_at="2024-01-01T10:00:00"),
    Item(id=2, name="Mouse", description="Wireless mouse", price=29.99, in_stock=True, created_at="2024-01-02T11:00:00"),
    Item(id=3, name="Keyboard", description="Mechanical keyboard", price=79.99, in_stock=False, created_at="2024-01-03T12:00:00"),
]


@app.get("/", response_model=Message)
async def root():
    """
    Root endpoint - Health check

    Returns welcome message and timestamp
    """
    return Message(
        message="Welcome to FastAPI on Vercel! Visit /docs for interactive API documentation.",
        timestamp=datetime.now().isoformat()
    )


@app.get("/api", response_model=dict)
async def api_info():
    """
    API information endpoint

    Returns API metadata and available endpoints
    """
    return {
        "name": "FastAPI on Vercel",
        "version": "1.0.0",
        "framework": "FastAPI",
        "runtime": "Python 3.12",
        "platform": "Vercel Serverless",
        "example": "02-fastapi-basic",
        "documentation": "/docs",
        "endpoints": {
            "/": "Welcome message",
            "/api": "This endpoint",
            "/api/items": "List all items",
            "/api/items/{item_id}": "Get specific item",
            "/api/items/search": "Search items",
            "/docs": "Interactive API documentation (Swagger UI)",
            "/redoc": "API documentation (ReDoc)"
        }
    }


@app.get("/api/items", response_model=List[Item])
async def list_items(
    in_stock: Optional[bool] = Query(None, description="Filter by stock availability"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price")
):
    """
    List all items with optional filters

    Query Parameters:
    - in_stock: Filter by stock availability (true/false)
    - min_price: Minimum price filter
    - max_price: Maximum price filter
    """
    filtered_items = items_db

    # Filter by stock
    if in_stock is not None:
        filtered_items = [item for item in filtered_items if item.in_stock == in_stock]

    # Filter by price range
    if min_price is not None:
        filtered_items = [item for item in filtered_items if item.price >= min_price]
    if max_price is not None:
        filtered_items = [item for item in filtered_items if item.price <= max_price]

    return filtered_items


@app.get("/api/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    """
    Get a specific item by ID

    Path Parameters:
    - item_id: Item ID (integer)

    Raises:
    - 404: Item not found
    """
    item = next((item for item in items_db if item.id == item_id), None)

    if item is None:
        raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")

    return item


@app.get("/api/items/search", response_model=List[Item])
async def search_items(
    q: str = Query(..., min_length=1, description="Search query")
):
    """
    Search items by name or description

    Query Parameters:
    - q: Search query (minimum 1 character)

    Returns items where the query matches name or description (case-insensitive)
    """
    query_lower = q.lower()
    results = [
        item for item in items_db
        if query_lower in item.name.lower() or
        (item.description and query_lower in item.description.lower())
    ]

    return results


@app.post("/api/items", response_model=Item, status_code=201)
async def create_item(item: Item):
    """
    Create a new item

    Request Body:
    - Item object with name, price, and optional description

    Automatically validates:
    - name: 1-100 characters
    - price: Must be positive
    - description: Max 500 characters

    Returns the created item with auto-generated ID and timestamp
    """
    # Generate new ID
    new_id = max([item.id for item in items_db]) + 1 if items_db else 1

    # Create item with ID and timestamp
    new_item = Item(
        id=new_id,
        name=item.name,
        description=item.description,
        price=item.price,
        in_stock=item.in_stock,
        created_at=datetime.now().isoformat()
    )

    items_db.append(new_item)

    return new_item


@app.put("/api/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: Item):
    """
    Update an existing item

    Path Parameters:
    - item_id: Item ID to update

    Request Body:
    - Updated item data

    Raises:
    - 404: Item not found
    """
    existing_item = next((item for item in items_db if item.id == item_id), None)

    if existing_item is None:
        raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")

    # Update fields
    existing_item.name = item.name
    existing_item.description = item.description
    existing_item.price = item.price
    existing_item.in_stock = item.in_stock

    return existing_item


@app.delete("/api/items/{item_id}", response_model=Message)
async def delete_item(item_id: int):
    """
    Delete an item

    Path Parameters:
    - item_id: Item ID to delete

    Raises:
    - 404: Item not found
    """
    item = next((item for item in items_db if item.id == item_id), None)

    if item is None:
        raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")

    items_db.remove(item)

    return Message(
        message=f"Item {item_id} deleted successfully",
        timestamp=datetime.now().isoformat()
    )


@app.get("/api/health", response_model=dict)
async def health_check():
    """
    Health check endpoint

    Returns application health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "items_count": len(items_db)
    }
