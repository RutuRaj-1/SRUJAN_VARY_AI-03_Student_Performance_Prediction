from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., description="High-level application status: healthy | degraded")
    app_name: str = Field(..., description="Application name")
    environment: str = Field(..., description="Active environment (e.g. development, staging, production)")
    version: str = Field("0.1.0", description="API version")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    services: Dict[str, str] = Field(
        default_factory=dict,
        description="Status overview of internal subsystems"
    )


class DatabaseHealthResponse(BaseModel):
    status: str = Field(..., description="Database status: connected | unconfigured | disconnected")
    configured: bool = Field(..., description="Whether DATABASE_URL is set in environment")
    message: str = Field(..., description="Human-readable status summary")
    latency_ms: Optional[float] = Field(None, description="Probe latency in milliseconds if connected")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RootInfoResponse(BaseModel):
    app: str = "MASTERY"
    tagline: str = "Beyond Marks. Towards Mastery."
    description: str = "AI-powered Student Performance Analytics, Academic Risk Prediction and Career Readiness Platform"
    version: str = "0.1.0"
    api_v1_docs: str = "/docs"
    api_v1_health: str = "/api/v1/health"
    api_v1_db_health: str = "/api/v1/health/database"
