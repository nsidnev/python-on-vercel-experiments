"""
Native Libraries Test

This example tests Python packages with native C/Rust extensions on Vercel.
Testing: orjson (Rust) and immutables (C)
"""

from fastapi import FastAPI
from fastapi.responses import Response
from datetime import datetime
import sys
import platform

app = FastAPI(
    title="Native Libraries on Vercel",
    description="Testing orjson (Rust) and immutables (C)",
    version="1.0.0",
)


@app.get("/")
async def root():
    """Welcome endpoint with library status"""
    libraries = {
        "orjson": False,
        "immutables": False,
    }

    # Test orjson (Rust-based fast JSON)
    try:
        import orjson
        libraries["orjson"] = orjson.__version__
    except ImportError:
        pass

    # Test immutables (C-based immutable maps)
    try:
        import immutables
        libraries["immutables"] = immutables.__version__
    except ImportError:
        pass

    return {
        "message": "Native Libraries Test on Vercel",
        "timestamp": datetime.now().isoformat(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "libraries": libraries,
        "endpoints": {
            "/": "This endpoint",
            "/test/immutables-orjson": "Test immutables (C) + orjson (Rust)",
            "/docs": "API documentation",
        },
    }


@app.get("/test/immutables-orjson")
async def test_immutables_orjson():
    """Test immutables (C) + orjson (Rust) for fast JSON serialization"""
    try:
        import immutables
        import orjson

        # Create an immutable map (C-based implementation)
        config_map = immutables.Map()
        config_map = config_map.set("app_name", "Vercel Python")
        config_map = config_map.set("max_connections", 100)
        config_map = config_map.set("timeout", 30.5)
        config_map = config_map.set("features", ["sse", "websockets", "http2"])
        config_map = config_map.set("enabled", True)

        # Add nested structure
        nested = immutables.Map()
        nested = nested.set("host", "vercel.com")
        nested = nested.set("port", 443)
        config_map = config_map.set("server", dict(nested.items()))

        # Convert to dict for serialization
        config_dict = dict(config_map.items())

        # Build response data
        response_data = {
            "status": "success",
            "immutables_version": immutables.__version__,
            "orjson_version": orjson.__version__,
            "test_results": {
                "map_size": len(config_map),
                "map_keys": list(config_map.keys()),
                "config": config_dict,
                "immutability_test": {
                    "original_timeout": config_map.get("timeout"),
                    "map_is_immutable": True,
                    "note": "Attempting to modify returns a new map instance",
                },
            },
            "note": "immutables uses C for fast immutable mappings, orjson uses Rust for fast JSON encoding",
        }

        # Use orjson to serialize (much faster than standard json)
        json_bytes = orjson.dumps(response_data)

        return Response(content=json_bytes, media_type="application/json")

    except ImportError as e:
        return {"status": "error", "message": f"Library not available: {e}"}
