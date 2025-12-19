"""
Sanic Basic Example

Sanic is an async Python web framework. Note: Sanic works but FastAPI is recommended
for new projects due to better type hints, validation, and documentation.
"""

from sanic import Sanic, response
from datetime import datetime

app = Sanic("sanic-vercel")


@app.route("/")
async def index(request):
    return response.json({
        "message": "Sanic on Vercel",
        "framework": "Sanic",
        "timestamp": datetime.now().isoformat(),
        "note": "Sanic works on Vercel, but FastAPI is recommended for better DX"
    })


@app.route("/api/hello/<name>")
async def hello(request, name):
    return response.json({
        "message": f"Hello, {name}!",
        "timestamp": datetime.now().isoformat()
    })


# Sanic app is ASGI-compatible and works directly with Vercel
