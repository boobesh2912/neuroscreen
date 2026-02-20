"""Health and readiness routes."""

from datetime import datetime, timezone

from fastapi import APIRouter, Response

from app.core.config import settings
from app.core.database import get_db, table_exists
from app.core.lifespan import get_feature_names, get_model


router = APIRouter()
REQUIRED_TABLES = [
    "users",
    "test_results",
    "doctors",
    "doctor_availability",
    "appointments",
    "doctor_reviews",
]


def collect_readiness() -> dict:
    """Collect runtime readiness diagnostics for deployment checks."""
    readiness = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "model_cache": {
            "parkinson_model_loaded": get_model() is not None,
            "feature_name_count": len(get_feature_names()),
        },
        "database": {
            "connected": False,
            "missing_tables": [],
            "doctor_count": 0,
        },
    }

    try:
        with get_db() as conn:
            cur = conn.cursor()
            readiness["database"]["connected"] = True
            missing_tables: list[str] = []

            for table in REQUIRED_TABLES:
                if not table_exists(conn, table):
                    missing_tables.append(table)

            readiness["database"]["missing_tables"] = missing_tables

            if "doctors" not in missing_tables:
                cur.execute("SELECT COUNT(*) AS c FROM doctors")
                readiness["database"]["doctor_count"] = int(cur.fetchone()["c"])
    except Exception as exc:
        readiness["database"]["error"] = str(exc)

    model_ready = readiness["model_cache"]["parkinson_model_loaded"]
    db_ready = readiness["database"]["connected"] and len(readiness["database"]["missing_tables"]) == 0
    seeded = readiness["database"]["doctor_count"] > 0
    readiness["status"] = "ready" if (model_ready and db_ready and seeded) else "degraded"
    return readiness


@router.get("/health")
async def health_check():
    """API health check endpoint."""
    readiness = collect_readiness()
    return {
        "status": "healthy" if readiness["status"] == "ready" else "degraded",
        "service": "MediGuardian API",
        "version": settings.API_VERSION,
        "readiness": {
            "status": readiness["status"],
            "model_cached": readiness["model_cache"]["parkinson_model_loaded"],
            "database_connected": readiness["database"]["connected"],
            "missing_tables": readiness["database"]["missing_tables"],
            "doctor_count": readiness["database"]["doctor_count"],
        },
    }


@router.get("/health/readiness")
async def readiness_check(response: Response):
    """Detailed readiness endpoint for deployment checks."""
    readiness = collect_readiness()
    if readiness["status"] != "ready":
        response.status_code = 503
    return readiness


@router.get("/seed-status")
async def seed_status():
    """Return doctor-seed status to verify booking bootstrap."""
    readiness = collect_readiness()
    return {
        "success": True,
        "doctor_count": readiness["database"]["doctor_count"],
        "seeded": readiness["database"]["doctor_count"] > 0,
        "missing_tables": readiness["database"]["missing_tables"],
        "status": readiness["status"],
        "checked_at": readiness["checked_at"],
    }
