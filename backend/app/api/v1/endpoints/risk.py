import uuid
from typing import List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_active_user, CurrentUser, require_roles
from app.models.academic_data import StudentAcademicProfile
from app.models.risk import AcademicRiskTarget, RiskModelVersion, AcademicRiskPrediction
from app.models.enums import UserRole
from app.schemas.risk import (
    RiskTargetCreateRequest,
    RiskTargetUpdateRequest,
    RiskTargetResponse,
    DatasetPreviewRequest,
    DatasetPreviewResponse,
    RiskModelTrainRequest,
    RiskModelVersionResponse,
    RiskPredictionGenerateRequest,
    AcademicRiskPredictionResponse,
    StudentRiskProfileResponse,
    CohortRiskSummaryResponse,
    AcademicRiskExplanationItem,
    RiskReadinessResponse,
)
from app.services.risk.target_service import risk_target_service
from app.services.risk.training_service import risk_training_service
from app.services.risk.prediction_service import academic_risk_service
from app.core.logging import logger

router = APIRouter()


def _parse_uuid(val: Any) -> Optional[uuid.UUID]:
    if val is None:
        return None
    if isinstance(val, uuid.UUID):
        return val
    return uuid.UUID(str(val))


def _verify_student_self_access(db: Session, current_user: CurrentUser, requested_student_id: uuid.UUID):
    user_role = current_user.role if isinstance(current_user.role, str) else current_user.role.value
    user_uuid = _parse_uuid(current_user.user_id)
    inst_uuid = _parse_uuid(current_user.institution_id)

    if user_role == UserRole.STUDENT.value:
        student_rec = (
            db.query(StudentAcademicProfile)
            .filter(
                StudentAcademicProfile.profile_id == user_uuid,
                StudentAcademicProfile.institution_id == inst_uuid,
            )
            .first()
        )
        if not student_rec or student_rec.id != requested_student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Students may only inspect their own academic risk records.",
            )
    elif user_role == UserRole.PLACEMENT_OFFICER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Placement officers are restricted from academic risk prediction.",
        )


# =========================================================================
# 1. Target Configuration Endpoints
# =========================================================================

@router.get("/targets", response_model=List[RiskTargetResponse])
def list_targets(
    subject_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    user_role = current_user.role if isinstance(current_user.role, str) else current_user.role.value
    if user_role == UserRole.PLACEMENT_OFFICER.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    inst_id = _parse_uuid(current_user.institution_id)
    return risk_target_service.get_targets(db, inst_id, subject_id)


@router.post(
    "/targets",
    response_model=RiskTargetResponse,
    dependencies=[Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN]))],
)
def create_target(
    req: RiskTargetCreateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _parse_uuid(current_user.institution_id)
    return risk_target_service.create_target(db, inst_id, req)


@router.get("/targets/{target_id}", response_model=RiskTargetResponse)
def get_target(
    target_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _parse_uuid(current_user.institution_id)
    return risk_target_service.get_target_by_id(db, target_id, inst_id)


@router.put(
    "/targets/{target_id}",
    response_model=RiskTargetResponse,
    dependencies=[Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN]))],
)
def update_target(
    target_id: uuid.UUID,
    req: RiskTargetUpdateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _parse_uuid(current_user.institution_id)
    return risk_target_service.update_target(db, target_id, inst_id, req)


# =========================================================================
# 2. Dataset & Readiness Endpoints
# =========================================================================

@router.get(
    "/readiness",
    response_model=RiskReadinessResponse,
    dependencies=[Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.FACULTY]))],
)
def get_risk_readiness(
    subject_id: uuid.UUID = Query(...),
    target_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _parse_uuid(current_user.institution_id)
    target = (
        risk_target_service.get_target_by_id(db, target_id, inst_id)
        if target_id
        else risk_target_service.get_or_create_default_target(db, inst_id, subject_id)
    )

    preview = risk_training_service.inspect_dataset_readiness(
        db, inst_id, subject_id, target.id
    )

    active_model = (
        db.query(RiskModelVersion)
        .filter(
            RiskModelVersion.institution_id == inst_id,
            RiskModelVersion.target_id == target.id,
            RiskModelVersion.is_active.is_(True),
        )
        .first()
    )

    return RiskReadinessResponse(
        institution_id=inst_id,
        subject_id=subject_id,
        target_id=target.id,
        is_target_configured=target.status == "ACTIVE",
        target_status=target.status,
        total_historical_records=preview.total_candidates,
        labeled_samples_count=preview.eligible_samples_count,
        positive_class_count=preview.positive_class_count,
        negative_class_count=preview.negative_class_count,
        is_dataset_ready_for_training=preview.readiness_status == "READY_FOR_TRAINING",
        active_deployed_model=active_model.version_tag if active_model else "None (Deterministic Rule Baseline Active)",
        readiness_notes=preview.readiness_reasons,
        scientific_disclaimer=preview.scientific_disclaimer,
    )


@router.post(
    "/datasets/preview",
    response_model=DatasetPreviewResponse,
    dependencies=[Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.FACULTY]))],
)
def preview_training_dataset(
    req: DatasetPreviewRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _parse_uuid(current_user.institution_id)
    return risk_training_service.inspect_dataset_readiness(
        db=db,
        institution_id=inst_id,
        subject_id=req.subject_id,
        target_id=req.target_id,
        cutoff_date=req.cutoff_date,
    )


# =========================================================================
# 3. Model Training & Registry Endpoints
# =========================================================================

@router.post(
    "/models/train",
    response_model=RiskModelVersionResponse,
    dependencies=[Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.FACULTY]))],
)
def train_risk_model(
    req: RiskModelTrainRequest,
    subject_id: uuid.UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _parse_uuid(current_user.institution_id)
    user_id = _parse_uuid(current_user.user_id)
    return risk_training_service.train_and_evaluate_model(
        db=db,
        institution_id=inst_id,
        subject_id=subject_id,
        req=req,
        trained_by_profile_id=user_id,
    )


@router.get(
    "/models",
    response_model=List[RiskModelVersionResponse],
    dependencies=[Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.FACULTY]))],
)
def list_risk_models(
    target_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _parse_uuid(current_user.institution_id)
    query = db.query(RiskModelVersion).filter(RiskModelVersion.institution_id == inst_id)
    if target_id:
        query = query.filter(RiskModelVersion.target_id == target_id)
    return query.order_by(RiskModelVersion.created_at.desc()).all()


@router.post(
    "/models/{model_id}/deploy",
    response_model=RiskModelVersionResponse,
    dependencies=[Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN]))],
)
def deploy_risk_model(
    model_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _parse_uuid(current_user.institution_id)
    return risk_training_service.deploy_model_version(db, inst_id, model_id)


# =========================================================================
# 4. Prediction Generation & Retrieval Endpoints
# =========================================================================

@router.post(
    "/predictions/generate",
    response_model=List[AcademicRiskPredictionResponse],
    dependencies=[Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.FACULTY]))],
)
def generate_risk_predictions(
    req: RiskPredictionGenerateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _parse_uuid(current_user.institution_id)
    user_id = _parse_uuid(current_user.user_id)
    predictions = academic_risk_service.generate_predictions(
        db=db,
        institution_id=inst_id,
        req=req,
        triggered_by_profile_id=user_id,
    )
    return [
        AcademicRiskPredictionResponse(
            id=p.id,
            institution_id=p.institution_id,
            student_id=p.student_id,
            subject_id=p.subject_id,
            target_id=p.target_id,
            model_version_id=p.model_version_id,
            risk_classification=p.risk_classification,
            risk_score=p.risk_score,
            is_calibrated_probability=p.is_calibrated_probability,
            evidence_sufficiency=p.evidence_sufficiency,
            prediction_cutoff_date=p.prediction_cutoff_date,
            prediction_status=p.prediction_status,
            scientific_disclaimer=p.scientific_disclaimer,
            created_at=p.created_at,
            explanations=[AcademicRiskExplanationItem.model_validate(e) for e in p.explanations],
        )
        for p in predictions
    ]


@router.get("/students/{student_id}/subjects/{subject_id}/profile", response_model=StudentRiskProfileResponse)
def get_student_risk_profile(
    student_id: uuid.UUID,
    subject_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    _verify_student_self_access(db, current_user, student_id)
    inst_id = _parse_uuid(current_user.institution_id)
    return academic_risk_service.get_student_risk_profile(
        db=db,
        institution_id=inst_id,
        student_id=student_id,
        subject_id=subject_id,
    )


@router.get(
    "/cohort/subjects/{subject_id}/summary",
    response_model=CohortRiskSummaryResponse,
    dependencies=[Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.FACULTY]))],
)
def get_cohort_risk_summary(
    subject_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _parse_uuid(current_user.institution_id)
    return academic_risk_service.get_cohort_risk_summary(
        db=db,
        institution_id=inst_id,
        subject_id=subject_id,
    )


@router.get("/predictions/{prediction_id}/explanation", response_model=List[AcademicRiskExplanationItem])
def get_prediction_explanations(
    prediction_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    inst_id = _parse_uuid(current_user.institution_id)
    pred = (
        db.query(AcademicRiskPrediction)
        .filter(
            AcademicRiskPrediction.id == prediction_id,
            AcademicRiskPrediction.institution_id == inst_id,
        )
        .first()
    )
    if not pred:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found.")

    _verify_student_self_access(db, current_user, pred.student_id)
    return [AcademicRiskExplanationItem.model_validate(e) for e in pred.explanations]
