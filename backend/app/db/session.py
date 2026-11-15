"""
Database Engine, Session Local factory, and Health Check utilities.
Designed to fail safely and gracefully when DATABASE_URL is not set or has placeholders.
"""
import time
from typing import Generator, Optional, Tuple
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()

_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None and settings.is_database_configured:
        try:
            db_url = settings.DATABASE_URL
            # Normalize postgres:// -> postgresql+psycopg://
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
            elif db_url.startswith("postgresql://") and "+psycopg" not in db_url:
                db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

            _engine = create_engine(
                db_url,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                connect_args={"connect_timeout": 3} if "sqlite" not in db_url else {},
            )
            logger.info("Database engine initialized successfully.")
        except Exception as exc:
            logger.error("Failed to initialize database engine: %s", exc)
            _engine = None
    return _engine


def get_session_local():
    global _SessionLocal
    engine = get_engine()
    if engine is not None and _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal


def get_db() -> Generator[Optional[Session], None, None]:
    """FastAPI dependency for obtaining a database session."""
    session_factory = get_session_local()
    if session_factory is None:
        yield None
        return
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> Tuple[bool, str, Optional[float]]:
    """
    Validates database connectivity without throwing unhandled exceptions.
    Returns:
        (is_connected, status_message, latency_ms)
    """
    if not settings.DATABASE_URL or not settings.DATABASE_URL.strip():
        return (
            False,
            "DATABASE_URL is not configured. Running in standalone / decoupled mode.",
            None,
        )

    if "[YOUR-PASSWORD]" in settings.DATABASE_URL:
        return (
            False,
            "DATABASE_URL contains the unpopulated placeholder [YOUR-PASSWORD]. Please update backend/.env with your Supabase database password.",
            None,
        )

    engine = get_engine()
    if engine is None:
        return (
            False,
            "Failed to construct database engine from the configured DATABASE_URL.",
            None,
        )

    start_time = time.perf_counter()
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        latency = (time.perf_counter() - start_time) * 1000.0
        return True, "Database connection operational.", round(latency, 2)
    except Exception as exc:
        logger.warning("Database connectivity probe failed: %s", exc)
        return (
            False,
            f"Database connection failed: {str(exc)}",
            None,
        )
