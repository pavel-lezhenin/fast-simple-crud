"""Pydantic models for the API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Item(BaseModel):
    """Item model."""

    id: int
    name: str
    price: float = Field(gt=0)
    is_active: bool = True


class ItemCreate(BaseModel):
    """Item creation model."""

    name: str
    price: float = Field(gt=0)
    is_active: bool = True


class ItemUpdate(BaseModel):
    """Item update model (partial)."""

    name: str | None = None
    price: float | None = Field(default=None, gt=0)
    is_active: bool | None = None


class Message(BaseModel):
    """WebSocket message model."""

    event: str
    data: str
