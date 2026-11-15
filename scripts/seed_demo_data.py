"""
MASTERY — Synthetic Demonstration Cohort Seed Script.
Phase 11: Final Platform Hardening & Hackathon Readiness.

Populates a comprehensive, realistic, and explicitly labeled synthetic CSE cohort
illustrating all 10 academic and career scenarios required for hackathon demonstration.

Scenarios Covered:
 1. Strong academic performance & sufficient evidence (Aarav Sharma).
 2. Good marks but weak topic evidence / grade inflation (Riya Sen).
 3. Genuine academic difficulty with verified evidence (Kabir Mehta).
 4. Insufficient evidence / transferred student with formative diagnostic (Neha Patel).
 5. Asymmetric Bloom taxonomy attainment profile (Aditya Joshi).
 6. Active faculty-reviewed academic intervention plan (Sneha Rao).
 7. Divergent career role readiness alignment (Vikram Choudhury).
 8. Practical project awaiting faculty verification (Pooja Hegde).
 9. Verified practical open-source project portfolio (Tanmay Deshmukh).
10. Categorized industry skill gaps with developmental roadmap (Ananya Dixit).
"""

import os
import sys
import uuid
from datetime import datetime, timezone, timedelta

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath("backend"))

from sqlalchemy import select
from app.db.session import get_session_local
from app.models.enums import (
    UserRole,
    AccountStatus,
    BloomTaxonomyLevel,
    AssessmentType,
    AttendanceStatus,
    RecordVerificationStatus,
    RiskClassification,
    InterventionPlanStatus,
    CareerAlignmentStatus,
    ProjectVerificationStatus,
    IndustryImportance,
    CompetencyCategory,
)
from app.models.institution import Institution, InstitutionMembership
from app.models.profile import Profile
from app.models.syllabus import (
    AcademicProgram,
    AcademicSubject,
    SyllabusDocument,
    SyllabusUnit,
    SyllabusTopic,
    LearningOutcome,
    IndustryRoleProfile,
    IndustryCompetencyRequirement,
)
from app.models.academic_data import (
    StudentAcademicProfile,
    StudentSubjectEnrollment,
    AcademicAssessment,
    StudentAssessmentRecord,
    StudentAttendanceRecord,
)
from app.models.mastery import (
    MasteryAnalysisJob,
    TopicMasteryResult,
    LearningOutcomeAttainmentResult,
    LearningGapFinding,
)
from app.models.risk import (
    AcademicRiskTarget,
    AcademicRiskPrediction,
    AcademicRiskPredictionExplanation,
)
from app.models.interventions import (
    AcademicInterventionPlan,
    AcademicInterventionAction,
    InterventionProgressEvent,
)
from app.models.career import (
    StudentProjectEvidence,
    CareerReadinessAnalysis,
    CareerSkillGapFinding,
    CareerDevelopmentRecommendation,
)


def seed_demo_data():
    session_factory = get_session_local()
    if not session_factory:
        print("[ERROR] Database not configured. Cannot seed demonstration cohort.")
        return

    session = session_factory()
    try:
        now = datetime.now(timezone.utc)
        print("[DEMO SEED] Starting synthetic hackathon demonstration data seeding...")

        # ---------------------------------------------------------------------
        # 1. Demonstration Institution
        # ---------------------------------------------------------------------
        inst_stmt = select(Institution).where(Institution.institution_code == "SIAT-2026")
        inst = session.execute(inst_stmt).scalars().first()
        if not inst:
            inst = Institution(
                id=uuid.uuid4(),
                name="Srujan Institute of Advanced Technology (SIAT)",
                institution_code="SIAT-2026",
                institution_type="Autonomous Engineering Institute",
                city="Pune",
                state="Maharashtra",
                country="India",
                is_active=True,
            )
            session.add(inst)
            session.flush()
            print(f"[DEMO SEED] Created Demo Institution: {inst.name}")

        # ---------------------------------------------------------------------
        # 2. Demonstration Program
        # ---------------------------------------------------------------------
        prog_stmt = select(AcademicProgram).where(
            AcademicProgram.institution_id == inst.id,
            AcademicProgram.code == "CSE-SIAT"
        )
        prog = session.execute(prog_stmt).scalars().first()
        if not prog:
            prog = AcademicProgram(
                id=uuid.uuid4(),
                institution_id=inst.id,
                name="B.Tech Computer Science and Engineering",
                code="CSE-SIAT",
                degree_type="UNDERGRADUATE",
                duration_years=4,
                is_active=True,
            )
            session.add(prog)
            session.flush()
            print(f"[DEMO SEED] Created Demo Program: {prog.name}")

        # ---------------------------------------------------------------------
        # 3. Core Academic Subjects
        # ---------------------------------------------------------------------
        subjects_meta = [
            ("CS-301", "Advanced Data Structures & Algorithms", 5, 4),
            ("CS-302", "Database Management Systems", 5, 4),
            ("CS-303", "Operating Systems & Concurrency", 5, 4),
        ]
        created_subjects = {}
        for code, name, sem, creds in subjects_meta:
            subj_stmt = select(AcademicSubject).where(
                AcademicSubject.institution_id == inst.id,
                AcademicSubject.code == code
            )
            subj = session.execute(subj_stmt).scalars().first()
            if not subj:
                subj = AcademicSubject(
                    id=uuid.uuid4(),
                    institution_id=inst.id,
                    program_id=prog.id,
                    name=name,
                    code=code,
                    semester=sem,
                    credits=creds,
                    academic_year="2024-2025",
                )
                session.add(subj)
                session.flush()
            created_subjects[code] = subj

        primary_subj = created_subjects["CS-301"]

        # ---------------------------------------------------------------------
        # 4. Institutional Staff Profiles
        # ---------------------------------------------------------------------
        staff_data = [
            ("faculty@siat.edu", "Dr. Ananya Iyer", UserRole.FACULTY),
            ("placement@siat.edu", "Prof. Vikram Malhotra", UserRole.PLACEMENT_OFFICER),
            ("admin@siat.edu", "Dean Rajesh Kulkarni", UserRole.INSTITUTION_ADMIN),
        ]
        staff_profiles = {}
        for email, full_name, role in staff_data:
            prof_stmt = select(Profile).where(Profile.email == email)
            prof = session.execute(prof_stmt).scalars().first()
            if not prof:
                prof = Profile(
                    id=uuid.uuid4(),
                    email=email,
                    full_name=full_name,
                    role=role.value,
                    account_status=AccountStatus.ACTIVE.value,
                    institution_id=inst.id,
                )
                session.add(prof)
                session.flush()
            staff_profiles[role] = prof

        # ---------------------------------------------------------------------
        # 5. Syllabus Document, Units, Topics & CLOs for CS-301
        # ---------------------------------------------------------------------
        doc_stmt = select(SyllabusDocument).where(SyllabusDocument.subject_id == primary_subj.id)
        doc = session.execute(doc_stmt).scalars().first()
        if not doc:
            doc = SyllabusDocument(
                id=uuid.uuid4(),
                institution_id=inst.id,
                subject_id=primary_subj.id,
                uploaded_by=staff_profiles[UserRole.FACULTY].id,
                file_name="CS301_ADSA_Syllabus.pdf",
                file_size_bytes=245800,
                mime_type="application/pdf",
                storage_path="syllabi/CS301_ADSA.pdf",
                status="APPROVED",
            )
            session.add(doc)
            session.flush()

        # Units and Topics
        units_spec = [
            ("Unit 1: Tree Architectures", 1, [
                "Binary Search Trees & Balancing",
                "AVL Trees & Red-Black Rotations",
                "B-Trees & Multi-way Storage"
            ]),
            ("Unit 2: Graph Theory & Networks", 2, [
                "Graph Representation & Traversal (BFS/DFS)",
                "Minimum Spanning Trees (Kruskal/Prim)",
                "Shortest Path Algorithms (Dijkstra/Bellman-Ford)"
            ]),
            ("Unit 3: Algorithmic Paradigms", 3, [
                "Divide and Conquer Strategy",
                "Greedy Choice Principles",
                "Dynamic Programming Foundations"
            ]),
        ]
        demo_topics = []
        for u_title, u_num, topic_names in units_spec:
            u_stmt = select(SyllabusUnit).where(
                SyllabusUnit.subject_id == primary_subj.id,
                SyllabusUnit.unit_number == u_num
            )
            unit_obj = session.execute(u_stmt).scalars().first()
            if not unit_obj:
                unit_obj = SyllabusUnit(
                    id=uuid.uuid4(),
                    document_id=doc.id,
                    subject_id=primary_subj.id,
                    unit_number=u_num,
                    title=u_title,
                    estimated_hours=15,
                )
                session.add(unit_obj)
                session.flush()

            for idx, t_name in enumerate(topic_names, 1):
                t_stmt = select(SyllabusTopic).where(
                    SyllabusTopic.unit_id == unit_obj.id,
                    SyllabusTopic.topic_name == t_name
                )
                top = session.execute(t_stmt).scalars().first()
                if not top:
                    top = SyllabusTopic(
                        id=uuid.uuid4(),
                        unit_id=unit_obj.id,
                        topic_name=t_name,
                        order_index=idx,
                    )
                    session.add(top)
                    session.flush()
                demo_topics.append(top)

        # ---------------------------------------------------------------------
        # 6. Reference Industry Role Profile
        # ---------------------------------------------------------------------
        role_stmt = select(IndustryRoleProfile).where(
            IndustryRoleProfile.role_title == "Software Development Engineer - Backend"
        )
        backend_role = session.execute(role_stmt).scalars().first()
        if not backend_role:
            backend_role = IndustryRoleProfile(
                id=uuid.uuid4(),
                institution_id=inst.id,
                role_title="Software Development Engineer - Backend",
                role_family="Software Development",
                description="Engineers scalable microservices, backend data pipelines, and distributed APIs.",
                experience_tier="Entry-Level / Graduate",
                is_active=True,
            )
            session.add(backend_role)
            session.flush()

        # Risk Target
        target_stmt = select(AcademicRiskTarget).where(
            AcademicRiskTarget.institution_id == inst.id,
            AcademicRiskTarget.target_code == "SIAT-CS301-FAIL"
        )
        risk_target = session.execute(target_stmt).scalars().first()
        if not risk_target:
            risk_target = AcademicRiskTarget(
                id=uuid.uuid4(),
                institution_id=inst.id,
                subject_id=primary_subj.id,
                target_code="SIAT-CS301-FAIL",
                target_name="End-Semester Exam Difficulty",
                outcome_definition="Scoring below 40.0% in final end-semester examination",
                positive_label_definition="Score < 40%",
                negative_label_definition="Score >= 40%",
                passing_threshold_percentage=40.0,
                status="ACTIVE",
            )
            session.add(risk_target)
            session.flush()

        # Mastery Analysis Job
        job_stmt = select(MasteryAnalysisJob).where(
            MasteryAnalysisJob.subject_id == primary_subj.id,
            MasteryAnalysisJob.status == "COMPLETED"
        )
        mastery_job = session.execute(job_stmt).scalars().first()
        if not mastery_job:
            mastery_job = MasteryAnalysisJob(
                id=uuid.uuid4(),
                institution_id=inst.id,
                subject_id=primary_subj.id,
                academic_year="2024-2025",
                semester=5,
                status="COMPLETED",
            )
            session.add(mastery_job)
            session.flush()

        # ---------------------------------------------------------------------
        # 7. 10 Comprehensive Synthetic Demonstration Personas
        # ---------------------------------------------------------------------
        demo_students_spec = [
            {
                "num": "001",
                "first": "Aarav",
                "last": "Sharma",
                "email": "aarav.sharma@siat.edu",
                "scenario": "Scenario 1: Strong Academic Performance & Sufficient Evidence",
                "attendance": 94.0,
                "exam_score": 46.0,
                "max_score": 50.0,
                "mastery_scores": [92.0, 88.0, 85.0, 90.0, 86.0],
                "risk_class": "LOW",
                "risk_prob": 0.08,
                "adverse": [],
                "protective": ["Consistently high attendance (94%)", "Demonstrated mastery on 5 core algorithmic topics"],
                "has_intervention": False,
                "project_title": "High-Throughput Concurrent Cache in Go",
                "project_status": "VERIFIED",
                "role_coverage_core": 90.0,
                "role_coverage_prac": 95.0,
                "alignment": "STRONG_EVIDENCE_ALIGNMENT",
            },
            {
                "num": "002",
                "first": "Riya",
                "last": "Sen",
                "email": "riya.sen@siat.edu",
                "scenario": "Scenario 2: Good Marks but Weak Topic-Level Evidence (Grade Inflation / Evidence Gap)",
                "attendance": 88.0,
                "exam_score": 44.0,
                "max_score": 50.0,
                "mastery_scores": [88.0], # Only 1 topic assessed; others unassessed
                "risk_class": "MODERATE",
                "risk_prob": 0.42,
                "adverse": ["High overall marks but unassessed critical topics (B-Trees, Shortest Path)"],
                "protective": ["High mid-term score (88%) on basic BST"],
                "has_intervention": False,
                "project_title": "Simple Todo App",
                "project_status": "PENDING_REVIEW",
                "role_coverage_core": 60.0,
                "role_coverage_prac": 40.0,
                "alignment": "PARTIAL_EVIDENCE_ALIGNMENT",
            },
            {
                "num": "003",
                "first": "Kabir",
                "last": "Mehta",
                "email": "kabir.mehta@siat.edu",
                "scenario": "Scenario 3: Genuine Academic Difficulty with Verified Evidence",
                "attendance": 62.0,
                "exam_score": 19.0,
                "max_score": 50.0,
                "mastery_scores": [34.0, 28.0, 38.0],
                "risk_class": "HIGH",
                "risk_prob": 0.84,
                "adverse": ["Low attendance (62%)", "Low mid-term assessment marks (38%)", "Persistent deficit in Graph Traversal"],
                "protective": ["Attended 2 tutorial sessions"],
                "has_intervention": True,
                "intervention_title": "Graph Traversal & MST Remedial Program",
                "project_title": None,
                "project_status": None,
                "role_coverage_core": 30.0,
                "role_coverage_prac": 20.0,
                "alignment": "LIMITED_EVIDENCE_ALIGNMENT",
            },
            {
                "num": "004",
                "first": "Neha",
                "last": "Patel",
                "email": "neha.patel@siat.edu",
                "scenario": "Scenario 4: Insufficient Evidence / Mid-Semester Transfer (Formative Diagnostic)",
                "attendance": 78.0,
                "exam_score": None, # Exempted / transferred
                "max_score": 50.0,
                "mastery_scores": [], # Unassessed
                "risk_class": "INSUFFICIENT_EVIDENCE",
                "risk_prob": 0.25,
                "adverse": ["Missing formal mid-term evaluation records"],
                "protective": ["No negative attendance signals (78%)"],
                "has_intervention": True,
                "intervention_title": "Formative Diagnostic Assessment for Lateral Transfer",
                "project_title": "Previous Institution Data Structure Lab Tasks",
                "project_status": "PENDING_REVIEW",
                "role_coverage_core": 20.0,
                "role_coverage_prac": 30.0,
                "alignment": "INSUFFICIENT_EVIDENCE",
            },
            {
                "num": "005",
                "first": "Aditya",
                "last": "Joshi",
                "email": "aditya.joshi@siat.edu",
                "scenario": "Scenario 5: Asymmetric Bloom Taxonomy Attainment (High Remember, Low Analyze)",
                "attendance": 84.0,
                "exam_score": 36.0,
                "max_score": 50.0,
                "mastery_scores": [90.0, 42.0], # 90 on basic definitions, 42 on optimization
                "risk_class": "MODERATE",
                "risk_prob": 0.45,
                "adverse": ["Attainment cliff at Bloom Level 4 (Analyze)"],
                "protective": ["Strong recall and conceptual definition scores"],
                "has_intervention": True,
                "intervention_title": "Higher-Order Algorithmic Problem Solving Workshop",
                "project_title": "Sorting Algorithm Visualizer",
                "project_status": "VERIFIED",
                "role_coverage_core": 65.0,
                "role_coverage_prac": 55.0,
                "alignment": "PARTIAL_EVIDENCE_ALIGNMENT",
            },
            {
                "num": "006",
                "first": "Sneha",
                "last": "Rao",
                "email": "sneha.rao@siat.edu",
                "scenario": "Scenario 6: Active Faculty-Reviewed Intervention with Tracked Progress",
                "attendance": 72.0,
                "exam_score": 26.0,
                "max_score": 50.0,
                "mastery_scores": [52.0, 48.0],
                "risk_class": "MODERATE",
                "risk_prob": 0.52,
                "adverse": ["Mid-term 1 score below median"],
                "protective": ["Engaged with faculty support plan", "Completed 2 assigned coding tasks"],
                "has_intervention": True,
                "intervention_title": "Dynamic Programming Structured Support Plan",
                "project_title": "Knapsack Optimization Simulator",
                "project_status": "VERIFIED",
                "role_coverage_core": 70.0,
                "role_coverage_prac": 75.0,
                "alignment": "PARTIAL_EVIDENCE_ALIGNMENT",
            },
            {
                "num": "007",
                "first": "Vikram",
                "last": "Choudhury",
                "email": "vikram.choudhury@siat.edu",
                "scenario": "Scenario 7: Divergent Career Alignment (Strong Web Developer, Developing ML)",
                "attendance": 89.0,
                "exam_score": 41.0,
                "max_score": 50.0,
                "mastery_scores": [82.0, 84.0],
                "risk_class": "LOW",
                "risk_prob": 0.12,
                "adverse": [],
                "protective": ["Consistent assessment performance", "High project engagement"],
                "has_intervention": False,
                "project_title": "Full-Stack Collaborative Document Editor",
                "project_status": "VERIFIED",
                "role_coverage_core": 88.0,
                "role_coverage_prac": 92.0,
                "alignment": "STRONG_EVIDENCE_ALIGNMENT",
            },
            {
                "num": "008",
                "first": "Pooja",
                "last": "Hegde",
                "email": "pooja.hegde@siat.edu",
                "scenario": "Scenario 8: Practical Engineering Project Awaiting Faculty Review",
                "attendance": 86.0,
                "exam_score": 38.0,
                "max_score": 50.0,
                "mastery_scores": [76.0, 74.0],
                "risk_class": "LOW",
                "risk_prob": 0.18,
                "adverse": [],
                "protective": ["Solid course attendance", "Practical project in verification queue"],
                "has_intervention": False,
                "project_title": "Distributed Task Queue in Python",
                "project_status": "PENDING_REVIEW",
                "role_coverage_core": 75.0,
                "role_coverage_prac": 50.0,
                "alignment": "PARTIAL_EVIDENCE_ALIGNMENT",
            },
            {
                "num": "009",
                "first": "Tanmay",
                "last": "Deshmukh",
                "email": "tanmay.deshmukh@siat.edu",
                "scenario": "Scenario 9: Verified Open-Source Production Portfolio Evidence",
                "attendance": 92.0,
                "exam_score": 45.0,
                "max_score": 50.0,
                "mastery_scores": [95.0, 92.0, 89.0],
                "risk_class": "LOW",
                "risk_prob": 0.05,
                "adverse": [],
                "protective": ["Exceptional topic mastery", "Verified distributed systems engineering project"],
                "has_intervention": False,
                "project_title": "Raft Consensus Protocol Implementation in Rust",
                "project_status": "VERIFIED",
                "role_coverage_core": 94.0,
                "role_coverage_prac": 98.0,
                "alignment": "STRONG_EVIDENCE_ALIGNMENT",
            },
            {
                "num": "010",
                "first": "Ananya",
                "last": "Dixit",
                "email": "ananya.dixit@siat.edu",
                "scenario": "Scenario 10: Categorized Industry Skill Gaps with Developmental Roadmap",
                "attendance": 85.0,
                "exam_score": 40.0,
                "max_score": 50.0,
                "mastery_scores": [80.0, 78.0],
                "risk_class": "LOW",
                "risk_prob": 0.16,
                "adverse": ["Missing demonstrated practical evidence in Containerization and Message Queues"],
                "protective": ["High core database and algorithmic proficiency"],
                "has_intervention": False,
                "project_title": "Relational Database Engine Parser",
                "project_status": "VERIFIED",
                "role_coverage_core": 82.0,
                "role_coverage_prac": 64.0,
                "alignment": "PARTIAL_EVIDENCE_ALIGNMENT",
            },
        ]

        seeded_count = 0
        for spec in demo_students_spec:
            # Identity Profile
            p_stmt = select(Profile).where(Profile.email == spec["email"])
            prof = session.execute(p_stmt).scalars().first()
            if not prof:
                prof = Profile(
                    id=uuid.uuid4(),
                    email=spec["email"],
                    full_name=f"{spec['first']} {spec['last']}",
                    role=UserRole.STUDENT.value,
                    account_status=AccountStatus.ACTIVE.value,
                    institution_id=inst.id,
                )
                session.add(prof)
                session.flush()

            # Academic Profile
            sap_stmt = select(StudentAcademicProfile).where(
                StudentAcademicProfile.enrollment_number == f"DEMO-CSE-{spec['num']}"
            )
            sap = session.execute(sap_stmt).scalars().first()
            if not sap:
                sap = StudentAcademicProfile(
                    id=uuid.uuid4(),
                    profile_id=prof.id,
                    institution_id=inst.id,
                    program_id=prog.id,
                    enrollment_number=f"DEMO-CSE-{spec['num']}",
                    first_name=spec["first"],
                    last_name=spec["last"],
                    email=spec["email"],
                    department="Computer Science & Engineering",
                    admission_year=2023,
                    current_semester=5,
                    academic_status="ENROLLED",
                )
                session.add(sap)
                session.flush()
                seeded_count += 1

            # Subject Enrollment
            enr_stmt = select(StudentSubjectEnrollment).where(
                StudentSubjectEnrollment.student_id == sap.id,
                StudentSubjectEnrollment.subject_id == primary_subj.id,
            )
            if not session.execute(enr_stmt).scalars().first():
                enr = StudentSubjectEnrollment(
                    institution_id=inst.id,
                    student_id=sap.id,
                    subject_id=primary_subj.id,
                    academic_year="2024-2025",
                    semester=5,
                )
                session.add(enr)

            # Attendance Record
            att_stmt = select(StudentAttendanceRecord).where(
                StudentAttendanceRecord.student_id == sap.id,
                StudentAttendanceRecord.subject_id == primary_subj.id,
            )
            if not session.execute(att_stmt).scalars().first():
                att = StudentAttendanceRecord(
                    institution_id=inst.id,
                    student_id=sap.id,
                    subject_id=primary_subj.id,
                    academic_year="2024-2025",
                    semester=5,
                    attendance_date=now - timedelta(days=5),
                    attendance_status=AttendanceStatus.PRESENT.value if spec["attendance"] > 75 else AttendanceStatus.ABSENT.value,
                )
                session.add(att)

            # Assessment Record
            if spec["exam_score"] is not None:
                ass_stmt = select(AcademicAssessment).where(
                    AcademicAssessment.subject_id == primary_subj.id,
                    AcademicAssessment.assessment_name == "Mid-Term Examination 1"
                )
                exam = session.execute(ass_stmt).scalars().first()
                if not exam:
                    exam = AcademicAssessment(
                        id=uuid.uuid4(),
                        institution_id=inst.id,
                        subject_id=primary_subj.id,
                        assessment_name="Mid-Term Examination 1",
                        assessment_type=AssessmentType.MID_TERM.value,
                        maximum_marks=50.0,
                        academic_year="2024-2025",
                        semester=5,
                    )
                    session.add(exam)
                    session.flush()

                rec_stmt = select(StudentAssessmentRecord).where(
                    StudentAssessmentRecord.student_id == sap.id,
                    StudentAssessmentRecord.assessment_id == exam.id,
                )
                if not session.execute(rec_stmt).scalars().first():
                    rec = StudentAssessmentRecord(
                        institution_id=inst.id,
                        student_id=sap.id,
                        assessment_id=exam.id,
                        marks_obtained=spec["exam_score"],
                        maximum_marks_snapshot=spec["max_score"],
                        verification_status=RecordVerificationStatus.VERIFIED.value,
                    )
                    session.add(rec)

            # Topic Mastery Results
            for idx, m_score in enumerate(spec["mastery_scores"]):
                if idx < len(demo_topics):
                    t_obj = demo_topics[idx]
                    top_stmt = select(TopicMasteryResult).where(
                        TopicMasteryResult.student_id == sap.id,
                        TopicMasteryResult.topic_id == t_obj.id,
                    )
                    if not session.execute(top_stmt).scalars().first():
                        m_res = TopicMasteryResult(
                            institution_id=inst.id,
                            analysis_job_id=mastery_job.id,
                            student_id=sap.id,
                            subject_id=primary_subj.id,
                            topic_id=t_obj.id,
                            mastery_percentage=m_score,
                            mastery_status="DEMONSTRATED" if m_score >= 70.0 else "DEVELOPING",
                            evidence_sufficiency="SUFFICIENT",
                        )
                        session.add(m_res)

            # Academic Risk Prediction
            risk_stmt = select(AcademicRiskPrediction).where(
                AcademicRiskPrediction.student_id == sap.id,
                AcademicRiskPrediction.target_id == risk_target.id,
            )
            if not session.execute(risk_stmt).scalars().first():
                pred = AcademicRiskPrediction(
                    institution_id=inst.id,
                    student_id=sap.id,
                    subject_id=primary_subj.id,
                    target_id=risk_target.id,
                    risk_classification=spec["risk_class"],
                    risk_score=spec["risk_prob"],
                    prediction_cutoff_date=now,
                )
                session.add(pred)
                session.flush()

                for factor in spec["adverse"]:
                    exp = AcademicRiskPredictionExplanation(
                        prediction_id=pred.id,
                        feature_name="academic_performance",
                        feature_value=spec["exam_score"] or 0.0,
                        contribution_weight=0.35,
                        explanation_text=factor,
                        is_adverse_factor=True,
                    )
                    session.add(exp)

                for factor in spec["protective"]:
                    exp = AcademicRiskPredictionExplanation(
                        prediction_id=pred.id,
                        feature_name="attendance_consistency",
                        feature_value=spec["attendance"],
                        contribution_weight=0.25,
                        explanation_text=factor,
                        is_adverse_factor=False,
                    )
                    session.add(exp)

            # Academic Intervention Plan (if applicable)
            if spec["has_intervention"]:
                plan_stmt = select(AcademicInterventionPlan).where(
                    AcademicInterventionPlan.student_id == sap.id,
                    AcademicInterventionPlan.plan_title == spec["intervention_title"],
                )
                if not session.execute(plan_stmt).scalars().first():
                    plan = AcademicInterventionPlan(
                        institution_id=inst.id,
                        student_id=sap.id,
                        subject_id=primary_subj.id,
                        plan_title=spec["intervention_title"],
                        learning_objective="Remediate core algorithmic topic deficiencies with targeted tasks",
                        plan_status=InterventionPlanStatus.ACTIVE.value,
                        assigned_faculty_id=staff_profiles[UserRole.FACULTY].id,
                    )
                    session.add(plan)
                    session.flush()

                    action = AcademicInterventionAction(
                        institution_id=inst.id,
                        plan_id=plan.id,
                        action_title="Complete 3 Guided Graph Traversal Problems",
                        action_status="PENDING",
                        instructions="Submit repository pull request or code notebook for faculty review",
                    )
                    session.add(action)

            # Practical Project Evidence (if applicable)
            if spec["project_title"]:
                proj_stmt = select(StudentProjectEvidence).where(
                    StudentProjectEvidence.student_id == sap.id,
                    StudentProjectEvidence.title == spec["project_title"],
                )
                if not session.execute(proj_stmt).scalars().first():
                    proj = StudentProjectEvidence(
                        institution_id=inst.id,
                        student_id=sap.id,
                        title=spec["project_title"],
                        description=f"Synthetic demonstration project for {spec['first']} {spec['last']}.",
                        repository_url=f"https://github.com/{spec['first'].lower()}/{spec['project_title'].lower().replace(' ', '-')}",
                        verification_status=spec["project_status"],
                        reviewer_id=staff_profiles[UserRole.FACULTY].id if spec["project_status"] == "VERIFIED" else None,
                        reviewed_at=now if spec["project_status"] == "VERIFIED" else None,
                        verification_notes="Verified code quality, git history, and design modularity." if spec["project_status"] == "VERIFIED" else None,
                    )
                    session.add(proj)

            # Career Readiness Analysis
            readiness_stmt = select(CareerReadinessAnalysis).where(
                CareerReadinessAnalysis.student_id == sap.id,
                CareerReadinessAnalysis.role_id == backend_role.id,
            )
            if not session.execute(readiness_stmt).scalars().first():
                readiness = CareerReadinessAnalysis(
                    institution_id=inst.id,
                    student_id=sap.id,
                    role_id=backend_role.id,
                    alignment_status=spec["alignment"],
                    core_competency_coverage=spec["role_coverage_core"],
                    practical_evidence_coverage=spec["role_coverage_prac"],
                    summary_rationale=f"Evaluated against backend engineering benchmark: {spec['scenario']}",
                )
                session.add(readiness)

        session.commit()
        print(f"[DEMO SEED] SUCCESS: Verified {len(demo_students_spec)} demonstration student personas in database.")
    except Exception as exc:
        session.rollback()
        print(f"[DEMO SEED] ERROR seeding demonstration data: {exc}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_demo_data()
