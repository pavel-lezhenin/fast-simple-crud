"""FastAPI demo: REST CRUD, SSE, WebSocket."""

from __future__ import annotations

from typing import Final

__version__: Final[str] = "0.1.0"

from fast_simple_crud.app import app
from fast_simple_crud.models import Item, ItemCreate, ItemUpdate, Message

__all__ = ["Item", "ItemCreate", "ItemUpdate", "Message", "app"]
