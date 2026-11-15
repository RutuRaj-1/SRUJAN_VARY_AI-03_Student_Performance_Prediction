"""
Unified Intelligence Dashboard API Endpoints (Phase 10).
Provides role-aware aggregated views for Students, Faculty, Institution Admins,
Placement Officers, and Super Admins.
Enforces defense-in-depth authorization, tenant isolation, and Placement Officer firewall.
"""

import uuid
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_active_user, require_roles, CurrentUser
from app.models.enums import UserRole
from app.models.academic_data import StudentAcademicProfile
from app.schemas.dashboard import (
    StudentOverviewResponse,
    StudentAcademicPerformanceCard,
    StudentMasterySummaryCard,
    StudentRiskSummaryCard,
    StudentInterventionSummaryCard,
    StudentCareerSummaryCard,
    FacultyOverviewResponse,
    FacultyVerificationQueue,
    FacultyCohortRiskOverview,
    InstitutionOverviewResponse,
    InstitutionAcademicDataStatus,
    InstitutionMasteryOverview,
    InstitutionRiskDistribution,
    InstitutionInterventionMetrics,
    InstitutionCareerReadinessOverview,
    PlacementOverviewResponse,
    PlacementReadinessDistribution,
    PlacementProjectVerificationSummary,
    SkillGapItem,
    SuperAdminOverviewResponse,
    DataFreshnessInfo,
)
from app.services.dashboard import (
    student_dashboard_service,
    faculty_dashboard_service,
    institution_dashboard_service,
    placement_dashboard_service,
    admin_dashboard_service,
)

router = APIRouter()


def _parse_uuid(val: Any) -> Optional[uuid.UUID]:
    if not val:
        return None
    if isinstance(val, uuid.UUID):
        return val
    try:
        return uuid.UUID(str(val))
    except ValueError:
        return None


def _assert_not_placement_officer(current_user: CurrentUser):
    """Enforces firewall preventing Placement Officers from accessing risk or confidential interventions."""
    if current_user.role == UserRole.PLACEMENT_OFFICER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Placement Officers are strictly prohibited from accessing academic risk or confidential interventions."
        )


# =========================================================================
# 1. Student Intelligence Dashboard Endpoints
# =========================================================================

@router.get("/student/overview", response_model=StudentOverviewResponse)
def get_student_overview(
    student_id: Optional[uuid.UUID] = Query(None, description="Optional target student ID for faculty/admin"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(
        [UserRole.STUDENT, UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN]
    )),
):
    """Unified Student Intelligence Dashboard aggregating academic, mastery, risk, intervention, and career readiness."""
    _assert_not_placement_officer(current_user)
    user_uuid = _parse_uuid(current_user.user_id)
    inst_uuid = _parse_uuid(current_user.institution_id)

    # Student ownership check: students cannot view other students' dashboards
    if current_user.role == UserRole.STUDENT:
        if student_id:
            profile = db.query(StudentAcademicProfile).filter(StudentAcademicProfile.id == student_id).first()
            if not profile or profile.profile_id != user_uuid:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Students may only access their own dashboard."
                )

    return student_dashboard_service.get_student_overview(
        db=db,
        user_id=user_uuid,
        institution_id=inst_uuid,
        target_student_id=student_id,
    )


@router.get("/student/academic-summary", response_model=StudentAcademicPerformanceCard)
def get_student_academic_summary(
    student_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(
        [UserRole.STUDENT, UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN]
    )),
):
    overview = get_student_overview(student_id=student_id, db=db, current_user=current_user)
    return overview.academic_performance


@router.get("/student/mastery-summary", response_model=StudentMasterySummaryCard)
def get_student_mastery_summary(
    student_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(
        [UserRole.STUDENT, UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN]
    )),
):
    overview = get_student_overview(student_id=student_id, db=db, current_user=current_user)
    return overview.mastery_summary


@router.get("/student/risk-summary", response_model=StudentRiskSummaryCard)
def get_student_risk_summary(
    student_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(
        [UserRole.STUDENT, UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN]
    )),
):
    _assert_not_placement_officer(current_user)
    overview = get_student_overview(student_id=student_id, db=db, current_user=current_user)
    return overview.risk_summary


@router.get("/student/intervention-summary", response_model=StudentInterventionSummaryCard)
def get_student_intervention_summary(
    student_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(
        [UserRole.STUDENT, UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN]
    )),
):
    _assert_not_placement_officer(current_user)
    overview = get_student_overview(student_id=student_id, db=db, current_user=current_user)
    return overview.intervention_summary


@router.get("/student/career-summary", response_model=StudentCareerSummaryCard)
def get_student_career_summary(
    student_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(
        [UserRole.STUDENT, UserRole.FACULTY, UserRole.PLACEMENT_OFFICER, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN]
    )),
):
    user_uuid = _parse_uuid(current_user.user_id)
    inst_uuid = _parse_uuid(current_user.institution_id)
    overview = student_dashboard_service.get_student_overview(
        db=db,
        user_id=user_uuid,
        institution_id=inst_uuid,
        target_student_id=student_id,
    )
    return overview.career_summary


# =========================================================================
# 2. Faculty Intelligence Dashboard Endpoints
# =========================================================================

@router.get("/faculty/overview", response_model=FacultyOverviewResponse)
def get_faculty_overview(
    subject_id: Optional[uuid.UUID] = Query(None, description="Optional subject filter"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(
        [UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN]
    )),
):
    """Faculty intelligence overview covering assigned subjects, verification queues, and cohort risk flags."""
    user_uuid = _parse_uuid(current_user.user_id)
    inst_uuid = _parse_uuid(current_user.institution_id)
    if not inst_uuid:
        raise HTTPException(status_code=400, detail="Institution context required.")

    return faculty_dashboard_service.get_faculty_overview(
        db=db,
        user_id=user_uuid,
        institution_id=inst_uuid,
        subject_id=subject_id,
    )


@router.get("/faculty/verification-queue", response_model=FacultyVerificationQueue)
def get_faculty_verification_queue(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(
        [UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN]
    )),
):
    overview = get_faculty_overview(subject_id=None, db=db, current_user=current_user)
    return overview.verification_queue


@router.get("/faculty/cohort-risk", response_model=FacultyCohortRiskOverview)
def get_faculty_cohort_risk(
    subject_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(
        [UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN]
    )),
):
    overview = get_faculty_overview(subject_id=subject_id, db=db, current_user=current_user)
    return overview.cohort_risk_overview


# =========================================================================
# 3. Institution Admin Dashboard Endpoints
# =========================================================================

@router.get("/institution/overview", response_model=InstitutionOverviewResponse)
def get_institution_overview(
    institution_id: Optional[uuid.UUID] = Query(None, description="Optional institution ID for Super Admin"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(
        [UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN]
    )),
):
    """Institution administrator dashboard summarizing academic, mastery, risk, and intervention health."""
    inst_uuid = institution_id if (current_user.role == UserRole.SUPER_ADMIN and institution_id) else _parse_uuid(current_user.institution_id)
    if not inst_uuid:
        raise HTTPException(status_code=400, detail="Valid institution ID required.")

    return institution_dashboard_service.get_institution_overview(
        db=db,
        institution_id=inst_uuid,
    )


@router.get("/institution/academic-summary", response_model=InstitutionAcademicDataStatus)
def get_institution_academic_summary(
    institution_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    overview = get_institution_overview(institution_id=institution_id, db=db, current_user=current_user)
    return overview.academic_data_status


@router.get("/institution/mastery-summary", response_model=InstitutionMasteryOverview)
def get_institution_mastery_summary(
    institution_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    overview = get_institution_overview(institution_id=institution_id, db=db, current_user=current_user)
    return overview.mastery_overview


@router.get("/institution/risk-summary", response_model=InstitutionRiskDistribution)
def get_institution_risk_summary(
    institution_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    overview = get_institution_overview(institution_id=institution_id, db=db, current_user=current_user)
    return overview.risk_distribution


@router.get("/institution/intervention-summary", response_model=InstitutionInterventionMetrics)
def get_institution_intervention_summary(
    institution_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    overview = get_institution_overview(institution_id=institution_id, db=db, current_user=current_user)
    return overview.intervention_metrics


@router.get("/institution/career-summary", response_model=InstitutionCareerReadinessOverview)
def get_institution_career_summary(
    institution_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    overview = get_institution_overview(institution_id=institution_id, db=db, current_user=current_user)
    return overview.career_readiness_overview


# =========================================================================
# 4. Placement Officer Dashboard Endpoints (Firewalled)
# =========================================================================

@router.get("/placement/overview", response_model=PlacementOverviewResponse)
def get_placement_overview(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(
        [UserRole.PLACEMENT_OFFICER, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN, UserRole.FACULTY]
    )),
):
    """
    Placement officer career readiness workspace.
    Completely firewalled from academic risk predictions and confidential interventions.
    """
    inst_uuid = _parse_uuid(current_user.institution_id)
    if not inst_uuid:
        raise HTTPException(status_code=400, detail="Institution context required.")

    return placement_dashboard_service.get_placement_overview(
        db=db,
        institution_id=inst_uuid,
    )


@router.get("/placement/career-summary", response_model=PlacementReadinessDistribution)
def get_placement_readiness_distribution(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(
        [UserRole.PLACEMENT_OFFICER, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN, UserRole.FACULTY]
    )),
):
    overview = get_placement_overview(db=db, current_user=current_user)
    return overview.readiness_distribution


@router.get("/placement/project-verification-summary", response_model=PlacementProjectVerificationSummary)
def get_placement_project_summary(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(
        [UserRole.PLACEMENT_OFFICER, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN, UserRole.FACULTY]
    )),
):
    overview = get_placement_overview(db=db, current_user=current_user)
    return overview.project_verification_summary


@router.get("/placement/competency-summary", response_model=List[SkillGapItem])
def get_placement_top_skill_gaps(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles(
        [UserRole.PLACEMENT_OFFICER, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN, UserRole.FACULTY]
    )),
):
    overview = get_placement_overview(db=db, current_user=current_user)
    return overview.top_industry_skill_gaps


# =========================================================================
# 5. Super Admin Platform Overview Endpoints
# =========================================================================

@router.get("/admin/overview", response_model=SuperAdminOverviewResponse)
def get_admin_overview(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN])),
):
    """Super Admin platform overview providing multi-tenant telemetry and subsystem health."""
    return admin_dashboard_service.get_platform_overview(db=db)


@router.get("/admin/system-health")
def get_admin_system_health(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN])),
):
    overview = get_admin_overview(db=db, current_user=current_user)
    return {
        "database_connectivity": overview.database_connectivity,
        "database_latency_ms": overview.database_latency_ms,
        "latest_migration": overview.latest_migration,
        "ai_service_configured": overview.ai_service_configured,
        "freshness": overview.freshness,
    }


@router.get("/admin/module-health")
def get_admin_module_health(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN])),
):
    overview = get_admin_overview(db=db, current_user=current_user)
    return {
        "module_health_status": overview.module_health_status,
        "freshness": overview.freshness,
    }
