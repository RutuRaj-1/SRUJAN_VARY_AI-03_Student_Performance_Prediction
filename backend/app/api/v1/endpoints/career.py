import uuid
from typing import List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_active_user, require_roles, CurrentUser
from app.models.enums import UserRole
from app.models.academic_data import StudentAcademicProfile
from app.models.syllabus import IndustryRoleProfile, IndustryCompetencyRequirement
from app.models.career import (
    StudentProjectEvidence,
    StudentCompetencyEvidence,
    CareerReadinessAnalysis,
    CareerSkillGapFinding,
    CareerDevelopmentRecommendation,
    DEFAULT_CAREER_READINESS_DISCLAIMER,
)
from app.schemas.career import (
    IndustryRoleProfileCreate,
    IndustryRoleProfileUpdate,
    IndustryRoleProfileResponse,
    IndustryCompetencyRequirementCreate,
    IndustryCompetencyRequirementResponse,
    StudentProjectEvidenceCreate,
    StudentProjectEvidenceUpdate,
    StudentProjectEvidenceReview,
    StudentProjectEvidenceResponse,
    StudentCompetencyEvidenceResponse,
    CareerReadinessAnalysisRequest,
    CareerReadinessAnalysisResponse,
    CareerReadinessComparisonResponse,
    CareerDashboardOverviewResponse,
    CareerSkillGapFindingResponse,
    CareerDevelopmentRecommendationResponse,
    CareerDevelopmentRecommendationUpdate,
)
from app.services.career import (
    RoleProfileService,
    ProjectEvidenceService,
    CompetencyEvidenceService,
    CareerReadinessAnalysisService,
    CareerRecommendationService,
)

router = APIRouter()


def _parse_uuid(val: Any) -> uuid.UUID:
    if isinstance(val, uuid.UUID):
        return val
    return uuid.UUID(str(val))


def _get_student_profile(db: Session, user_id: uuid.UUID, institution_id: Optional[uuid.UUID] = None) -> StudentAcademicProfile:
    query = db.query(StudentAcademicProfile).filter(StudentAcademicProfile.profile_id == user_id)
    if institution_id:
        query = query.filter(StudentAcademicProfile.institution_id == institution_id)
    profile = query.first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student academic profile not found for the authenticated user.",
        )
    return profile


# =========================================================================
# 1. Career Role Profiles & Requirements
# =========================================================================

@router.get(
    "/roles",
    response_model=List[IndustryRoleProfileResponse],
    summary="List available industry career role profiles",
)
def list_career_roles(
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    institution_id = _parse_uuid(current_user.institution_id) if current_user.institution_id else None
    return RoleProfileService.list_roles(db, institution_id=institution_id, include_inactive=include_inactive)


@router.get(
    "/roles/{role_id}",
    response_model=IndustryRoleProfileResponse,
    summary="Get details of a specific career role profile including requirements",
)
def get_career_role(
    role_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    return RoleProfileService.get_role_by_id(db, role_id)


@router.post(
    "/roles",
    response_model=IndustryRoleProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new career role profile (Faculty/Admin only)",
)
def create_career_role(
    role_in: IndustryRoleProfileCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    inst_id = _parse_uuid(current_user.institution_id) if current_user.institution_id else None
    return RoleProfileService.create_role(db, role_in, institution_id=inst_id)


@router.put(
    "/roles/{role_id}",
    response_model=IndustryRoleProfileResponse,
    summary="Update a career role profile (Faculty/Admin only)",
)
def update_career_role(
    role_id: uuid.UUID,
    role_in: IndustryRoleProfileUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    return RoleProfileService.update_role(db, role_id, role_in)


@router.post(
    "/roles/{role_id}/requirements",
    response_model=IndustryCompetencyRequirementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a competency requirement to a role profile (Faculty/Admin only)",
)
def add_role_requirement(
    role_id: uuid.UUID,
    req_in: IndustryCompetencyRequirementCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    if req_in.role_id != role_id:
        req_in.role_id = role_id
    return RoleProfileService.add_requirement(db, req_in)


# =========================================================================
# 2. Student Project Evidence Endpoints
# =========================================================================

@router.get(
    "/projects",
    response_model=List[StudentProjectEvidenceResponse],
    summary="List student practical project submissions",
)
def list_student_projects(
    student_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _parse_uuid(current_user.institution_id) if current_user.institution_id else None

    if current_user.role == UserRole.STUDENT:
        student_profile = _get_student_profile(db, _parse_uuid(current_user.id), inst_id)
        target_student_id = student_profile.id
    else:
        if not student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="student_id query parameter is required for staff and placement queries.",
            )
        target_student_id = student_id

    return ProjectEvidenceService.list_student_projects(db, target_student_id, inst_id)


@router.post(
    "/projects",
    response_model=StudentProjectEvidenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit practical project evidence (Student or Faculty on behalf)",
)
def submit_student_project(
    project_in: StudentProjectEvidenceCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.STUDENT, UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    inst_id = _parse_uuid(current_user.institution_id)
    if current_user.role == UserRole.STUDENT:
        student_profile = _get_student_profile(db, _parse_uuid(current_user.id), inst_id)
        target_student_id = student_profile.id
    else:
        if not project_in.student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="student_id must be provided when submitting on behalf of a student.",
            )
        target_student_id = project_in.student_id

    return ProjectEvidenceService.submit_project(db, project_in, target_student_id, inst_id)


@router.put(
    "/projects/{project_id}",
    response_model=StudentProjectEvidenceResponse,
    summary="Update project evidence (Student owner only, prior to verification)",
)
def update_student_project(
    project_id: uuid.UUID,
    project_in: StudentProjectEvidenceUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.STUDENT, UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    inst_id = _parse_uuid(current_user.institution_id)
    if current_user.role == UserRole.STUDENT:
        student_profile = _get_student_profile(db, _parse_uuid(current_user.id), inst_id)
        target_student_id = student_profile.id
    else:
        proj = ProjectEvidenceService.get_project_by_id(db, project_id)
        target_student_id = proj.student_id

    return ProjectEvidenceService.update_project(db, project_id, project_in, target_student_id)


@router.post(
    "/projects/{project_id}/review",
    response_model=StudentProjectEvidenceResponse,
    summary="Faculty review and verification of student project evidence",
)
def review_student_project(
    project_id: uuid.UUID,
    review_in: StudentProjectEvidenceReview,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    return ProjectEvidenceService.review_project(
        db,
        project_id=project_id,
        review_in=review_in,
        reviewer_id=_parse_uuid(current_user.id),
    )


# =========================================================================
# 3. Student Competency Evidence
# =========================================================================

@router.get(
    "/evidence",
    response_model=List[StudentCompetencyEvidenceResponse],
    summary="Retrieve verified competency evidence ledger for a student",
)
def get_competency_evidence(
    student_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _parse_uuid(current_user.institution_id)

    if current_user.role == UserRole.STUDENT:
        student_profile = _get_student_profile(db, _parse_uuid(current_user.id), inst_id)
        target_student_id = student_profile.id
    else:
        if not student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="student_id is required for faculty, admin, and placement officer queries.",
            )
        target_student_id = student_id

    return CompetencyEvidenceService.get_student_evidence(db, target_student_id, inst_id)


# =========================================================================
# 4. Career Readiness Analysis & Role Comparison
# =========================================================================

@router.post(
    "/analyze",
    response_model=CareerReadinessAnalysisResponse,
    summary="Run or retrieve role-specific career readiness analysis",
)
def analyze_career_readiness(
    req: CareerReadinessAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _parse_uuid(current_user.institution_id)

    if current_user.role == UserRole.STUDENT:
        student_profile = _get_student_profile(db, _parse_uuid(current_user.id), inst_id)
        target_student_id = student_profile.id
    else:
        if not req.student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="student_id is required in request body for staff queries.",
            )
        target_student_id = req.student_id

    analysis = CareerReadinessAnalysisService.analyze_role_readiness(
        db=db,
        student_id=target_student_id,
        role_id=req.role_id,
        institution_id=inst_id,
        force_recalculate=req.force_recalculate,
    )

    # Attach role_title for response
    role = db.query(IndustryRoleProfile).filter(IndustryRoleProfile.id == analysis.role_id).first()
    res = CareerReadinessAnalysisResponse.model_validate(analysis)
    if role:
        res.role_title = role.role_title
    return res


@router.get(
    "/compare",
    response_model=CareerReadinessComparisonResponse,
    summary="Compare student readiness across multiple permitted role profiles",
)
def compare_career_roles(
    student_id: Optional[uuid.UUID] = Query(None),
    role_ids: Optional[List[uuid.UUID]] = Query(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _parse_uuid(current_user.institution_id)

    if current_user.role == UserRole.STUDENT:
        student_profile = _get_student_profile(db, _parse_uuid(current_user.id), inst_id)
        target_student_id = student_profile.id
    else:
        if not student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="student_id is required for staff queries.",
            )
        target_student_id = student_id

    compared = CareerReadinessAnalysisService.compare_roles(
        db=db,
        student_id=target_student_id,
        institution_id=inst_id,
        role_ids=role_ids,
    )

    return CareerReadinessComparisonResponse(
        student_id=target_student_id,
        compared_roles=compared,
        disclaimer=DEFAULT_CAREER_READINESS_DISCLAIMER,
    )


@router.get(
    "/overview",
    response_model=CareerDashboardOverviewResponse,
    summary="Get aggregated career readiness overview for student workspace",
)
def get_career_overview(
    student_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _parse_uuid(current_user.institution_id)

    if current_user.role == UserRole.STUDENT:
        student_profile = _get_student_profile(db, _parse_uuid(current_user.id), inst_id)
        target_student_id = student_profile.id
    else:
        if not student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="student_id is required for staff queries.",
            )
        target_student_id = student_id

    roles_count = db.query(IndustryRoleProfile).filter(IndustryRoleProfile.is_active == True).count()
    
    latest_analysis = db.query(CareerReadinessAnalysis).filter(
        CareerReadinessAnalysis.student_id == target_student_id
    ).order_by(CareerReadinessAnalysis.created_at.desc()).first()

    verified_proj_count = db.query(StudentProjectEvidence).filter(
        StudentProjectEvidence.student_id == target_student_id,
        StudentProjectEvidence.verification_status == "VERIFIED",
    ).count()

    pending_proj_count = db.query(StudentProjectEvidence).filter(
        StudentProjectEvidence.student_id == target_student_id,
        StudentProjectEvidence.verification_status == "PENDING_REVIEW",
    ).count()

    ev_list = CompetencyEvidenceService.get_student_evidence(db, target_student_id, inst_id)
    demonstrated_c = sum(1 for e in ev_list if e.evidence_state == "DEMONSTRATED")
    developing_c = sum(1 for e in ev_list if e.evidence_state == "DEVELOPING")

    active_gaps_count = db.query(CareerSkillGapFinding).filter(
        CareerSkillGapFinding.student_id == target_student_id,
        CareerSkillGapFinding.status == "ACTIVE",
    ).count()

    active_recs_count = db.query(CareerDevelopmentRecommendation).filter(
        CareerDevelopmentRecommendation.student_id == target_student_id,
        CareerDevelopmentRecommendation.status.in_(["PROPOSED", "ACCEPTED", "IN_PROGRESS"]),
    ).count()

    analysis_res = None
    if latest_analysis:
        analysis_res = CareerReadinessAnalysisResponse.model_validate(latest_analysis)
        role = db.query(IndustryRoleProfile).filter(IndustryRoleProfile.id == latest_analysis.role_id).first()
        if role:
            analysis_res.role_title = role.role_title

    return CareerDashboardOverviewResponse(
        student_id=target_student_id,
        enrolled_roles_count=roles_count,
        latest_analysis=analysis_res,
        verified_projects_count=verified_proj_count,
        pending_projects_count=pending_proj_count,
        demonstrated_competencies_count=demonstrated_c,
        developing_competencies_count=developing_c,
        active_gaps_count=active_gaps_count,
        active_recommendations_count=active_recs_count,
        disclaimer=DEFAULT_CAREER_READINESS_DISCLAIMER,
    )


# =========================================================================
# 5. Career Development Recommendations Endpoints
# =========================================================================

@router.get(
    "/recommendations",
    response_model=List[CareerDevelopmentRecommendationResponse],
    summary="List career development recommendations for a student",
)
def list_recommendations(
    student_id: Optional[uuid.UUID] = Query(None),
    role_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _parse_uuid(current_user.institution_id)

    if current_user.role == UserRole.STUDENT:
        student_profile = _get_student_profile(db, _parse_uuid(current_user.id), inst_id)
        target_student_id = student_profile.id
    else:
        if not student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="student_id is required for staff queries.",
            )
        target_student_id = student_id

    return CareerRecommendationService.list_student_recommendations(
        db, target_student_id, inst_id, role_id=role_id
    )


@router.patch(
    "/recommendations/{recommendation_id}",
    response_model=CareerDevelopmentRecommendationResponse,
    summary="Update career recommendation progress or feedback",
)
def update_recommendation(
    recommendation_id: uuid.UUID,
    rec_in: CareerDevelopmentRecommendationUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    is_staff = current_user.role in (UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN)
    return CareerRecommendationService.update_recommendation(
        db=db,
        recommendation_id=recommendation_id,
        rec_in=rec_in,
        user_id=_parse_uuid(current_user.id),
        is_staff=is_staff,
    )
