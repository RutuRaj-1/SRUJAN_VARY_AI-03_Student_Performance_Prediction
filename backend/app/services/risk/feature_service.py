import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.academic_data import StudentAcademicProfile, StudentAttendanceRecord, StudentAssessmentRecord
from app.models.assessment import AssessmentAttempt, AssessmentOnlineStatus
from app.models.mastery import TopicMasteryResult, LearningOutcomeAttainmentResult, LearningGapFinding
from app.models.syllabus import SyllabusTopic, LearningOutcome
from app.models.risk import RiskFeatureSnapshot
from app.models.enums import (
    EvidenceSufficiencyLevel,
    MasteryStatus,
    AttainmentStatus,
    LearningGapSeverity,
)
from app.services.risk.leakage_validator import leakage_validator, TemporalLeakageException
from app.core.logging import logger

FEATURE_KEYS = [
    "continuous_assessment_average",
    "assessment_score_trajectory",
    "topic_mastery_ratio",
    "needs_attention_topic_count",
    "unassessed_topic_count",
    "high_severity_learning_gap_count",
    "clo_attainment_ratio",
    "verified_attendance_percentage",
]


class RiskFeatureEngineeringService:
    """
    Extracts time-bounded, verified features for students strictly on or before observation_cutoff_date.
    Guarantees temporal causality and full data provenance.
    """

    @staticmethod
    def extract_student_features(
        db: Session,
        institution_id: uuid.UUID,
        student_id: uuid.UUID,
        subject_id: uuid.UUID,
        cutoff_date: Optional[datetime] = None,
        target_id: Optional[uuid.UUID] = None,
    ) -> RiskFeatureSnapshot:
        if cutoff_date is None:
            cutoff_date = datetime.now(timezone.utc)
        elif cutoff_date.tzinfo is None:
            cutoff_date = cutoff_date.replace(tzinfo=timezone.utc)

        features: Dict[str, float] = {}
        provenance: Dict[str, Any] = {}
        eligible_records_count = 0

        # ---------------------------------------------------------------------
        # 1. Continuous Assessment Performance (Phase 04 & 05)
        # Excludes FINAL_EXAM to prevent target leakage!
        # ---------------------------------------------------------------------
        attempts = (
            db.query(AssessmentAttempt)
            .filter(
                AssessmentAttempt.student_id == student_id,
                AssessmentAttempt.submitted_at.isnot(None),
                AssessmentAttempt.submitted_at <= cutoff_date,
            )
            .all()
        )

        assessment_scores: List[float] = []
        for attempt in attempts:
            leakage_validator.assert_record_precedes_cutoff(attempt.submitted_at, cutoff_date, str(attempt.id))
            if attempt.assessment and attempt.assessment.subject_id == subject_id:
                # Do NOT use final exam as feature
                if attempt.assessment.assessment_type == "FINAL_EXAM":
                    continue
                if attempt.marks_obtained is not None and attempt.total_marks > 0:
                    pct = (attempt.marks_obtained / attempt.total_marks) * 100.0
                    assessment_scores.append(pct)
                    eligible_records_count += 1

        # Also inspect Phase 04 verified gradebook records
        gradebook_records = (
            db.query(StudentAssessmentRecord)
            .join(StudentAssessmentRecord.assessment)
            .filter(
                StudentAssessmentRecord.student_id == student_id,
                StudentAssessmentRecord.assessment.property.mapper.class_.subject_id == subject_id,
                StudentAssessmentRecord.recorded_at <= cutoff_date,
                StudentAssessmentRecord.verification_status == "VERIFIED",
            )
            .all()
        )
        for g_rec in gradebook_records:
            if g_rec.assessment and g_rec.assessment.assessment_type == "FINAL_EXAM":
                continue
            if g_rec.marks_obtained is not None and g_rec.maximum_marks_snapshot > 0:
                pct = (g_rec.marks_obtained / g_rec.maximum_marks_snapshot) * 100.0
                assessment_scores.append(pct)
                eligible_records_count += 1

        if assessment_scores:
            avg_score = sum(assessment_scores) / len(assessment_scores)
            features["continuous_assessment_average"] = round(avg_score, 2)
            # Trajectory (slope/delta between recent and older assessments)
            if len(assessment_scores) >= 2:
                trajectory = assessment_scores[-1] - assessment_scores[0]
                features["assessment_score_trajectory"] = round(trajectory, 2)
            else:
                features["assessment_score_trajectory"] = 0.0
        else:
            features["continuous_assessment_average"] = 50.0  # neutral prior when unassessed
            features["assessment_score_trajectory"] = 0.0

        provenance["continuous_assessment_average"] = {
            "source": "Phase 04/05 Continuous Assessments",
            "count": len(assessment_scores),
            "cutoff_applied": cutoff_date.isoformat(),
        }

        # ---------------------------------------------------------------------
        # 2. Learning Mastery & Topic Gaps (Phase 06)
        # ---------------------------------------------------------------------
        total_topics_count = (
            db.query(func.count(SyllabusTopic.id))
            .join(SyllabusTopic.unit)
            .join(SyllabusTopic.unit.property.mapper.class_.document)
            .filter(SyllabusTopic.unit.property.mapper.class_.document.property.mapper.class_.subject_id == subject_id)
            .scalar()
            or 0
        )

        topic_results = (
            db.query(TopicMasteryResult)
            .filter(
                TopicMasteryResult.student_id == student_id,
                TopicMasteryResult.subject_id == subject_id,
                TopicMasteryResult.calculated_at <= cutoff_date,
            )
            .all()
        )

        mastered_count = 0
        needs_attention_count = 0
        assessed_topics = set()
        for tr in topic_results:
            assessed_topics.add(tr.topic_id)
            if tr.mastery_status == MasteryStatus.MASTERED.value:
                mastered_count += 1
            elif tr.mastery_status == MasteryStatus.NEEDS_ATTENTION.value:
                needs_attention_count += 1
            if tr.eligible_question_count > 0:
                eligible_records_count += 1

        unassessed_count = max(0, total_topics_count - len(assessed_topics))
        features["topic_mastery_ratio"] = round((mastered_count / total_topics_count) if total_topics_count > 0 else 0.0, 2)
        features["needs_attention_topic_count"] = float(needs_attention_count)
        features["unassessed_topic_count"] = float(unassessed_count)

        provenance["topic_mastery"] = {
            "source": "Phase 06 Topic Mastery Results",
            "total_topics": total_topics_count,
            "mastered": mastered_count,
            "needs_attention": needs_attention_count,
            "unassessed": unassessed_count,
        }

        # ---------------------------------------------------------------------
        # 3. Learning Gaps Discovery (Phase 06)
        # ---------------------------------------------------------------------
        gaps = (
            db.query(LearningGapFinding)
            .filter(
                LearningGapFinding.student_id == student_id,
                LearningGapFinding.subject_id == subject_id,
                LearningGapFinding.created_at <= cutoff_date,
                LearningGapFinding.status != "RESOLVED",
            )
            .all()
        )
        critical_gaps = [g for g in gaps if g.severity in (LearningGapSeverity.CRITICAL.value, LearningGapSeverity.HIGH.value)]
        features["high_severity_learning_gap_count"] = float(len(critical_gaps))
        provenance["learning_gaps"] = {
            "source": "Phase 06 Learning Gap Findings",
            "active_gaps_count": len(gaps),
            "high_severity_count": len(critical_gaps),
        }

        # ---------------------------------------------------------------------
        # 4. Course Learning Outcome Attainment (Phase 06)
        # ---------------------------------------------------------------------
        clos = (
            db.query(LearningOutcomeAttainmentResult)
            .filter(
                LearningOutcomeAttainmentResult.student_id == student_id,
                LearningOutcomeAttainmentResult.subject_id == subject_id,
                LearningOutcomeAttainmentResult.calculated_at <= cutoff_date,
            )
            .all()
        )
        attained_clo_count = sum(1 for c in clos if c.attainment_status == AttainmentStatus.ATTAINED.value)
        features["clo_attainment_ratio"] = round((attained_clo_count / len(clos)) if clos else 0.0, 2)
        provenance["clo_attainment"] = {
            "source": "Phase 06 Outcome Attainment",
            "total_measured": len(clos),
            "attained_count": attained_clo_count,
        }

        # ---------------------------------------------------------------------
        # 5. Verified Attendance Rate (Phase 04)
        # ---------------------------------------------------------------------
        attendance_records = (
            db.query(StudentAttendanceRecord)
            .filter(
                StudentAttendanceRecord.student_id == student_id,
                StudentAttendanceRecord.subject_id == subject_id,
                StudentAttendanceRecord.attendance_date <= cutoff_date,
            )
            .all()
        )
        if attendance_records:
            present_count = sum(1 for a in attendance_records if a.attendance_status == "PRESENT")
            # Only count non-exempt sessions in denominator
            valid_sessions = [a for a in attendance_records if a.attendance_status not in ("EXEMPTED", "LEAVE_APPROVED")]
            denom = len(valid_sessions) if valid_sessions else len(attendance_records)
            att_rate = (present_count / denom) * 100.0 if denom > 0 else 100.0
            features["verified_attendance_percentage"] = round(att_rate, 2)
            eligible_records_count += 1
        else:
            features["verified_attendance_percentage"] = 100.0  # default neutral attendance

        provenance["attendance"] = {
            "source": "Phase 04 Attendance Ledger",
            "records_counted": len(attendance_records),
        }

        # ---------------------------------------------------------------------
        # 6. Target Leakage Assertion
        # ---------------------------------------------------------------------
        leakage_validator.validate_feature_vector(
            features,
            prohibited_targets=["final_exam_marks", "course_failure", "target_label", "semester_grade"]
        )

        # ---------------------------------------------------------------------
        # 7. Evidence Sufficiency Determination
        # ---------------------------------------------------------------------
        if eligible_records_count < 2:
            sufficiency = EvidenceSufficiencyLevel.INSUFFICIENT.value
        elif eligible_records_count < 4:
            sufficiency = EvidenceSufficiencyLevel.LIMITED.value
        elif len(assessment_scores) >= 3 and len(topic_results) >= 2:
            sufficiency = EvidenceSufficiencyLevel.STRONG.value
        else:
            sufficiency = EvidenceSufficiencyLevel.MODERATE.value

        snapshot = RiskFeatureSnapshot(
            institution_id=institution_id,
            student_id=student_id,
            subject_id=subject_id,
            target_id=target_id,
            observation_cutoff_date=cutoff_date,
            feature_vector_json=features,
            feature_provenance_json=provenance,
            evidence_sufficiency=sufficiency,
            eligible_records_count=eligible_records_count,
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        return snapshot


risk_feature_service = RiskFeatureEngineeringService()
