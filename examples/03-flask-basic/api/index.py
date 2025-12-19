"""
Flask Basic Example

Demonstrates Flask on Vercel with:
- Traditional web framework patterns
- JSON API endpoints
- Request/response handling
- Query parameters and path variables
"""

from flask import Flask, jsonify, request, abort
from datetime import datetime
from typing import List, Dict, Optional

# Create Flask app
app = Flask(__name__)


# In-memory storage (resets between deployments)
items_db: List[Dict] = [
    {"id": 1, "name": "Laptop", "description": "High-performance laptop", "price": 999.99, "in_stock": True, "created_at": "2024-01-01T10:00:00"},
    {"id": 2, "name": "Mouse", "description": "Wireless mouse", "price": 29.99, "in_stock": True, "created_at": "2024-01-02T11:00:00"},
    {"id": 3, "name": "Keyboard", "description": "Mechanical keyboard", "price": 79.99, "in_stock": False, "created_at": "2024-01-03T12:00:00"},
]


@app.route("/")
def root():
    """
    Root endpoint - Health check

    Returns welcome message and timestamp
    """
    return jsonify({
        "message": "Welcome to Flask on Vercel!",
        "timestamp": datetime.now().isoformat()
    })


@app.route("/api")
def api_info():
    """
    API information endpoint

    Returns API metadata and available endpoints
    """
    return jsonify({
        "name": "Flask on Vercel",
        "version": "1.0.0",
        "framework": "Flask",
        "runtime": "Python 3.12",
        "platform": "Vercel Serverless",
        "example": "03-flask-basic",
        "endpoints": {
            "/": "Welcome message",
            "/api": "This endpoint",
            "/api/items": "List all items (GET), Create item (POST)",
            "/api/items/<item_id>": "Get/Update/Delete specific item",
            "/api/items/search": "Search items",
            "/api/health": "Health check"
        }
    })


@app.route("/api/items", methods=["GET"])
def list_items():
    """
    List all items with optional filters

    Query Parameters:
    - in_stock: Filter by stock availability (true/false)
    - min_price: Minimum price filter
    - max_price: Maximum price filter
    """
    filtered_items = items_db.copy()

    # Filter by stock
    in_stock_param = request.args.get("in_stock")
    if in_stock_param is not None:
        in_stock = in_stock_param.lower() == "true"
        filtered_items = [item for item in filtered_items if item["in_stock"] == in_stock]

    # Filter by price range
    min_price = request.args.get("min_price", type=float)
    if min_price is not None:
        filtered_items = [item for item in filtered_items if item["price"] >= min_price]

    max_price = request.args.get("max_price", type=float)
    if max_price is not None:
        filtered_items = [item for item in filtered_items if item["price"] <= max_price]

    return jsonify(filtered_items)


@app.route("/api/items/<int:item_id>", methods=["GET"])
def get_item(item_id: int):
    """
    Get a specific item by ID

    Path Parameters:
    - item_id: Item ID (integer)

    Returns:
    - 404: Item not found
    """
    item = next((item for item in items_db if item["id"] == item_id), None)

    if item is None:
        abort(404, description=f"Item with id {item_id} not found")

    return jsonify(item)


@app.route("/api/items/search", methods=["GET"])
def search_items():
    """
    Search items by name or description

    Query Parameters:
    - q: Search query (required)

    Returns items where the query matches name or description (case-insensitive)
    """
    query = request.args.get("q", "").strip()

    if not query:
        abort(400, description="Query parameter 'q' is required")

    query_lower = query.lower()
    results = [
        item for item in items_db
        if query_lower in item["name"].lower() or
        (item.get("description") and query_lower in item["description"].lower())
    ]

    return jsonify(results)


@app.route("/api/items", methods=["POST"])
def create_item():
    """
    Create a new item

    Request Body (JSON):
    - name: Item name (required, 1-100 characters)
    - description: Item description (optional, max 500 characters)
    - price: Item price (required, must be positive)
    - in_stock: Stock availability (optional, defaults to True)

    Returns the created item with auto-generated ID and timestamp
    """
    data = request.get_json()

    if not data:
        abort(400, description="Request body is required")

    # Validate required fields
    if "name" not in data or not data["name"]:
        abort(400, description="Field 'name' is required")

    if "price" not in data:
        abort(400, description="Field 'price' is required")

    # Validate field constraints
    name = data["name"].strip()
    if len(name) < 1 or len(name) > 100:
        abort(400, description="Field 'name' must be between 1 and 100 characters")

    try:
        price = float(data["price"])
        if price <= 0:
            abort(400, description="Field 'price' must be positive")
    except (ValueError, TypeError):
        abort(400, description="Field 'price' must be a number")

    description = data.get("description", "").strip()
    if description and len(description) > 500:
        abort(400, description="Field 'description' must be max 500 characters")

    in_stock = data.get("in_stock", True)

    # Generate new ID
    new_id = max([item["id"] for item in items_db]) + 1 if items_db else 1

    # Create item
    new_item = {
        "id": new_id,
        "name": name,
        "description": description if description else None,
        "price": price,
        "in_stock": in_stock,
        "created_at": datetime.now().isoformat()
    }

    items_db.append(new_item)

    return jsonify(new_item), 201


@app.route("/api/items/<int:item_id>", methods=["PUT"])
def update_item(item_id: int):
    """
    Update an existing item

    Path Parameters:
    - item_id: Item ID to update

    Request Body (JSON):
    - Updated item data

    Returns:
    - 404: Item not found
    """
    item = next((item for item in items_db if item["id"] == item_id), None)

    if item is None:
        abort(404, description=f"Item with id {item_id} not found")

    data = request.get_json()

    if not data:
        abort(400, description="Request body is required")

    # Update fields with validation
    if "name" in data:
        name = data["name"].strip()
        if len(name) < 1 or len(name) > 100:
            abort(400, description="Field 'name' must be between 1 and 100 characters")
        item["name"] = name

    if "description" in data:
        description = data["description"].strip() if data["description"] else None
        if description and len(description) > 500:
            abort(400, description="Field 'description' must be max 500 characters")
        item["description"] = description

    if "price" in data:
        try:
            price = float(data["price"])
            if price <= 0:
                abort(400, description="Field 'price' must be positive")
            item["price"] = price
        except (ValueError, TypeError):
            abort(400, description="Field 'price' must be a number")

    if "in_stock" in data:
        item["in_stock"] = bool(data["in_stock"])

    return jsonify(item)


@app.route("/api/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id: int):
    """
    Delete an item

    Path Parameters:
    - item_id: Item ID to delete

    Returns:
    - 404: Item not found
    """
    item = next((item for item in items_db if item["id"] == item_id), None)

    if item is None:
        abort(404, description=f"Item with id {item_id} not found")

    items_db.remove(item)

    return jsonify({
        "message": f"Item {item_id} deleted successfully",
        "timestamp": datetime.now().isoformat()
    })


@app.route("/api/health")
def health_check():
    """
    Health check endpoint

    Returns application health status
    """
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "items_count": len(items_db)
    })


# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Not Found",
        "message": str(error.description) if hasattr(error, 'description') else "The requested resource was not found"
    }), 404


@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors"""
    return jsonify({
        "error": "Bad Request",
        "message": str(error.description) if hasattr(error, 'description') else "Invalid request"
    }), 400


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred"
    }), 500
