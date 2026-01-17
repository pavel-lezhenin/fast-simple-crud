"""Tests for FastAPI application."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient


class TestItemsCRUD:
    """Tests for CRUD endpoints."""

    @pytest.mark.asyncio
    async def test_list_items(self, client: AsyncClient) -> None:
        """Test listing items."""
        response = await client.get("/items")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_create_item(self, client: AsyncClient) -> None:
        """Test creating an item."""
        response = await client.post(
            "/items",
            json={"name": "Test", "price": 10.0},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test"
        assert data["price"] == 10.0

    @pytest.mark.asyncio
    async def test_get_item_not_found(self, client: AsyncClient) -> None:
        """Test getting non-existent item."""
        response = await client.get("/items/9999")
        assert response.status_code == 404
