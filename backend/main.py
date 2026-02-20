"""ASGI entrypoint for the MediGuardian FastAPI backend."""

import logging
import time

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.database import DatabaseConnectionError, DatabaseQueryError
from app.core.lifespan import lifespan
from app.core.logging import configure_logging
from app.routers import analysis, appointments, auth, dashboard, doctors, files, health, instructions, profile

configure_logging(settings.LOG_LEVEL)
logger = logging.getLogger("mediguardian.api")

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ALLOW_ORIGIN_REGEX,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.exception(
            "%s %s -> unhandled exception (%.2f ms)",
            request.method,
            request.url.path,
            duration_ms,
        )
        raise

    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s -> %s (%.2f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    logger.warning("Request validation failed: %s", exc.errors())
    if not exc.errors():
        return JSONResponse(status_code=400, content={"error": "Invalid request payload"})

    first_error = exc.errors()[0]
    message = first_error.get("msg", "Invalid request payload")
    return JSONResponse(status_code=400, content={"error": message})


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_: Request, exc: StarletteHTTPException):
    if exc.status_code >= 500:
        logger.error("HTTP exception %s: %s", exc.status_code, exc.detail)
    if exc.status_code == 404:
        detail = exc.detail if isinstance(exc.detail, str) else "Endpoint not found"
        # Preserve semantic 404 messages raised by route handlers.
        if detail.strip().lower() == "not found":
            detail = "Endpoint not found"
        return JSONResponse(status_code=404, content={"error": detail})

    if exc.status_code == 413:
        return JSONResponse(status_code=413, content={"error": "File too large. Maximum size is 50MB"})

    detail = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return JSONResponse(status_code=exc.status_code, content={"error": detail})


@app.exception_handler(RuntimeError)
async def runtime_exception_handler(_: Request, exc: RuntimeError):
    logger.error("Runtime error: %s", exc)
    if "Database connection failed" in str(exc):
        return JSONResponse(status_code=503, content={"error": "Database is temporarily unavailable"})
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


@app.exception_handler(DatabaseConnectionError)
async def database_connection_exception_handler(_: Request, exc: DatabaseConnectionError):
    logger.error("Database connection error: %s", exc)
    return JSONResponse(status_code=503, content={"error": "Database is temporarily unavailable"})


@app.exception_handler(DatabaseQueryError)
async def database_query_exception_handler(_: Request, exc: DatabaseQueryError):
    logger.error("Database query error: %s", exc)
    return JSONResponse(status_code=500, content={"error": "Database operation failed"})


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(analysis.router, prefix="/api/analyze", tags=["Analysis"])
app.include_router(instructions.router, prefix="/api", tags=["Analysis"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(doctors.router, prefix="/api/doctors", tags=["Doctors"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["Appointments"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(profile.router, prefix="/api", tags=["Profile"])
app.include_router(files.router, prefix="/api", tags=["Files"])


@app.get("/")
async def root():
    return {
        "message": "MediGuardian API",
        "version": settings.API_VERSION,
        "endpoints": {
            "auth": {
                "register": "POST /api/auth/register",
                "login": "POST /api/auth/login",
                "verify": "GET /api/auth/verify",
            },
            "analysis": {
                "analyze": "POST /api/analyze",
                "analyze_multi_disease": "POST /api/analyze/multi-disease",
                "recording_instructions": "GET /api/recording-instructions/{test_type}",
            },
            "health": {
                "liveness": "GET /api/health",
                "readiness": "GET /api/health/readiness",
                "seed_status": "GET /api/seed-status",
            },
            "dashboard": {
                "dashboard": "GET /api/dashboard",
                "result": "GET /api/results/{test_id}",
            },
            "profile": {
                "profile": "GET /api/profile",
                "add_emergency": "POST /api/profile/emergency",
                "get_emergency": "GET /api/profile/emergency",
            },
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.runtime_port,
        reload=settings.DEBUG,
    )
