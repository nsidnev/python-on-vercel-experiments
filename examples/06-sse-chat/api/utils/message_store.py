"""Thread-safe in-memory message store for SSE chat."""

import threading
from datetime import datetime, timezone
from typing import TypedDict


class Message(TypedDict):
    """Chat message structure."""
    id: int
    username: str
    content: str
    timestamp: str


class MessageStore:
    """Thread-safe in-memory message storage."""

    def __init__(self):
        self._messages: list[Message] = []
        self._lock = threading.Lock()
        self._message_id_counter = 0

    def add_message(self, username: str, content: str) -> Message:
        """Add a new message and return it."""
        with self._lock:
            self._message_id_counter += 1
            message: Message = {
                "id": self._message_id_counter,
                "username": username,
                "content": content,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            self._messages.append(message)
            return message

    def get_all_messages(self) -> list[Message]:
        """Get all messages."""
        with self._lock:
            return self._messages.copy()

    def get_messages_since(self, since_id: int) -> list[Message]:
        """Get messages with ID greater than since_id."""
        with self._lock:
            return [msg for msg in self._messages if msg["id"] > since_id]


# Global message store instance
message_store = MessageStore()
