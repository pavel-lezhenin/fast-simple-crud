"""Tests for FastAPI application."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

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
    async def test_get_item(self, client: AsyncClient) -> None:
        """Test getting existing item."""
        response = await client.get("/items/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1

    @pytest.mark.asyncio
    async def test_get_item_not_found(self, client: AsyncClient) -> None:
        """Test getting non-existent item."""
        response = await client.get("/items/9999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_item(self, client: AsyncClient) -> None:
        """Test full update of item."""
        response = await client.put(
            "/items/1",
            json={"name": "Updated", "price": 99.0},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated"
        assert data["price"] == 99.0

    @pytest.mark.asyncio
    async def test_update_item_not_found(self, client: AsyncClient) -> None:
        """Test update of non-existent item."""
        response = await client.put(
            "/items/9999",
            json={"name": "X", "price": 1.0},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_patch_item(self, client: AsyncClient) -> None:
        """Test partial update of item."""
        # Create item first
        create_resp = await client.post(
            "/items", json={"name": "ToPatch", "price": 50.0}
        )
        item_id = create_resp.json()["id"]
        response = await client.patch(
            f"/items/{item_id}",
            json={"name": "Patched"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Patched"

    @pytest.mark.asyncio
    async def test_patch_item_not_found(self, client: AsyncClient) -> None:
        """Test patch of non-existent item."""
        response = await client.patch(
            "/items/9999",
            json={"name": "X"},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_item(self, client: AsyncClient) -> None:
        """Test deleting item."""
        # Create item first
        create_resp = await client.post(
            "/items", json={"name": "ToDelete", "price": 10.0}
        )
        item_id = create_resp.json()["id"]
        response = await client.delete(f"/items/{item_id}")
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_item_not_found(self, client: AsyncClient) -> None:
        """Test deleting non-existent item."""
        response = await client.delete("/items/9999")
        assert response.status_code == 404


class TestSSE:
    """Tests for SSE endpoint."""

    @pytest.mark.asyncio
    async def test_event_generator(self) -> None:
        """Test event generator yields correct format."""
        from fast_simple_crud.app import event_generator  # noqa: PLC0415

        gen = event_generator()
        event = await gen.__anext__()
        assert event["event"] == "tick"
        assert "Server time:" in event["data"]
        await gen.aclose()

    @pytest.mark.asyncio
    async def test_event_generator_multiple_events(self) -> None:
        """Test event generator yields multiple events."""
        with patch("fast_simple_crud.app.asyncio.sleep", return_value=None):
            from fast_simple_crud.app import event_generator  # noqa: PLC0415

            gen = event_generator()
            event1 = await gen.__anext__()
            event2 = await gen.__anext__()
            assert event1["event"] == "tick"
            assert event2["event"] == "tick"
            await gen.aclose()

    @pytest.mark.asyncio
    async def test_sse_stream_returns_event_source_response(self) -> None:
        """Test sse_stream returns EventSourceResponse."""
        from sse_starlette.sse import EventSourceResponse  # noqa: PLC0415

        from fast_simple_crud.app import sse_stream  # noqa: PLC0415

        response = await sse_stream()
        assert isinstance(response, EventSourceResponse)


class TestBroadcast:
    """Tests for broadcast functionality."""

    @pytest.mark.asyncio
    async def test_broadcast_to_clients(self) -> None:
        """Test broadcast sends to all connected clients."""
        from unittest.mock import AsyncMock  # noqa: PLC0415

        from fast_simple_crud.app import broadcast, websocket_clients  # noqa: PLC0415

        mock_client = AsyncMock()
        websocket_clients.append(mock_client)
        try:
            await broadcast("test message")
            mock_client.send_json.assert_called_once()
        finally:
            websocket_clients.remove(mock_client)

    @pytest.mark.asyncio
    async def test_broadcast_handles_error(self) -> None:
        """Test broadcast handles client errors gracefully."""
        from unittest.mock import AsyncMock  # noqa: PLC0415

        from fast_simple_crud.app import broadcast, websocket_clients  # noqa: PLC0415

        mock_client = AsyncMock()
        mock_client.send_json.side_effect = Exception("Connection lost")
        websocket_clients.append(mock_client)
        try:
            # Should not raise
            await broadcast("test message")
        finally:
            websocket_clients.remove(mock_client)
    """Tests for WebSocket endpoint."""

    @pytest.mark.asyncio
    async def test_websocket_echo(self) -> None:
        """Test WebSocket echo functionality."""
        from starlette.testclient import TestClient  # noqa: PLC0415

        from fast_simple_crud.app import app  # noqa: PLC0415

        with TestClient(app) as sync_client, sync_client.websocket_connect("/ws") as ws:
            ws.send_json({"event": "message", "data": "hello"})
            response = ws.receive_json()
            assert response["event"] == "echo"
            assert "hello" in response["data"]


class TestMain:
    """Tests for __main__ module."""

    def test_main_function(self) -> None:
        """Test main entry point."""
        with patch("uvicorn.run") as mock_run:
            from fast_simple_crud.__main__ import main  # noqa: PLC0415

            main()
            mock_run.assert_called_once()

    def test_main_block(self) -> None:
        """Test __main__ block execution."""
        with patch("uvicorn.run"):
            import runpy  # noqa: PLC0415

            runpy.run_module("fast_simple_crud", run_name="__main__")
