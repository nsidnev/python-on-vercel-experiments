"""
BlackSheep Basic Example

BlackSheep is a fast async Python web framework.
"""

from blacksheep import Application, get, json
from datetime import datetime

app = Application()


@get("/")
async def index():
    return json({
        "message": "BlackSheep on Vercel",
        "framework": "BlackSheep",
        "timestamp": datetime.now().isoformat(),
        "note": "BlackSheep is a fast async framework with ASGI support"
    })


@get("/api/hello/{name}")
async def hello(name: str):
    return json({
        "message": f"Hello, {name}!",
        "timestamp": datetime.now().isoformat()
    })


# BlackSheep app is ASGI-compatible
