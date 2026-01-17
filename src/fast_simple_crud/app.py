"""FastAPI application with REST, SSE, and WebSocket endpoints."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager, suppress
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from sse_starlette.sse import EventSourceResponse

from fast_simple_crud.models import Item, ItemCreate, ItemUpdate, Message

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, AsyncIterator


# In-memory storage
db: dict[int, Item] = {}
counter: int = 0
websocket_clients: list[WebSocket] = []


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # noqa: ARG001
    """Application lifespan: startup and shutdown."""
    global counter  # noqa: PLW0603
    for i in range(1, 4):
        db[i] = Item(id=i, name=f"Item {i}", price=i * 10.0)
        counter = i
    yield
    db.clear()


app = FastAPI(
    title="Fast Simple CRUD",
    description="Demo: REST API, SSE, WebSocket",
    version="0.1.0",
    lifespan=lifespan,
)


# =============================================================================
# REST CRUD Endpoints
# =============================================================================


@app.get("/items", response_model=list[Item], tags=["REST"])
async def list_items() -> list[Item]:
    """Get all items."""
    return list(db.values())


@app.get("/items/{item_id}", response_model=Item, tags=["REST"])
async def get_item(item_id: int) -> Item:
    """Get item by ID."""
    if item_id not in db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return db[item_id]


@app.post(
    "/items",
    response_model=Item,
    status_code=status.HTTP_201_CREATED,
    tags=["REST"],
)
async def create_item(item: ItemCreate) -> Item:
    """Create new item."""
    global counter  # noqa: PLW0603
    counter += 1
    new_item = Item(id=counter, **item.model_dump())
    db[counter] = new_item
    await broadcast(f"Item created: {new_item.name}")
    return new_item


@app.put("/items/{item_id}", response_model=Item, tags=["REST"])
async def update_item(item_id: int, item: ItemCreate) -> Item:
    """Full update of item."""
    if item_id not in db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    updated = Item(id=item_id, **item.model_dump())
    db[item_id] = updated
    await broadcast(f"Item updated: {updated.name}")
    return updated


@app.patch("/items/{item_id}", response_model=Item, tags=["REST"])
async def patch_item(item_id: int, item: ItemUpdate) -> Item:
    """Partial update of item."""
    if item_id not in db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    current = db[item_id]
    update_data = item.model_dump(exclude_unset=True)
    updated = current.model_copy(update=update_data)
    db[item_id] = updated
    await broadcast(f"Item patched: {updated.name}")
    return updated


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["REST"])
async def delete_item(item_id: int) -> None:
    """Delete item."""
    if item_id not in db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    name = db[item_id].name
    del db[item_id]
    await broadcast(f"Item deleted: {name}")


# =============================================================================
# SSE (Server-Sent Events)
# =============================================================================


async def event_generator() -> AsyncGenerator[dict[str, str], None]:
    """Generate SSE events every second."""
    while True:
        now = datetime.now(tz=UTC).isoformat()
        yield {"event": "tick", "data": f"Server time: {now}"}
        await asyncio.sleep(1)


@app.get("/sse/stream", tags=["SSE"])
async def sse_stream() -> EventSourceResponse:
    """SSE endpoint: streams server time every second."""
    return EventSourceResponse(event_generator())


# =============================================================================
# WebSocket
# =============================================================================


async def broadcast(message: str) -> None:
    """Broadcast message to all connected WebSocket clients."""
    for client in websocket_clients:
        with suppress(Exception):
            await client.send_json({"event": "broadcast", "data": message})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time communication."""
    await websocket.accept()
    websocket_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            msg = Message(**data)
            # Echo back with server acknowledgment
            await websocket.send_json(
                {
                    "event": "echo",
                    "data": f"Received: {msg.data}",
                }
            )
    except WebSocketDisconnect:
        websocket_clients.remove(websocket)
