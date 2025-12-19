"""
Users API - Simple CRUD Operations

This demonstrates file-based routing with in-memory data storage.
Accessible at /api/users
"""

from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import json
from datetime import datetime


# In-memory user storage (resets on each function invocation)
# In production, use a database instead
USERS = [
    {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "created_at": "2024-01-01T10:00:00"},
    {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "created_at": "2024-01-02T11:30:00"},
    {"id": 3, "name": "Charlie Brown", "email": "charlie@example.com", "created_at": "2024-01-03T14:15:00"},
]


class handler(BaseHTTPRequestHandler):
    """Handler for /api/users endpoint"""

    def do_GET(self):
        """
        Get all users or filter by query parameters

        Query params:
        - name: Filter by name (partial match)
        - id: Get specific user by ID
        """
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        # Filter by ID
        if 'id' in query_params:
            user_id = int(query_params['id'][0])
            user = next((u for u in USERS if u['id'] == user_id), None)

            if user:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(user, indent=2).encode())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error = {"error": f"User with id {user_id} not found"}
                self.wfile.write(json.dumps(error).encode())
            return

        # Filter by name
        if 'name' in query_params:
            name_filter = query_params['name'][0].lower()
            filtered_users = [u for u in USERS if name_filter in u['name'].lower()]

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "users": filtered_users,
                "count": len(filtered_users),
                "filter": name_filter
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            return

        # Return all users
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {
            "users": USERS,
            "count": len(USERS),
            "timestamp": datetime.now().isoformat()
        }
        self.wfile.write(json.dumps(response, indent=2).encode())

    def do_POST(self):
        """
        Create a new user

        Expected JSON body:
        {
            "name": "John Doe",
            "email": "john@example.com"
        }
        """
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error = {"error": "Invalid JSON"}
            self.wfile.write(json.dumps(error).encode())
            return

        # Validate required fields
        if 'name' not in data or 'email' not in data:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error = {"error": "Missing required fields: name, email"}
            self.wfile.write(json.dumps(error).encode())
            return

        # Create new user
        new_user = {
            "id": max([u['id'] for u in USERS]) + 1 if USERS else 1,
            "name": data['name'],
            "email": data['email'],
            "created_at": datetime.now().isoformat()
        }

        USERS.append(new_user)

        self.send_response(201)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {
            "message": "User created successfully",
            "user": new_user,
            "note": "Data is stored in-memory and will reset on next deployment"
        }
        self.wfile.write(json.dumps(response, indent=2).encode())

    def do_PUT(self):
        """
        Update a user

        Query param: id (required)
        Expected JSON body (partial updates allowed):
        {
            "name": "Updated Name",
            "email": "updated@example.com"
        }
        """
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        if 'id' not in query_params:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error = {"error": "Missing required query parameter: id"}
            self.wfile.write(json.dumps(error).encode())
            return

        user_id = int(query_params['id'][0])
        user = next((u for u in USERS if u['id'] == user_id), None)

        if not user:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error = {"error": f"User with id {user_id} not found"}
            self.wfile.write(json.dumps(error).encode())
            return

        # Read update data
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error = {"error": "Invalid JSON"}
            self.wfile.write(json.dumps(error).encode())
            return

        # Update user fields
        if 'name' in data:
            user['name'] = data['name']
        if 'email' in data:
            user['email'] = data['email']

        user['updated_at'] = datetime.now().isoformat()

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {
            "message": "User updated successfully",
            "user": user
        }
        self.wfile.write(json.dumps(response, indent=2).encode())

    def do_DELETE(self):
        """
        Delete a user

        Query param: id (required)
        """
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        if 'id' not in query_params:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error = {"error": "Missing required query parameter: id"}
            self.wfile.write(json.dumps(error).encode())
            return

        user_id = int(query_params['id'][0])
        user = next((u for u in USERS if u['id'] == user_id), None)

        if not user:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error = {"error": f"User with id {user_id} not found"}
            self.wfile.write(json.dumps(error).encode())
            return

        USERS.remove(user)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {
            "message": "User deleted successfully",
            "deleted_user": user
        }
        self.wfile.write(json.dumps(response, indent=2).encode())
