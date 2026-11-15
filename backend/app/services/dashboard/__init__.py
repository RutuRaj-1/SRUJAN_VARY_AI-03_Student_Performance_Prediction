"""
Dashboard Integration Services Package (Phase 10).
"""

from app.services.dashboard.student_dashboard_service import (
    StudentDashboardService,
    student_dashboard_service,
)
from app.services.dashboard.faculty_dashboard_service import (
    FacultyDashboardService,
    faculty_dashboard_service,
)
from app.services.dashboard.institution_dashboard_service import (
    InstitutionDashboardService,
    institution_dashboard_service,
)
from app.services.dashboard.placement_dashboard_service import (
    PlacementDashboardService,
    placement_dashboard_service,
)
from app.services.dashboard.admin_dashboard_service import (
    AdminDashboardService,
    admin_dashboard_service,
)

__all__ = [
    "StudentDashboardService",
    "student_dashboard_service",
    "FacultyDashboardService",
    "faculty_dashboard_service",
    "InstitutionDashboardService",
    "institution_dashboard_service",
    "PlacementDashboardService",
    "placement_dashboard_service",
    "AdminDashboardService",
    "admin_dashboard_service",
]
