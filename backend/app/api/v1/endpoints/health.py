from fastapi import APIRouter, Response, status
from app.core.config import get_settings
from app.db.session import check_database_connection
from app.schemas.health import HealthResponse, DatabaseHealthResponse

router = APIRouter(prefix="/health", tags=["Health & Diagnostics"])
settings = get_settings()


@router.get("", response_model=HealthResponse, summary="Application Health Check")
def get_app_health() -> HealthResponse:
    """
    Returns general application health and subsystem configuration states.
    Does not falsely report external services as connected if unconfigured.
    """
    is_db_connected, db_msg, _ = check_database_connection()

    db_status = "connected" if is_db_connected else ("unconfigured" if not settings.is_database_configured else "disconnected")
    ai_status = "configured" if settings.is_ai_configured else "unconfigured"
    supabase_status = "configured" if settings.is_supabase_configured else "unconfigured"

    # Overall app health is healthy if core API is running
    overall_status = "healthy"

    return HealthResponse(
        status=overall_status,
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        version="0.1.0",
        services={
            "api": "operational",
            "database": db_status,
            "ai_engine": ai_status,
            "supabase_auth": supabase_status,
        },
    )


@router.get("/database", response_model=DatabaseHealthResponse, summary="Database Health Probe")
def get_database_health(response: Response) -> DatabaseHealthResponse:
    """
    Explicit database health probe.
    - If DATABASE_URL is not set: returns 200 with status='unconfigured'.
    - If DATABASE_URL is set and reachable: returns 200 with status='connected'.
    - If DATABASE_URL is set but unreachable: returns 503 with status='disconnected'.
    """
    is_connected, message, latency_ms = check_database_connection()

    if not settings.is_database_configured:
        return DatabaseHealthResponse(
            status="unconfigured",
            configured=False,
            message=message,
            latency_ms=None,
        )

    if not is_connected:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return DatabaseHealthResponse(
            status="disconnected",
            configured=True,
            message=message,
            latency_ms=None,
        )

    return DatabaseHealthResponse(
        status="connected",
        configured=True,
        message=message,
        latency_ms=latency_ms,
    )
