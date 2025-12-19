"""
Simple API - Health Check and Info Endpoint

This demonstrates the simplest possible Vercel Python function
using file-based routing without any framework.
"""

from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime


class handler(BaseHTTPRequestHandler):
    """
    Basic HTTP handler for the root API endpoint.

    Vercel automatically calls this handler for requests to /api or /api/index
    """

    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response = {
            "message": "Welcome to Python on Vercel!",
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "endpoints": {
                "/api": "This endpoint (health check)",
                "/api/users": "User CRUD operations",
            },
            "vercel_info": {
                "runtime": "Python 3.12",
                "platform": "Vercel Serverless",
                "example": "01-simple-api"
            }
        }

        self.wfile.write(json.dumps(response, indent=2).encode())

    def do_POST(self):
        """Handle POST requests"""
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error = {"error": "Invalid JSON"}
            self.wfile.write(json.dumps(error).encode())
            return

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response = {
            "message": "Data received successfully",
            "received_data": data,
            "timestamp": datetime.now().isoformat()
        }

        self.wfile.write(json.dumps(response, indent=2).encode())
