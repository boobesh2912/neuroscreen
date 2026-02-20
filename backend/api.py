"""Compatibility entrypoint for the FastAPI backend."""

from main import app


if __name__ == "__main__":
    import uvicorn

    from app.core.config import settings

    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.runtime_port,
        reload=settings.DEBUG,
    )
