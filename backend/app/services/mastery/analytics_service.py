import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func

from app.models.academic_data import StudentAcademicProfile, StudentSubjectEnrollment
from app.models.syllabus import AcademicSubject, SyllabusTopic, SyllabusUnit, LearningOutcome, Competency
from app.models.mastery import (
    MasteryAnalysisJob,
    MasteryEvidenceRecord,
    TopicMasteryResult,
    LearningOutcomeAttainmentResult,
    LearningGapFinding,
)
from app.models.enums import (
    AnalysisJobStatus,
    EvidenceEligibilityStatus,
    MasteryStatus,
    AttainmentStatus,
    EvidenceSufficiencyLevel,
)
from app.schemas.mastery import (
    MasteryAnalyzeRequest,
    StudentMasteryProfileResponse,
    TopicMasteryDetailResponse,
    LearningOutcomeAttainmentDetailResponse,
    LearningGapFindingResponse,
    StudentPerformanceTrendResponse,
    PerformanceTrendPoint,
    CohortMasterySummaryResponse,
)
from app.services.mastery.eligibility_service import EvidenceEligibilityService
from app.services.mastery.calculation_service import TopicMasteryCalculationService
from app.services.mastery.outcome_service import LearningOutcomeAttainmentService
from app.services.mastery.gap_service import LearningGapAnalysisService
from app.core.logging import logger

SCIENTIFIC_DISCLAIMER = (
    "DISCLAIMER: Learning mastery metrics reflect observed, normalized performance across eligible "
    "assessment items. They represent evidence-backed indicators of topic familiarity and must NEVER "
    "be equated with a scientifically proven measure of total internal conceptual mastery or student intelligence."
)


class MasteryAnalyticsService:
    @staticmethod
    def execute_analysis_job(
        db: Session,
        institution_id: uuid.UUID,
        creator_id: Optional[uuid.UUID],
        request: MasteryAnalyzeRequest,
    ) -> MasteryAnalysisJob:
        """
        Executes a deterministic Learning Mastery analysis job for a subject and target student(s).
        Extracts evidence, enforces eligibility rules, calculates topic mastery, CLO attainment, and gaps.
        """
        now = datetime.now(timezone.utc)

        # 1. Create Analysis Job
        job = MasteryAnalysisJob(
            id=uuid.uuid4(),
            institution_id=institution_id,
            student_id=request.student_id,
            subject_id=request.subject_id,
            academic_year=request.academic_year,
            semester=request.semester,
            curriculum_version="2024.1",
            calculation_version=request.calculation_version,
            status=AnalysisJobStatus.RUNNING.value,
            started_at=now,
            created_by=creator_id,
        )
        db.add(job)
        db.flush()

        # 2. Identify target students
        if request.student_id:
            target_student_ids = [request.student_id]
        else:
            # All enrolled students in this subject
            enrollments = db.execute(
                select(StudentSubjectEnrollment.student_id).where(
                    StudentSubjectEnrollment.institution_id == institution_id,
                    StudentSubjectEnrollment.subject_id == request.subject_id,
                    StudentSubjectEnrollment.enrollment_status == "ACTIVE",
                )
            ).scalars().all()
            target_student_ids = list(set(enrollments))

        total_examined = 0
        total_eligible = 0
        total_excluded = 0

        # 3. Process each student
        for s_id in target_student_ids:
            # Evidence Extraction & Provenance
            evidence = EvidenceEligibilityService.extract_and_evaluate_evidence(
                db=db,
                institution_id=institution_id,
                analysis_job_id=job.id,
                student_id=s_id,
                subject_id=request.subject_id,
                include_practice=request.include_practice_tests,
            )
            total_examined += len(evidence)
            total_eligible += sum(1 for e in evidence if e.eligibility_status == EvidenceEligibilityStatus.ELIGIBLE.value)
            total_excluded += sum(1 for e in evidence if e.eligibility_status == EvidenceEligibilityStatus.EXCLUDED.value)

            db.add_all(evidence)
            db.flush()

            # Topic Mastery Calculation
            topic_results = TopicMasteryCalculationService.calculate_topic_mastery(
                db=db,
                institution_id=institution_id,
                analysis_job_id=job.id,
                student_id=s_id,
                subject_id=request.subject_id,
                evidence_records=evidence,
                calculation_version=request.calculation_version,
            )
            db.add_all(topic_results)
            db.flush()

            # Learning Outcome Attainment
            outcome_results = LearningOutcomeAttainmentService.calculate_outcome_attainment(
                db=db,
                institution_id=institution_id,
                analysis_job_id=job.id,
                student_id=s_id,
                subject_id=request.subject_id,
                evidence_records=evidence,
                calculation_version=request.calculation_version,
            )
            db.add_all(outcome_results)
            db.flush()

            # Learning Gap Discovery
            gap_findings = LearningGapAnalysisService.identify_learning_gaps(
                db=db,
                institution_id=institution_id,
                analysis_job_id=job.id,
                student_id=s_id,
                subject_id=request.subject_id,
                topic_results=topic_results,
                outcome_results=outcome_results,
            )
            db.add_all(gap_findings)
            db.flush()

        # 4. Finalize Job
        job.total_evidence_examined = total_examined
        job.eligible_evidence_count = total_eligible
        job.excluded_evidence_count = total_excluded
        job.status = AnalysisJobStatus.COMPLETED.value
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)

        logger.info(
            "Mastery analysis job %s completed for subject %s: %s students, %s evidence records.",
            job.id,
            request.subject_id,
            len(target_student_ids),
            total_examined,
        )
        return job

    @staticmethod
    def get_student_mastery_profile(
        db: Session,
        institution_id: uuid.UUID,
        student_id: uuid.UUID,
        subject_id: uuid.UUID,
    ) -> StudentMasteryProfileResponse:
        student = db.execute(
            select(StudentAcademicProfile).where(
                StudentAcademicProfile.id == student_id,
                StudentAcademicProfile.institution_id == institution_id,
            )
        ).scalar_one_or_none()

        subject = db.execute(
            select(AcademicSubject).where(
                AcademicSubject.id == subject_id,
                AcademicSubject.institution_id == institution_id,
            )
        ).scalar_one_or_none()

        if not student or not subject:
            raise ValueError("Student or subject not found.")

        # Latest Topic Results
        topic_results_rows = db.execute(
            select(TopicMasteryResult, SyllabusTopic, SyllabusUnit)
            .join(SyllabusTopic, TopicMasteryResult.topic_id == SyllabusTopic.id)
            .join(SyllabusUnit, SyllabusTopic.unit_id == SyllabusUnit.id)
            .where(
                TopicMasteryResult.institution_id == institution_id,
                TopicMasteryResult.student_id == student_id,
                TopicMasteryResult.subject_id == subject_id,
            )
            .order_by(TopicMasteryResult.calculated_at.desc(), SyllabusUnit.unit_number.asc(), SyllabusTopic.order_index.asc())
        ).all()

        # Deduplicate to latest result per topic
        seen_topics = set()
        topic_details: List[TopicMasteryDetailResponse] = []
        for tr, top, u in topic_results_rows:
            if top.id in seen_topics:
                continue
            seen_topics.add(top.id)

            explanation = (
                f"Based on {tr.eligible_question_count} verified question(s) across {tr.eligible_attempt_count} attempt(s). "
                f"Candidate achieved {tr.marks_obtained}/{tr.maximum_marks} marks. "
                f"Evidence sufficiency is rated as {tr.evidence_sufficiency}."
                if tr.mastery_percentage is not None
                else "No eligible assessment evidence available for this syllabus topic. The topic has not been assessed."
            )

            topic_details.append(
                TopicMasteryDetailResponse(
                    id=tr.id,
                    topic_id=top.id,
                    topic_name=top.topic_name,
                    unit_number=u.unit_number,
                    unit_title=u.title,
                    eligible_question_count=tr.eligible_question_count,
                    eligible_attempt_count=tr.eligible_attempt_count,
                    marks_obtained=tr.marks_obtained,
                    maximum_marks=tr.maximum_marks,
                    mastery_percentage=tr.mastery_percentage,
                    evidence_sufficiency=tr.evidence_sufficiency,
                    confidence_category=tr.confidence_category,
                    mastery_status=tr.mastery_status,
                    calculation_version=tr.calculation_version,
                    calculated_at=tr.calculated_at,
                    plain_explanation=explanation,
                )
            )

        # Latest Learning Outcome Attainments
        outcome_rows = db.execute(
            select(LearningOutcomeAttainmentResult, LearningOutcome)
            .join(LearningOutcome, LearningOutcomeAttainmentResult.learning_outcome_id == LearningOutcome.id)
            .where(
                LearningOutcomeAttainmentResult.institution_id == institution_id,
                LearningOutcomeAttainmentResult.student_id == student_id,
                LearningOutcomeAttainmentResult.subject_id == subject_id,
            )
            .order_by(LearningOutcomeAttainmentResult.calculated_at.desc())
        ).all()

        seen_outcomes = set()
        outcome_details: List[LearningOutcomeAttainmentDetailResponse] = []
        for o_res, lo in outcome_rows:
            if lo.id in seen_outcomes:
                continue
            seen_outcomes.add(lo.id)
            outcome_details.append(
                LearningOutcomeAttainmentDetailResponse(
                    id=o_res.id,
                    learning_outcome_id=lo.id,
                    outcome_code=lo.outcome_code,
                    description=lo.description,
                    bloom_level=lo.bloom_level,
                    eligible_question_count=o_res.eligible_question_count,
                    mapped_marks=o_res.mapped_marks,
                    marks_obtained=o_res.marks_obtained,
                    attainment_percentage=o_res.attainment_percentage,
                    evidence_sufficiency=o_res.evidence_sufficiency,
                    confidence_category=o_res.confidence_category,
                    attainment_status=o_res.attainment_status,
                    calculation_version=o_res.calculation_version,
                    calculated_at=o_res.calculated_at,
                )
            )

        # Active Learning Gaps
        gap_rows = db.execute(
            select(LearningGapFinding, SyllabusTopic, LearningOutcome)
            .outerjoin(SyllabusTopic, LearningGapFinding.topic_id == SyllabusTopic.id)
            .outerjoin(LearningOutcome, LearningGapFinding.learning_outcome_id == LearningOutcome.id)
            .where(
                LearningGapFinding.institution_id == institution_id,
                LearningGapFinding.student_id == student_id,
                LearningGapFinding.subject_id == subject_id,
                LearningGapFinding.status == "OPEN",
            )
        ).all()

        gaps: List[LearningGapFindingResponse] = []
        for g, top, lo in gap_rows:
            gaps.append(
                LearningGapFindingResponse(
                    id=g.id,
                    subject_id=g.subject_id,
                    topic_id=g.topic_id,
                    topic_name=top.topic_name if top else None,
                    learning_outcome_id=g.learning_outcome_id,
                    outcome_code=lo.outcome_code if lo else None,
                    finding_type=g.finding_type,
                    severity=g.severity,
                    evidence_summary=g.evidence_summary,
                    supporting_evidence_refs=g.supporting_evidence_refs or {},
                    recommended_review_action=g.recommended_review_action,
                    status=g.status,
                    created_at=g.created_at,
                )
            )

        # Cognitive Breakdown (Bloom's Revised Taxonomy)
        cognitive_breakdown: Dict[str, Dict[str, Any]] = {
            level: {"questions_assessed": 0, "marks_obtained": 0.0, "maximum_marks": 0.0, "percentage": None}
            for level in ["REMEMBER", "UNDERSTAND", "APPLY", "ANALYZE", "EVALUATE", "CREATE"]
        }
        eligible_evidence = db.execute(
            select(MasteryEvidenceRecord).where(
                MasteryEvidenceRecord.institution_id == institution_id,
                MasteryEvidenceRecord.student_id == student_id,
                MasteryEvidenceRecord.subject_id == subject_id,
                MasteryEvidenceRecord.eligibility_status == EvidenceEligibilityStatus.ELIGIBLE.value,
            )
        ).scalars().all()

        for ev in eligible_evidence:
            if ev.bloom_level and ev.bloom_level in cognitive_breakdown:
                cognitive_breakdown[ev.bloom_level]["questions_assessed"] += 1
                cognitive_breakdown[ev.bloom_level]["marks_obtained"] += ev.marks_obtained
                cognitive_breakdown[ev.bloom_level]["maximum_marks"] += ev.maximum_marks

        for k, v in cognitive_breakdown.items():
            if v["maximum_marks"] > 0:
                v["percentage"] = round((v["marks_obtained"] / v["maximum_marks"]) * 100.0, 1)

        # Competency Breakdown
        competency_breakdown: Dict[str, Dict[str, Any]] = {
            cat: {"items": 0, "marks_obtained": 0.0, "maximum_marks": 0.0, "percentage": None}
            for cat in ["THEORETICAL", "PROGRAMMING", "TOOLS_TECHNOLOGIES", "ANALYTICAL", "PRACTICAL"]
        }

        # Sufficiency counts
        sufficiency_summary = {
            EvidenceSufficiencyLevel.STRONG.value: sum(1 for t in topic_details if t.evidence_sufficiency == EvidenceSufficiencyLevel.STRONG.value),
            EvidenceSufficiencyLevel.MODERATE.value: sum(1 for t in topic_details if t.evidence_sufficiency == EvidenceSufficiencyLevel.MODERATE.value),
            EvidenceSufficiencyLevel.LIMITED.value: sum(1 for t in topic_details if t.evidence_sufficiency == EvidenceSufficiencyLevel.LIMITED.value),
            EvidenceSufficiencyLevel.INSUFFICIENT.value: sum(1 for t in topic_details if t.evidence_sufficiency == EvidenceSufficiencyLevel.INSUFFICIENT.value),
        }

        # Calculate Overall Subject Mastery
        assessed_topics = [t for t in topic_details if t.mastery_percentage is not None]
        overall_mastery = (
            round(sum(t.mastery_percentage for t in assessed_topics) / len(assessed_topics), 1)
            if assessed_topics
            else None
        )

        return StudentMasteryProfileResponse(
            student_id=student.id,
            student_name=f"{student.first_name} {student.last_name}",
            enrollment_number=student.enrollment_number,
            subject_id=subject.id,
            subject_name=subject.name,
            subject_code=subject.code,
            overall_mastery_percentage=overall_mastery,
            total_topics_analyzed=len(topic_details),
            mastered_topics_count=sum(1 for t in topic_details if t.mastery_status == MasteryStatus.MASTERED.value),
            progressing_topics_count=sum(1 for t in topic_details if t.mastery_status == MasteryStatus.PROGRESSING.value),
            needs_attention_topics_count=sum(1 for t in topic_details if t.mastery_status == MasteryStatus.NEEDS_ATTENTION.value),
            insufficient_evidence_topics_count=sum(1 for t in topic_details if t.mastery_status == MasteryStatus.INSUFFICIENT_EVIDENCE.value),
            topic_results=topic_details,
            outcome_results=outcome_details,
            learning_gaps=gaps,
            cognitive_breakdown=cognitive_breakdown,
            competency_breakdown=competency_breakdown,
            evidence_sufficiency_summary=sufficiency_summary,
            scientific_disclaimer=SCIENTIFIC_DISCLAIMER,
        )

    @staticmethod
    def get_performance_trends(
        db: Session,
        institution_id: uuid.UUID,
        student_id: uuid.UUID,
        subject_id: uuid.UUID,
    ) -> StudentPerformanceTrendResponse:
        """
        Computes evidence-backed longitudinal performance points across assessments.
        Preserves timestamps and distinguishes assessment difficulties.
        """
        evidence_rows = db.execute(
            select(MasteryEvidenceRecord, SyllabusTopic)
            .outerjoin(SyllabusTopic, MasteryEvidenceRecord.topic_id == SyllabusTopic.id)
            .where(
                MasteryEvidenceRecord.institution_id == institution_id,
                MasteryEvidenceRecord.student_id == student_id,
                MasteryEvidenceRecord.subject_id == subject_id,
                MasteryEvidenceRecord.eligibility_status == EvidenceEligibilityStatus.ELIGIBLE.value,
            )
            .order_by(MasteryEvidenceRecord.evidence_timestamp.asc())
        ).all()

        points: List[PerformanceTrendPoint] = []
        for ev, top in evidence_rows:
            pct = round((ev.marks_obtained / ev.maximum_marks * 100.0), 1) if ev.maximum_marks > 0 else 0.0
            points.append(
                PerformanceTrendPoint(
                    timestamp=ev.evidence_timestamp,
                    assessment_name="Continuous Evaluation Item",
                    topic_id=ev.topic_id,
                    topic_name=top.topic_name if top else None,
                    percentage=pct,
                    evidence_type=ev.source_entity_type,
                    is_official=not ev.is_practice_assessment,
                )
            )

        # Determine trend direction if sufficient points
        if len(points) < 3:
            trend_dir = "INSUFFICIENT_OBSERVATIONS"
        else:
            first_half = points[: len(points) // 2]
            second_half = points[len(points) // 2 :]
            avg1 = sum(p.percentage for p in first_half) / len(first_half)
            avg2 = sum(p.percentage for p in second_half) / len(second_half)
            if avg2 - avg1 > 5.0:
                trend_dir = "IMPROVING"
            elif avg1 - avg2 > 5.0:
                trend_dir = "DECLINING"
            else:
                trend_dir = "STABLE"

        return StudentPerformanceTrendResponse(
            student_id=student_id,
            subject_id=subject_id,
            timeline=points,
            trend_direction=trend_dir,
            observation_count=len(points),
            scientific_disclaimer=SCIENTIFIC_DISCLAIMER,
        )

    @staticmethod
    def get_cohort_mastery_summary(
        db: Session,
        institution_id: uuid.UUID,
        subject_id: uuid.UUID,
    ) -> CohortMasterySummaryResponse:
        subject = db.execute(
            select(AcademicSubject).where(
                AcademicSubject.id == subject_id,
                AcademicSubject.institution_id == institution_id,
            )
        ).scalar_one_or_none()
        if not subject:
            raise ValueError("Subject not found.")

        # Total enrolled
        total_enrolled = db.execute(
            select(func.count(StudentSubjectEnrollment.id)).where(
                StudentSubjectEnrollment.institution_id == institution_id,
                StudentSubjectEnrollment.subject_id == subject_id,
                StudentSubjectEnrollment.enrollment_status == "ACTIVE",
            )
        ).scalar() or 0

        # Unique students with mastery results
        analyzed_students = db.execute(
            select(func.count(func.distinct(TopicMasteryResult.student_id))).where(
                TopicMasteryResult.institution_id == institution_id,
                TopicMasteryResult.subject_id == subject_id,
            )
        ).scalar() or 0

        # Topic aggregates
        topics = db.execute(
            select(SyllabusTopic)
            .join(SyllabusUnit, SyllabusTopic.unit_id == SyllabusUnit.id)
            .where(SyllabusUnit.subject_id == subject_id)
            .order_by(SyllabusUnit.unit_number.asc(), SyllabusTopic.order_index.asc())
        ).scalars().all()

        topic_aggs = []
        for t in topics:
            scores = db.execute(
                select(TopicMasteryResult.mastery_percentage).where(
                    TopicMasteryResult.institution_id == institution_id,
                    TopicMasteryResult.subject_id == subject_id,
                    TopicMasteryResult.topic_id == t.id,
                    TopicMasteryResult.mastery_percentage != None,
                )
            ).scalars().all()

            avg_score = round(sum(scores) / len(scores), 1) if scores else None
            topic_aggs.append({
                "topic_id": str(t.id),
                "topic_name": t.topic_name,
                "assessed_candidates_count": len(scores),
                "average_mastery_percentage": avg_score,
                "has_sufficient_evidence": len(scores) >= 1,
            })

        # Coverage percentage: topics with at least 1 assessed student / total topics
        topics_covered = sum(1 for ta in topic_aggs if ta["has_sufficient_evidence"])
        coverage_pct = round((topics_covered / len(topics) * 100.0), 1) if topics else 0.0

        return CohortMasterySummaryResponse(
            subject_id=subject.id,
            subject_name=subject.name,
            subject_code=subject.code,
            total_students_enrolled=total_enrolled,
            students_analyzed=analyzed_students,
            topic_aggregates=topic_aggs,
            outcome_aggregates=[],
            curriculum_coverage_percentage=coverage_pct,
            scientific_disclaimer=SCIENTIFIC_DISCLAIMER,
        )
