import uuid
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.core.security import get_current_active_user, CurrentUser, require_roles
from app.models.enums import UserRole
from app.models.academic_data import StudentAcademicProfile
from app.models.mastery import (
    MasteryAnalysisJob,
    MasteryEvidenceRecord,
    TopicMasteryResult,
    LearningOutcomeAttainmentResult,
    LearningGapFinding,
)
from app.schemas.mastery import (
    MasteryAnalyzeRequest,
    MasteryJobResponse,
    StudentMasteryProfileResponse,
    TopicMasteryDetailResponse,
    LearningOutcomeAttainmentDetailResponse,
    LearningGapFindingResponse,
    MasteryEvidenceItemResponse,
    StudentPerformanceTrendResponse,
    CohortMasterySummaryResponse,
)
from app.services.mastery.analytics_service import MasteryAnalyticsService

router = APIRouter()


# =========================================================================
# 1. Mastery Analysis Execution & Jobs
# =========================================================================

@router.post("/analyze", response_model=MasteryJobResponse, status_code=status.HTTP_201_CREATED)
def trigger_mastery_analysis(
    payload: MasteryAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN])),
):
    inst_id = uuid.UUID(current_user.institution_id)
    creator_id = uuid.UUID(current_user.user_id) if current_user.user_id else None

    job = MasteryAnalyticsService.execute_analysis_job(
        db=db,
        institution_id=inst_id,
        creator_id=creator_id,
        request=payload,
    )
    return job


@router.get("/jobs", response_model=List[MasteryJobResponse])
def list_mastery_jobs(
    subject_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = uuid.UUID(current_user.institution_id)
    query = select(MasteryAnalysisJob).where(MasteryAnalysisJob.institution_id == inst_id)
    if subject_id:
        query = query.where(MasteryAnalysisJob.subject_id == subject_id)
    query = query.order_by(MasteryAnalysisJob.created_at.desc())
    return db.execute(query).scalars().all()


@router.get("/jobs/{job_id}", response_model=MasteryJobResponse)
def get_mastery_job_detail(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = uuid.UUID(current_user.institution_id)
    job = db.execute(
        select(MasteryAnalysisJob).where(
            MasteryAnalysisJob.id == job_id,
            MasteryAnalysisJob.institution_id == inst_id,
        )
    ).scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mastery analysis job not found.")
    return job


# =========================================================================
# 2. Student Mastery Profile & Performance
# =========================================================================

@router.get("/students/{student_id}", response_model=StudentMasteryProfileResponse)
def get_student_mastery_profile(
    student_id: uuid.UUID,
    subject_id: uuid.UUID = Query(..., description="Target academic subject for mastery profile"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = uuid.UUID(current_user.institution_id)

    # Authorization Guard: Students may only view their own profile
    if current_user.role == UserRole.STUDENT:
        user_prof = db.execute(
            select(StudentAcademicProfile).where(
                StudentAcademicProfile.profile_id == uuid.UUID(current_user.user_id),
                StudentAcademicProfile.institution_id == inst_id,
            )
        ).scalar_one_or_none()

        if not user_prof or user_prof.id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden. You may only view your own learning mastery profile.",
            )

    try:
        profile = MasteryAnalyticsService.get_student_mastery_profile(
            db=db,
            institution_id=inst_id,
            student_id=student_id,
            subject_id=subject_id,
        )
        return profile
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/students/{student_id}/trends", response_model=StudentPerformanceTrendResponse)
def get_student_performance_trends(
    student_id: uuid.UUID,
    subject_id: uuid.UUID = Query(..., description="Target academic subject"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = uuid.UUID(current_user.institution_id)

    if current_user.role == UserRole.STUDENT:
        user_prof = db.execute(
            select(StudentAcademicProfile).where(
                StudentAcademicProfile.profile_id == uuid.UUID(current_user.user_id),
                StudentAcademicProfile.institution_id == inst_id,
            )
        ).scalar_one_or_none()

        if not user_prof or user_prof.id != student_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")

    return MasteryAnalyticsService.get_performance_trends(
        db=db,
        institution_id=inst_id,
        student_id=student_id,
        subject_id=subject_id,
    )


@router.get("/students/{student_id}/gaps", response_model=List[LearningGapFindingResponse])
def list_student_learning_gaps(
    student_id: uuid.UUID,
    subject_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = uuid.UUID(current_user.institution_id)

    if current_user.role == UserRole.STUDENT:
        user_prof = db.execute(
            select(StudentAcademicProfile).where(
                StudentAcademicProfile.profile_id == uuid.UUID(current_user.user_id),
                StudentAcademicProfile.institution_id == inst_id,
            )
        ).scalar_one_or_none()

        if not user_prof or user_prof.id != student_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")

    query = select(LearningGapFinding).where(
        LearningGapFinding.institution_id == inst_id,
        LearningGapFinding.student_id == student_id,
        LearningGapFinding.status == "OPEN",
    )
    if subject_id:
        query = query.where(LearningGapFinding.subject_id == subject_id)

    query = query.order_by(LearningGapFinding.created_at.desc())
    gaps = db.execute(query).scalars().all()

    # Form response with joined names
    results = []
    for g in gaps:
        results.append(
            LearningGapFindingResponse(
                id=g.id,
                subject_id=g.subject_id,
                topic_id=g.topic_id,
                topic_name=g.topic.topic_name if g.topic else None,
                learning_outcome_id=g.learning_outcome_id,
                outcome_code=g.learning_outcome.outcome_code if g.learning_outcome else None,
                finding_type=g.finding_type,
                severity=g.severity,
                evidence_summary=g.evidence_summary,
                supporting_evidence_refs=g.supporting_evidence_refs or {},
                recommended_review_action=g.recommended_review_action,
                status=g.status,
                created_at=g.created_at,
            )
        )
    return results


# =========================================================================
# 3. Cohort Mastery & Faculty Analytics
# =========================================================================

@router.get("/cohort/{subject_id}/summary", response_model=CohortMasterySummaryResponse)
def get_cohort_mastery_summary(
    subject_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles([UserRole.FACULTY, UserRole.INSTITUTION_ADMIN, UserRole.SUPER_ADMIN, UserRole.PLACEMENT_OFFICER])),
):
    inst_id = uuid.UUID(current_user.institution_id)
    try:
        return MasteryAnalyticsService.get_cohort_mastery_summary(
            db=db,
            institution_id=inst_id,
            subject_id=subject_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# =========================================================================
# 4. Evidence Inspection & Auditability
# =========================================================================

@router.get("/results/{result_id}/evidence", response_model=List[MasteryEvidenceItemResponse])
def inspect_result_contributing_evidence(
    result_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = uuid.UUID(current_user.institution_id)
    result = db.execute(
        select(TopicMasteryResult).where(
            TopicMasteryResult.id == result_id,
            TopicMasteryResult.institution_id == inst_id,
        )
    ).scalar_one_or_none()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic mastery result not found.")

    # Guard student access
    if current_user.role == UserRole.STUDENT:
        user_prof = db.execute(
            select(StudentAcademicProfile).where(
                StudentAcademicProfile.profile_id == uuid.UUID(current_user.user_id),
                StudentAcademicProfile.institution_id == inst_id,
            )
        ).scalar_one_or_none()
        if not user_prof or user_prof.id != result.student_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")

    # Fetch eligible evidence records for this topic and analysis job
    evidence_rows = db.execute(
        select(MasteryEvidenceRecord).where(
            MasteryEvidenceRecord.analysis_job_id == result.analysis_job_id,
            MasteryEvidenceRecord.student_id == result.student_id,
            MasteryEvidenceRecord.topic_id == result.topic_id,
            MasteryEvidenceRecord.eligibility_status == "ELIGIBLE",
        ).order_by(MasteryEvidenceRecord.evidence_timestamp.asc())
    ).scalars().all()

    items = []
    for ev in evidence_rows:
        items.append(
            MasteryEvidenceItemResponse(
                id=ev.id,
                source_entity_type=ev.source_entity_type,
                source_entity_id=ev.source_entity_id,
                assessment_id=ev.assessment_id,
                assessment_name=ev.assessment.assessment_name if ev.assessment else None,
                question_id=ev.question_id,
                question_text=ev.question.question_text if ev.question else None,
                marks_obtained=ev.marks_obtained,
                maximum_marks=ev.maximum_marks,
                eligibility_status=ev.eligibility_status,
                exclusion_reason=ev.exclusion_reason,
                mapping_status=ev.mapping_status,
                evaluation_status=ev.evaluation_status,
                verification_status=ev.verification_status,
                bloom_level=ev.bloom_level,
                is_practice_assessment=ev.is_practice_assessment,
                evidence_timestamp=ev.evidence_timestamp,
            )
        )
    return items


@router.get("/results/{result_id}/excluded-evidence", response_model=List[MasteryEvidenceItemResponse])
def inspect_result_excluded_evidence(
    result_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = uuid.UUID(current_user.institution_id)
    result = db.execute(
        select(TopicMasteryResult).where(
            TopicMasteryResult.id == result_id,
            TopicMasteryResult.institution_id == inst_id,
        )
    ).scalar_one_or_none()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic mastery result not found.")

    if current_user.role == UserRole.STUDENT:
        user_prof = db.execute(
            select(StudentAcademicProfile).where(
                StudentAcademicProfile.profile_id == uuid.UUID(current_user.user_id),
                StudentAcademicProfile.institution_id == inst_id,
            )
        ).scalar_one_or_none()
        if not user_prof or user_prof.id != result.student_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")

    excluded_rows = db.execute(
        select(MasteryEvidenceRecord).where(
            MasteryEvidenceRecord.analysis_job_id == result.analysis_job_id,
            MasteryEvidenceRecord.student_id == result.student_id,
            MasteryEvidenceRecord.eligibility_status == "EXCLUDED",
        ).order_by(MasteryEvidenceRecord.created_at.asc())
    ).scalars().all()

    items = []
    for ev in excluded_rows:
        items.append(
            MasteryEvidenceItemResponse(
                id=ev.id,
                source_entity_type=ev.source_entity_type,
                source_entity_id=ev.source_entity_id,
                assessment_id=ev.assessment_id,
                assessment_name=ev.assessment.assessment_name if ev.assessment else None,
                question_id=ev.question_id,
                question_text=ev.question.question_text if ev.question else None,
                marks_obtained=ev.marks_obtained,
                maximum_marks=ev.maximum_marks,
                eligibility_status=ev.eligibility_status,
                exclusion_reason=ev.exclusion_reason,
                mapping_status=ev.mapping_status,
                evaluation_status=ev.evaluation_status,
                verification_status=ev.verification_status,
                bloom_level=ev.bloom_level,
                is_practice_assessment=ev.is_practice_assessment,
                evidence_timestamp=ev.evidence_timestamp,
            )
        )
    return items
