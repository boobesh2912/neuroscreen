"""Database connection helpers for SQLite and PostgreSQL."""

from __future__ import annotations

from contextlib import contextmanager
import logging
import sqlite3
import time
from typing import Any, Generator

from app.core.config import settings

try:
    import psycopg
    from psycopg.rows import dict_row
    from psycopg_pool import ConnectionPool
except Exception:  # pragma: no cover - optional dependency in SQLite mode
    psycopg = None
    dict_row = None
    ConnectionPool = None


logger = logging.getLogger("mediguardian.database")
_pg_pool: ConnectionPool | None = None


class DatabaseConnectionError(RuntimeError):
    """Raised when a DB connection cannot be established."""


class DatabaseQueryError(RuntimeError):
    """Raised when a DB query fails after connection is established."""


def _convert_placeholders(query: str) -> str:
    if settings.database_backend == "postgresql":
        return query.replace("?", "%s")
    return query


def _is_connection_unavailable(exc: Exception) -> bool:
    message = str(exc).lower()
    unavailable_markers = (
        "could not connect",
        "connection refused",
        "connection reset",
        "connection not open",
        "server closed the connection",
        "timeout expired",
        "timed out",
        "temporary failure",
        "unable to open database file",
        "database is locked",
    )
    return any(marker in message for marker in unavailable_markers)


def _connect_with_retry(connect_fn, label: str):
    last_exc: Exception | None = None
    retries = settings.DB_CONNECT_MAX_RETRIES
    delay = settings.DB_CONNECT_RETRY_DELAY_SECONDS
    for attempt in range(1, retries + 1):
        try:
            return connect_fn()
        except Exception as exc:  # pragma: no cover - exercised via runtime smoke tests
            last_exc = exc
            logger.warning(
                "Database %s attempt %s/%s failed: %s",
                label,
                attempt,
                retries,
                exc,
            )
            if attempt < retries:
                time.sleep(delay)
    raise DatabaseConnectionError("Database connection failed") from last_exc


def _connect_sqlite_raw() -> sqlite3.Connection:
    settings.database_full_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(settings.database_full_path, timeout=30, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _ensure_postgres_pool() -> ConnectionPool:
    global _pg_pool
    if _pg_pool is not None:
        return _pg_pool

    if psycopg is None or ConnectionPool is None or dict_row is None:
        raise DatabaseConnectionError("Database connection failed")

    def _build_pool() -> ConnectionPool:
        pool = ConnectionPool(
            conninfo=settings.postgres_dsn,
            min_size=settings.DB_POOL_MIN_SIZE,
            max_size=settings.DB_POOL_MAX_SIZE,
            open=True,
            kwargs={"autocommit": False, "row_factory": dict_row},
        )
        pool.wait()
        return pool

    _pg_pool = _connect_with_retry(_build_pool, "pool initialization")
    return _pg_pool


def close_database() -> None:
    global _pg_pool
    if _pg_pool is not None:
        _pg_pool.close()
        _pg_pool = None


class CursorAdapter:
    def __init__(self, raw_cursor: Any):
        self._raw_cursor = raw_cursor

    def execute(self, query: str, params: Any = None):
        sql = _convert_placeholders(query)
        try:
            if params is None:
                return self._raw_cursor.execute(sql)
            return self._raw_cursor.execute(sql, params)
        except Exception as exc:
            logger.error("Database query failed: %s", exc)
            if _is_connection_unavailable(exc):
                raise DatabaseConnectionError("Database connection failed") from exc
            raise DatabaseQueryError("Database query failed") from exc

    def executemany(self, query: str, seq_of_params: Any):
        sql = _convert_placeholders(query)
        try:
            return self._raw_cursor.executemany(sql, seq_of_params)
        except Exception as exc:
            logger.error("Database bulk query failed: %s", exc)
            if _is_connection_unavailable(exc):
                raise DatabaseConnectionError("Database connection failed") from exc
            raise DatabaseQueryError("Database query failed") from exc

    def fetchone(self):
        return self._raw_cursor.fetchone()

    def fetchall(self):
        return self._raw_cursor.fetchall()

    @property
    def rowcount(self) -> int:
        return self._raw_cursor.rowcount

    def __getattr__(self, name: str):
        return getattr(self._raw_cursor, name)


class ConnectionAdapter:
    def __init__(self, raw_connection: Any):
        self._raw_connection = raw_connection

    def cursor(self) -> CursorAdapter:
        return CursorAdapter(self._raw_connection.cursor())

    def commit(self) -> None:
        self._raw_connection.commit()

    def rollback(self) -> None:
        self._raw_connection.rollback()

    def close(self) -> None:
        self._raw_connection.close()

    def __getattr__(self, name: str):
        return getattr(self._raw_connection, name)


def init_database() -> None:
    if settings.database_backend == "sqlite":
        settings.database_full_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        _ensure_postgres_pool()

    with get_db() as conn:
        cur = conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                date_of_birth TEXT,
                phone_number TEXT,
                address TEXT,
                created_at TEXT NOT NULL,
                last_login TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS emergency_contacts (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                relationship TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                email TEXT,
                is_primary BOOLEAN NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS medical_history (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                condition TEXT,
                diagnosis_date TEXT,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS test_results (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                test_type TEXT NOT NULL,
                test_date TEXT NOT NULL,
                prediction TEXT NOT NULL,
                confidence REAL NOT NULL,
                features TEXT NOT NULL,
                audio_file_path TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS doctor_referrals (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                doctor_name TEXT NOT NULL,
                specialty TEXT NOT NULL,
                hospital TEXT,
                address TEXT,
                phone_number TEXT,
                email TEXT,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS doctors (
                id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone_number TEXT NOT NULL,
                specialization TEXT NOT NULL,
                sub_specialties TEXT,
                qualification TEXT NOT NULL,
                experience_years INTEGER NOT NULL,
                hospital_affiliation TEXT,
                clinic_address TEXT,
                city TEXT NOT NULL,
                state TEXT NOT NULL,
                consultation_fee REAL NOT NULL,
                about TEXT,
                profile_image_url TEXT,
                languages TEXT,
                rating REAL DEFAULT 0.0,
                total_reviews INTEGER DEFAULT 0,
                is_available BOOLEAN DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS doctor_availability (
                id TEXT PRIMARY KEY,
                doctor_id TEXT NOT NULL,
                day_of_week INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                slot_duration INTEGER DEFAULT 30,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (doctor_id) REFERENCES doctors (id)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                doctor_id TEXT NOT NULL,
                test_result_id TEXT,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'scheduled',
                booking_type TEXT NOT NULL DEFAULT 'consultation',
                symptoms TEXT,
                notes TEXT,
                risk_score INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                cancellation_reason TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (doctor_id) REFERENCES doctors (id),
                FOREIGN KEY (test_result_id) REFERENCES test_results (id)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS doctor_reviews (
                id TEXT PRIMARY KEY,
                doctor_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                appointment_id TEXT,
                rating INTEGER NOT NULL,
                review_text TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (doctor_id) REFERENCES doctors (id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (appointment_id) REFERENCES appointments (id)
            )
            """
        )
        conn.commit()


def table_exists(connection: ConnectionAdapter, table_name: str) -> bool:
    cur = connection.cursor()
    if settings.database_backend == "postgresql":
        cur.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = ?
            ) AS present
            """,
            (table_name,),
        )
        row = cur.fetchone()
        if row is None:
            return False
        if isinstance(row, dict):
            return bool(row.get("present", False))
        return bool(row["present"])

    cur.execute(
        "SELECT COUNT(*) AS c FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    )
    row = cur.fetchone()
    if row is None:
        return False
    return int(row["c"]) > 0


@contextmanager
def get_db() -> Generator[ConnectionAdapter, None, None]:
    if settings.database_backend == "postgresql":
        pool = _ensure_postgres_pool()
        try:
            with pool.connection() as raw_connection:
                connection = ConnectionAdapter(raw_connection)
                try:
                    yield connection
                    raw_connection.commit()
                except Exception:
                    raw_connection.rollback()
                    raise
                return
        except DatabaseConnectionError:
            raise
        except Exception as exc:
            logger.error("Database connection failed: %s", exc)
            raise DatabaseConnectionError("Database connection failed") from exc

    raw_connection = _connect_with_retry(_connect_sqlite_raw, "connection")
    connection = ConnectionAdapter(raw_connection)
    try:
        yield connection
        raw_connection.commit()
    except Exception:
        raw_connection.rollback()
        raise
    finally:
        raw_connection.close()
