"""Entry point for running the application."""

from __future__ import annotations

import uvicorn


def main() -> None:
    """Run the FastAPI application."""
    uvicorn.run(
        "fast_simple_crud.app:app",
        host="0.0.0.0",  # nosec B104  # noqa: S104  # Development server binding
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
