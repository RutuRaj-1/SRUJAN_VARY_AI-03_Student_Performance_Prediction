import uuid
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_

from app.models.academic_data import (
    StudentAcademicProfile,
    StudentSubjectEnrollment,
    AcademicAssessment,
    StudentAssessmentRecord,
)
from app.models.assessment import (
    AssessmentAttempt,
    AssessmentResponse,
    AssessmentQuestion,
    AssessmentQuestionMapping,
)
from app.models.syllabus import AcademicSubject, SyllabusTopic, LearningOutcome
from app.models.enums import (
    AttemptStatus,
    ResponseEvaluationStatus,
    RecordVerificationStatus,
    AssessmentResultStatus,
    AssessmentType,
    EvidenceEligibilityStatus,
    EvidenceExclusionReason,
)
from app.models.mastery import MasteryEvidenceRecord
from app.core.logging import logger


class EvidenceEligibilityService:
    """
    Deterministic Evidence Eligibility & Provenance Engine.
    Filters raw candidate records into ELIGIBLE vs EXCLUDED evidence with full provenance tracking.
    Enforces strict anti-double-counting and excludes non-evaluative artifacts.
    """

    @staticmethod
    def extract_and_evaluate_evidence(
        db: Session,
        institution_id: uuid.UUID,
        analysis_job_id: uuid.UUID,
        student_id: uuid.UUID,
        subject_id: uuid.UUID,
        include_practice: bool = False,
    ) -> List[MasteryEvidenceRecord]:
        evidence_records: List[MasteryEvidenceRecord] = []

        # ---------------------------------------------------------------------
        # 1. Inspect Phase 05 Online Assessment Responses
        # ---------------------------------------------------------------------
        # Query all responses for student attempts belonging to this subject
        stmt = (
            select(AssessmentResponse, AssessmentAttempt, AcademicAssessment, AssessmentQuestion)
            .join(AssessmentAttempt, AssessmentResponse.attempt_id == AssessmentAttempt.id)
            .join(AcademicAssessment, AssessmentAttempt.assessment_id == AcademicAssessment.id)
            .join(AssessmentQuestion, AssessmentResponse.question_id == AssessmentQuestion.id)
            .where(
                AssessmentAttempt.institution_id == institution_id,
                AssessmentAttempt.student_id == student_id,
                AcademicAssessment.subject_id == subject_id,
            )
        )
        response_rows = db.execute(stmt).all()

        for resp, att, asmt, q in response_rows:
            is_practice = asmt.assessment_type == AssessmentType.PRACTICE_TEST.value
            is_eligible = True
            exclusion_reason: Optional[str] = None

            # Exclusion Rule 1: Practice Test handling
            if is_practice and not include_practice:
                is_eligible = False
                exclusion_reason = "Practice assessments excluded from authoritative analysis by configuration."

            # Exclusion Rule 2: Attempt Status must be SUBMITTED or EVALUATED
            elif att.attempt_status not in [AttemptStatus.SUBMITTED.value, AttemptStatus.EVALUATED.value]:
                is_eligible = False
                exclusion_reason = EvidenceExclusionReason.UNSUBMITTED_ATTEMPT.value

            # Exclusion Rule 3: Evaluation Status
            elif resp.evaluation_status in [ResponseEvaluationStatus.PENDING.value, ResponseEvaluationStatus.FACULTY_REVIEW_REQUIRED.value]:
                is_eligible = False
                exclusion_reason = EvidenceExclusionReason.UNVERIFIED_EVALUATION.value

            # Exclusion Rule 4: Maximum marks must be > 0
            elif (resp.marks_awarded is None) or (q.default_marks <= 0):
                is_eligible = False
                exclusion_reason = EvidenceExclusionReason.MISSING_MARKS.value

            # Mapping status check
            mapping_status = "APPROVED_MAPPING" if q.topic_id else "UNMAPPED"
            if not q.topic_id and not q.learning_outcome_id:
                is_eligible = False
                exclusion_reason = EvidenceExclusionReason.UNAPPROVED_CURRICULUM_MAPPING.value

            record = MasteryEvidenceRecord(
                id=uuid.uuid4(),
                institution_id=institution_id,
                analysis_job_id=analysis_job_id,
                student_id=student_id,
                subject_id=subject_id,
                topic_id=q.topic_id,
                learning_outcome_id=q.learning_outcome_id,
                source_entity_type="ASSESSMENT_RESPONSE",
                source_entity_id=resp.id,
                assessment_id=asmt.id,
                question_id=q.id,
                attempt_id=att.id,
                marks_obtained=float(resp.marks_awarded or 0.0),
                maximum_marks=float(q.default_marks),
                eligibility_status=(
                    EvidenceEligibilityStatus.ELIGIBLE.value
                    if is_eligible
                    else EvidenceEligibilityStatus.EXCLUDED.value
                ),
                exclusion_reason=exclusion_reason,
                mapping_status=mapping_status,
                evaluation_status=resp.evaluation_status,
                verification_status="AUTO_EVALUATED" if resp.is_auto_evaluated else "FACULTY_VERIFIED",
                bloom_level=q.bloom_level,
                is_practice_assessment=is_practice,
                evidence_timestamp=resp.saved_at or att.submitted_at or att.started_at,
            )
            evidence_records.append(record)

        # ---------------------------------------------------------------------
        # 2. Inspect Phase 04 Official Gradebook Records (with Double-Counting Prevention)
        # ---------------------------------------------------------------------
        # Identify assessments that already contributed online item-level responses above
        online_assessment_ids = {rec.assessment_id for rec in evidence_records if rec.assessment_id}

        gradebook_stmt = (
            select(StudentAssessmentRecord, AcademicAssessment)
            .join(AcademicAssessment, StudentAssessmentRecord.assessment_id == AcademicAssessment.id)
            .where(
                StudentAssessmentRecord.institution_id == institution_id,
                StudentAssessmentRecord.student_id == student_id,
                AcademicAssessment.subject_id == subject_id,
            )
        )
        gradebook_rows = db.execute(gradebook_stmt).all()

        for rec, asmt in gradebook_rows:
            # Check Double-Counting Rule:
            # If this assessment already contributed fine-grained question responses from Phase 05,
            # exclude this coarse aggregate gradebook record to prevent duplicate weighting!
            if asmt.id in online_assessment_ids:
                excluded_record = MasteryEvidenceRecord(
                    id=uuid.uuid4(),
                    institution_id=institution_id,
                    analysis_job_id=analysis_job_id,
                    student_id=student_id,
                    subject_id=subject_id,
                    topic_id=None,
                    learning_outcome_id=None,
                    source_entity_type="OFFICIAL_GRADEBOOK_RECORD",
                    source_entity_id=rec.id,
                    assessment_id=asmt.id,
                    question_id=None,
                    attempt_id=None,
                    marks_obtained=float(rec.marks_obtained or 0.0),
                    maximum_marks=float(rec.maximum_marks_snapshot),
                    eligibility_status=EvidenceEligibilityStatus.EXCLUDED.value,
                    exclusion_reason=EvidenceExclusionReason.DUPLICATE_GRADEBOOK_RECORD.value,
                    mapping_status="COARSE_ASSESSMENT_LEVEL",
                    evaluation_status="EVALUATED",
                    verification_status=rec.verification_status,
                    bloom_level=None,
                    is_practice_assessment=False,
                    evidence_timestamp=rec.recorded_at or datetime.now(timezone.utc),
                )
                evidence_records.append(excluded_record)
                continue

            # Check Non-Numeric State Rule (ABSENT, NOT_SUBMITTED, EXEMPTED)
            if rec.result_status in [
                AssessmentResultStatus.ABSENT.value,
                AssessmentResultStatus.NOT_SUBMITTED.value,
                AssessmentResultStatus.EXEMPTED.value,
            ] or rec.marks_obtained is None:
                excluded_record = MasteryEvidenceRecord(
                    id=uuid.uuid4(),
                    institution_id=institution_id,
                    analysis_job_id=analysis_job_id,
                    student_id=student_id,
                    subject_id=subject_id,
                    topic_id=None,
                    learning_outcome_id=None,
                    source_entity_type="OFFICIAL_GRADEBOOK_RECORD",
                    source_entity_id=rec.id,
                    assessment_id=asmt.id,
                    question_id=None,
                    attempt_id=None,
                    marks_obtained=0.0,
                    maximum_marks=float(rec.maximum_marks_snapshot),
                    eligibility_status=EvidenceEligibilityStatus.EXCLUDED.value,
                    exclusion_reason=EvidenceExclusionReason.EXEMPTED_RECORD.value,
                    mapping_status="COARSE_ASSESSMENT_LEVEL",
                    evaluation_status=rec.result_status,
                    verification_status=rec.verification_status,
                    bloom_level=None,
                    is_practice_assessment=False,
                    evidence_timestamp=rec.recorded_at or datetime.now(timezone.utc),
                )
                evidence_records.append(excluded_record)
                continue

            # For coarse gradebook records not linked to individual topics:
            # We record them as coarse evidence (excluded from topic-level calculation due to unmapped topic)
            coarse_record = MasteryEvidenceRecord(
                id=uuid.uuid4(),
                institution_id=institution_id,
                analysis_job_id=analysis_job_id,
                student_id=student_id,
                subject_id=subject_id,
                topic_id=None,
                learning_outcome_id=None,
                source_entity_type="OFFICIAL_GRADEBOOK_RECORD",
                source_entity_id=rec.id,
                assessment_id=asmt.id,
                question_id=None,
                attempt_id=None,
                marks_obtained=float(rec.marks_obtained),
                maximum_marks=float(rec.maximum_marks_snapshot),
                eligibility_status=EvidenceEligibilityStatus.EXCLUDED.value,
                exclusion_reason=EvidenceExclusionReason.UNAPPROVED_CURRICULUM_MAPPING.value,
                mapping_status="COARSE_ASSESSMENT_LEVEL",
                evaluation_status=rec.result_status,
                verification_status=rec.verification_status,
                bloom_level=None,
                is_practice_assessment=False,
                evidence_timestamp=rec.recorded_at or datetime.now(timezone.utc),
            )
            evidence_records.append(coarse_record)

        return evidence_records
