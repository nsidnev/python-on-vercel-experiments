"""SSE Chat API with FastAPI."""

import asyncio
import json
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .utils.message_store import message_store


app = FastAPI(title="SSE Chat API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MessageCreate(BaseModel):
    """Request model for creating a message."""
    username: str
    content: str


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "SSE Chat API"}


@app.get("/api/messages")
async def get_messages():
    """Get all messages."""
    messages = message_store.get_all_messages()
    return {"messages": messages}


@app.post("/api/messages")
async def create_message(message: MessageCreate):
    """Create a new message."""
    new_message = message_store.add_message(
        username=message.username,
        content=message.content
    )
    return {"message": new_message}


async def message_generator() -> AsyncGenerator[bytes, None]:
    """Generate SSE events for new messages."""
    last_id = 0

    while True:
        # Check for new messages
        new_messages = message_store.get_messages_since(last_id)

        if new_messages:
            for msg in new_messages:
                # Send message as SSE event
                event_data = {
                    "type": "message",
                    "message": msg
                }
                data = json.dumps(event_data)
                # Yield as bytes to force immediate flushing (no buffering)
                yield f"data: {data}\n\n".encode("utf-8")
                last_id = msg["id"]

        # Wait before checking again
        await asyncio.sleep(0.5)


@app.get("/api/stream")
async def stream_messages():
    """SSE endpoint for streaming new messages."""
    return StreamingResponse(
        message_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
