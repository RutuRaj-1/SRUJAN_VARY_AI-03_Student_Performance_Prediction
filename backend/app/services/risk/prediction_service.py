import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.academic_data import StudentAcademicProfile, StudentSubjectEnrollment
from app.models.syllabus import AcademicSubject
from app.models.risk import (
    AcademicRiskTarget,
    RiskFeatureSnapshot,
    RiskModelVersion,
    AcademicRiskPrediction,
    AcademicRiskPredictionExplanation,
    RiskPredictionJob,
    DEFAULT_RISK_DISCLAIMER,
)
from app.models.enums import (
    RiskClassification,
    RiskModelType,
    RiskModelStatus,
    RiskPredictionStatus,
    EvidenceSufficiencyLevel,
)
from app.schemas.risk import (
    RiskPredictionGenerateRequest,
    StudentRiskProfileResponse,
    CohortRiskSummaryResponse,
    CohortRiskSummaryItem,
    AcademicRiskExplanationItem,
)
from app.services.risk.target_service import risk_target_service
from app.services.risk.feature_service import risk_feature_service, FEATURE_KEYS
from app.services.risk.training_service import risk_training_service
from app.core.logging import logger


class AcademicRiskPredictionService:
    """
    Inference and explainability engine for Academic Risk Prediction.
    """

    @staticmethod
    def generate_predictions(
        db: Session,
        institution_id: uuid.UUID,
        req: RiskPredictionGenerateRequest,
        triggered_by_profile_id: Optional[uuid.UUID] = None,
    ) -> List[AcademicRiskPrediction]:
        target = risk_target_service.get_target_by_id(db, req.target_id, institution_id)

        # Resolve active model version
        model_version: Optional[RiskModelVersion] = None
        if req.model_version_id:
            model_version = (
                db.query(RiskModelVersion)
                .filter(
                    RiskModelVersion.id == req.model_version_id,
                    RiskModelVersion.institution_id == institution_id,
                )
                .first()
            )
        else:
            model_version = (
                db.query(RiskModelVersion)
                .filter(
                    RiskModelVersion.institution_id == institution_id,
                    RiskModelVersion.target_id == target.id,
                    RiskModelVersion.is_active.is_(True),
                )
                .first()
            )

        # If no active model, auto-initialize deterministic rule baseline
        if not model_version:
            preview = risk_training_service.inspect_dataset_readiness(
                db=db,
                institution_id=institution_id,
                subject_id=req.subject_id,
                target_id=target.id,
                cutoff_date=req.cutoff_date,
            )
            model_version = risk_training_service._train_deterministic_rule_baseline(
                db=db,
                institution_id=institution_id,
                target_id=target.id,
                version_tag=f"baseline-auto-{datetime.now().strftime('%Y%m%d%H%M')}",
                preview=preview,
                trained_by_profile_id=triggered_by_profile_id,
            )

        # Target student(s) resolution
        target_student_ids: List[uuid.UUID] = []
        if req.target_student_id:
            target_student_ids = [req.target_student_id]
        else:
            enrollments = (
                db.query(StudentSubjectEnrollment)
                .filter(
                    StudentSubjectEnrollment.institution_id == institution_id,
                    StudentSubjectEnrollment.subject_id == req.subject_id,
                    StudentSubjectEnrollment.enrollment_status == "ACTIVE",
                )
                .all()
            )
            target_student_ids = [e.student_id for e in enrollments]

        cutoff_date = req.cutoff_date or datetime.now(timezone.utc)
        if cutoff_date.tzinfo is None:
            cutoff_date = cutoff_date.replace(tzinfo=timezone.utc)

        predictions: List[AcademicRiskPrediction] = []

        for student_id in target_student_ids:
            # Slices features strictly on or before cutoff
            snapshot = risk_feature_service.extract_student_features(
                db=db,
                institution_id=institution_id,
                student_id=student_id,
                subject_id=req.subject_id,
                cutoff_date=cutoff_date,
                target_id=target.id,
            )

            pred = AcademicRiskPredictionService._score_student_and_explain(
                db=db,
                institution_id=institution_id,
                student_id=student_id,
                subject_id=req.subject_id,
                target=target,
                model_version=model_version,
                snapshot=snapshot,
                cutoff_date=cutoff_date,
            )
            predictions.append(pred)

        logger.info(f"Generated {len(predictions)} risk predictions for subject {req.subject_id}")
        return predictions

    @staticmethod
    def _score_student_and_explain(
        db: Session,
        institution_id: uuid.UUID,
        student_id: uuid.UUID,
        subject_id: uuid.UUID,
        target: AcademicRiskTarget,
        model_version: RiskModelVersion,
        snapshot: RiskFeatureSnapshot,
        cutoff_date: datetime,
    ) -> AcademicRiskPrediction:
        features = snapshot.feature_vector_json

        # ---------------------------------------------------------------------
        # Sufficiency Gate: If insufficient evidence (< 2 continuous records),
        # return INSUFFICIENT_EVIDENCE explicitly without guessing!
        # ---------------------------------------------------------------------
        if snapshot.evidence_sufficiency == EvidenceSufficiencyLevel.INSUFFICIENT.value:
            prediction = AcademicRiskPrediction(
                institution_id=institution_id,
                student_id=student_id,
                subject_id=subject_id,
                target_id=target.id,
                model_version_id=model_version.id,
                snapshot_id=snapshot.id,
                risk_classification=RiskClassification.INSUFFICIENT_EVIDENCE.value,
                risk_score=None,
                is_calibrated_probability=False,
                evidence_sufficiency=snapshot.evidence_sufficiency,
                prediction_cutoff_date=cutoff_date,
                prediction_status=RiskPredictionStatus.ACTIVE.value,
                scientific_disclaimer=DEFAULT_RISK_DISCLAIMER,
            )
            db.add(prediction)
            db.commit()
            db.refresh(prediction)

            explanation = AcademicRiskPredictionExplanation(
                prediction_id=prediction.id,
                feature_name="evidence_sufficiency",
                feature_value=float(snapshot.eligible_records_count),
                contribution_weight=0.0,
                explanation_text=(
                    f"Available assessment evidence is insufficient for reliable risk classification "
                    f"({snapshot.eligible_records_count} continuous records observed; minimum 2 required)."
                ),
                source_evidence_reference="RiskFeatureSnapshot",
                is_adverse_factor=False,
            )
            db.add(explanation)
            db.commit()
            db.refresh(prediction)
            return prediction

        # ---------------------------------------------------------------------
        # Model Scoring
        # ---------------------------------------------------------------------
        score = 0.5
        explanations_data: List[Dict[str, Any]] = []

        if model_version.model_type == RiskModelType.LOGISTIC_REGRESSION.value:
            coeffs = model_version.parameters_json.get("coefficients", {})
            intercept = float(model_version.parameters_json.get("intercept", 0.0))
            z = intercept
            for key in FEATURE_KEYS:
                val = float(features.get(key, 50.0))
                coef = float(coeffs.get(key, 0.0))
                contrib = coef * val
                z += contrib

                # Explanation for top adverse or protective features
                if abs(coef) > 0.01:
                    is_adverse = contrib > 0  # positive z increases risk probability
                    explanations_data.append({
                        "feature_name": key,
                        "feature_value": val,
                        "contribution_weight": round(contrib, 3),
                        "explanation_text": AcademicRiskPredictionService._format_explanation(key, val, is_adverse),
                        "source_evidence_reference": f"FeatureSnapshot:{key}",
                        "is_adverse_factor": is_adverse,
                    })

            # Sigmoid
            score = 1.0 / (1.0 + np.exp(-np.clip(z, -15.0, 15.0)))
            score = round(float(score), 3)

        elif model_version.model_type == RiskModelType.DECISION_TREE.value:
            # Interpretable tree decision heuristic
            avg = float(features.get("continuous_assessment_average", 50.0))
            gaps = float(features.get("high_severity_learning_gap_count", 0.0))
            att = float(features.get("verified_attendance_percentage", 100.0))

            if avg < 45.0 or gaps >= 2:
                score = 0.85
            elif avg < 60.0 or att < 75.0:
                score = 0.50
            else:
                score = 0.15

            explanations_data.append({
                "feature_name": "continuous_assessment_average",
                "feature_value": avg,
                "contribution_weight": round(0.85 if avg < 45.0 else 0.15, 2),
                "explanation_text": f"Continuous assessment average is {avg}%.",
                "source_evidence_reference": "Assessments",
                "is_adverse_factor": avg < 50.0,
            })

        else:
            # Deterministic Rule Baseline
            rules = model_version.parameters_json.get("rules", [])
            accumulated_weight = 0.0

            avg = float(features.get("continuous_assessment_average", 50.0))
            gaps = float(features.get("high_severity_learning_gap_count", 0.0))
            att = float(features.get("verified_attendance_percentage", 100.0))
            unassessed = float(features.get("unassessed_topic_count", 0.0))

            if avg < 40.0:
                accumulated_weight += 0.4
                explanations_data.append({
                    "feature_name": "continuous_assessment_average",
                    "feature_value": avg,
                    "contribution_weight": 0.4,
                    "explanation_text": f"Continuous assessment average ({avg}%) is critically below 40.0%.",
                    "source_evidence_reference": "Phase 04/05 Continuous Assessments",
                    "is_adverse_factor": True,
                })
            elif avg >= 70.0:
                explanations_data.append({
                    "feature_name": "continuous_assessment_average",
                    "feature_value": avg,
                    "contribution_weight": -0.3,
                    "explanation_text": f"Continuous assessment average ({avg}%) demonstrates strong foundation.",
                    "source_evidence_reference": "Phase 04/05 Continuous Assessments",
                    "is_adverse_factor": False,
                })

            if gaps >= 2:
                accumulated_weight += 0.3
                explanations_data.append({
                    "feature_name": "high_severity_learning_gap_count",
                    "feature_value": gaps,
                    "contribution_weight": 0.3,
                    "explanation_text": f"{int(gaps)} unresolved high-severity topic gaps identified in curriculum.",
                    "source_evidence_reference": "Phase 06 Learning Gap Findings",
                    "is_adverse_factor": True,
                })

            if att < 75.0:
                accumulated_weight += 0.2
                explanations_data.append({
                    "feature_name": "verified_attendance_percentage",
                    "feature_value": att,
                    "contribution_weight": 0.2,
                    "explanation_text": f"Verified attendance rate ({att}%) falls below 75.0% institutional threshold.",
                    "source_evidence_reference": "Phase 04 Attendance Ledger",
                    "is_adverse_factor": True,
                })

            if unassessed >= 3:
                accumulated_weight += 0.1
                explanations_data.append({
                    "feature_name": "unassessed_topic_count",
                    "feature_value": unassessed,
                    "contribution_weight": 0.1,
                    "explanation_text": f"{int(unassessed)} syllabus topics currently lack assessment evaluation.",
                    "source_evidence_reference": "Phase 06 Topic Mastery",
                    "is_adverse_factor": True,
                })

            score = min(1.0, round(accumulated_weight, 2))

        # ---------------------------------------------------------------------
        # Classification Mapping
        # ---------------------------------------------------------------------
        if score >= 0.55:
            classification = RiskClassification.HIGH.value
        elif score >= 0.30:
            classification = RiskClassification.MODERATE.value
        else:
            classification = RiskClassification.LOW.value

        prediction = AcademicRiskPrediction(
            institution_id=institution_id,
            student_id=student_id,
            subject_id=subject_id,
            target_id=target.id,
            model_version_id=model_version.id,
            snapshot_id=snapshot.id,
            risk_classification=classification,
            risk_score=score,
            is_calibrated_probability=False,
            evidence_sufficiency=snapshot.evidence_sufficiency,
            prediction_cutoff_date=cutoff_date,
            prediction_status=RiskPredictionStatus.ACTIVE.value,
            scientific_disclaimer=DEFAULT_RISK_DISCLAIMER,
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)

        # Persist explanations
        for exp in explanations_data:
            item = AcademicRiskPredictionExplanation(
                prediction_id=prediction.id,
                feature_name=exp["feature_name"],
                feature_value=exp["feature_value"],
                contribution_weight=exp["contribution_weight"],
                explanation_text=exp["explanation_text"],
                source_evidence_reference=exp.get("source_evidence_reference"),
                is_adverse_factor=exp["is_adverse_factor"],
            )
            db.add(item)
        db.commit()
        db.refresh(prediction)
        return prediction

    @staticmethod
    def _format_explanation(feature_name: str, value: float, is_adverse: bool) -> str:
        readable_names = {
            "continuous_assessment_average": f"Continuous assessment score is {value}%",
            "assessment_score_trajectory": f"Assessment trend slope delta is {value}%",
            "topic_mastery_ratio": f"Topic mastery ratio is {int(value * 100)}%",
            "needs_attention_topic_count": f"{int(value)} topics require attention (<50%)",
            "unassessed_topic_count": f"{int(value)} curriculum topics currently unassessed",
            "high_severity_learning_gap_count": f"{int(value)} high-severity learning gaps identified",
            "clo_attainment_ratio": f"Course Learning Outcome attainment is {int(value * 100)}%",
            "verified_attendance_percentage": f"Verified attendance rate is {value}%",
        }
        prefix = "Adverse contributor: " if is_adverse else "Protective contributor: "
        return prefix + readable_names.get(feature_name, f"{feature_name} = {value}")

    @staticmethod
    def get_student_risk_profile(
        db: Session,
        institution_id: uuid.UUID,
        student_id: uuid.UUID,
        subject_id: uuid.UUID,
    ) -> StudentRiskProfileResponse:
        student = (
            db.query(StudentAcademicProfile)
            .filter(
                StudentAcademicProfile.id == student_id,
                StudentAcademicProfile.institution_id == institution_id,
            )
            .first()
        )
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found.")

        subject = db.query(AcademicSubject).filter(AcademicSubject.id == subject_id).first()
        if not subject:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found.")

        # Latest active prediction
        pred = (
            db.query(AcademicRiskPrediction)
            .filter(
                AcademicRiskPrediction.student_id == student_id,
                AcademicRiskPrediction.subject_id == subject_id,
                AcademicRiskPrediction.prediction_status == RiskPredictionStatus.ACTIVE.value,
            )
            .order_by(AcademicRiskPrediction.created_at.desc())
            .first()
        )

        history_count = (
            db.query(func.count(AcademicRiskPrediction.id))
            .filter(
                AcademicRiskPrediction.student_id == student_id,
                AcademicRiskPrediction.subject_id == subject_id,
            )
            .scalar()
            or 0
        )

        if not pred:
            # Fallback when prediction hasn't been generated yet
            default_target = risk_target_service.get_or_create_default_target(db, institution_id, subject_id)
            return StudentRiskProfileResponse(
                student_id=student.id,
                student_name=f"{student.first_name} {student.last_name}",
                enrollment_number=student.enrollment_number,
                subject_id=subject.id,
                subject_code=subject.code,
                subject_name=subject.name,
                target_id=default_target.id,
                target_name=default_target.target_name,
                risk_classification=RiskClassification.MODEL_NOT_READY.value,
                risk_score=None,
                is_calibrated_probability=False,
                evidence_sufficiency=EvidenceSufficiencyLevel.INSUFFICIENT.value,
                model_type=None,
                model_version_tag=None,
                prediction_cutoff_date=datetime.now(timezone.utc),
                explanations=[],
                historical_predictions_count=0,
                supporting_academic_evidence={
                    "status": "No active prediction generated yet. Faculty can trigger prediction batch."
                },
                scientific_disclaimer=DEFAULT_RISK_DISCLAIMER,
            )

        model_version = pred.model_version
        explanations = [
            AcademicRiskExplanationItem.model_validate(e) for e in pred.explanations
        ]

        return StudentRiskProfileResponse(
            student_id=student.id,
            student_name=f"{student.first_name} {student.last_name}",
            enrollment_number=student.enrollment_number,
            subject_id=subject.id,
            subject_code=subject.code,
            subject_name=subject.name,
            target_id=pred.target_id,
            target_name=pred.target.target_name if pred.target else "Course Deficit",
            risk_classification=pred.risk_classification,
            risk_score=pred.risk_score,
            is_calibrated_probability=pred.is_calibrated_probability,
            evidence_sufficiency=pred.evidence_sufficiency,
            model_type=model_version.model_type if model_version else None,
            model_version_tag=model_version.version_tag if model_version else None,
            prediction_cutoff_date=pred.prediction_cutoff_date,
            explanations=explanations,
            historical_predictions_count=history_count,
            supporting_academic_evidence=pred.snapshot.feature_vector_json if pred.snapshot else {},
            scientific_disclaimer=pred.scientific_disclaimer,
        )

    @staticmethod
    def get_cohort_risk_summary(
        db: Session,
        institution_id: uuid.UUID,
        subject_id: uuid.UUID,
    ) -> CohortRiskSummaryResponse:
        subject = db.query(AcademicSubject).filter(AcademicSubject.id == subject_id).first()
        if not subject:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found.")

        target = risk_target_service.get_or_create_default_target(db, institution_id, subject_id)

        enrollments = (
            db.query(StudentSubjectEnrollment)
            .filter(
                StudentSubjectEnrollment.institution_id == institution_id,
                StudentSubjectEnrollment.subject_id == subject_id,
                StudentSubjectEnrollment.enrollment_status == "ACTIVE",
            )
            .all()
        )

        high_count = 0
        mod_count = 0
        low_count = 0
        insuff_count = 0
        not_ready_count = 0
        latest_date = None
        active_model = None
        student_rows: List[CohortRiskSummaryItem] = []

        for enr in enrollments:
            student = enr.student
            if not student:
                continue

            pred = (
                db.query(AcademicRiskPrediction)
                .filter(
                    AcademicRiskPrediction.student_id == student.id,
                    AcademicRiskPrediction.subject_id == subject_id,
                    AcademicRiskPrediction.prediction_status == RiskPredictionStatus.ACTIVE.value,
                )
                .order_by(AcademicRiskPrediction.created_at.desc())
                .first()
            )

            if pred:
                latest_date = pred.created_at if (not latest_date or pred.created_at > latest_date) else latest_date
                if pred.model_version and not active_model:
                    active_model = pred.model_version

                if pred.risk_classification == RiskClassification.HIGH.value:
                    high_count += 1
                elif pred.risk_classification == RiskClassification.MODERATE.value:
                    mod_count += 1
                elif pred.risk_classification == RiskClassification.LOW.value:
                    low_count += 1
                elif pred.risk_classification == RiskClassification.INSUFFICIENT_EVIDENCE.value:
                    insuff_count += 1
                else:
                    not_ready_count += 1

                top_adverse = None
                adverse_exps = [e for e in pred.explanations if e.is_adverse_factor]
                if adverse_exps:
                    top_adverse = adverse_exps[0].explanation_text

                student_rows.append(
                    CohortRiskSummaryItem(
                        student_id=student.id,
                        student_name=f"{student.first_name} {student.last_name}",
                        enrollment_number=student.enrollment_number,
                        risk_classification=pred.risk_classification,
                        risk_score=pred.risk_score,
                        evidence_sufficiency=pred.evidence_sufficiency,
                        top_adverse_factor=top_adverse,
                    )
                )
            else:
                not_ready_count += 1
                student_rows.append(
                    CohortRiskSummaryItem(
                        student_id=student.id,
                        student_name=f"{student.first_name} {student.last_name}",
                        enrollment_number=student.enrollment_number,
                        risk_classification=RiskClassification.MODEL_NOT_READY.value,
                        risk_score=None,
                        evidence_sufficiency=EvidenceSufficiencyLevel.INSUFFICIENT.value,
                        top_adverse_factor=None,
                    )
                )

        return CohortRiskSummaryResponse(
            subject_id=subject.id,
            subject_code=subject.code,
            subject_name=subject.name,
            target_id=target.id,
            target_name=target.target_name,
            total_enrolled=len(enrollments),
            analyzed_students_count=len(enrollments) - not_ready_count,
            high_risk_count=high_count,
            moderate_risk_count=mod_count,
            low_risk_count=low_count,
            insufficient_evidence_count=insuff_count,
            model_not_ready_count=not_ready_count,
            active_model_version=active_model.version_tag if active_model else None,
            active_model_type=active_model.model_type if active_model else None,
            latest_prediction_date=latest_date,
            students=student_rows,
            scientific_disclaimer=DEFAULT_RISK_DISCLAIMER,
        )


academic_risk_service = AcademicRiskPredictionService()
