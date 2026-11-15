# MASTERY Synthetic Demo Data Architecture

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Implementation:** Pure Frontend TypeScript Fixtures (`frontend/src/demo/`)  
**Database Policy:** Strict Isolation — Zero Database Writes, Zero Database Mutations  

---

## 1. Ethical & Architectural Boundary

A core requirement of the Phase 11 transformation is that the demonstration experience must be **entirely decoupled from database writes**:
- **No Supabase DB Writes:** No synthetic student profiles, marks, or syllabus rows are written to the live PostgreSQL instance.
- **No Database Migrations or Seeding Scripts:** Production database tables remain clean and unpolluted.
- **Frontend Memory Boundary:** All demo fixtures are statically typed TypeScript objects served via an in-memory `DemoContext`.
- **Transparent Disclaimers:** All screens rendered in Demo Mode display a permanent badge:  
  `DEMO DATA — SYNTHETIC / NOT REAL STUDENT RECORDS`

---

## 2. Institutional Entity Hierarchy

The synthetic demo dataset establishes a coherent academic ecosystem for **VARY Institute of Technology**:

### 2.1 Institution & Programs
- **Institution:** VARY Institute of Technology (VIT-CSE-2026)
- **Departments:**
  1. Department of Computer Science & Engineering (CSE)
  2. Department of Information Technology (IT)
- **Academic Programs:**
  - B.Tech Computer Science & Engineering (4 Years, Cohort 2022–2026, Semester 6)
  - B.Tech Information Technology (4 Years, Cohort 2022–2026, Semester 6)

### 2.2 Faculty Members
1. **Dr. Sarah Vance** — Professor & Head of Department (Algorithms & Data Structures)
2. **Prof. Rajiv Sharma** — Associate Professor (Database Management Systems)
3. **Dr. Priya Nair** — Assistant Professor (Operating Systems & Cloud)
4. **Prof. Michael Chang** — Senior Lecturer (Computer Networks)
5. **Dr. Alistair Chen** — Professor of AI (Machine Learning & Data Mining)

### 2.3 Academic Subjects (6)
1. `CS601` — Advanced Data Structures & Algorithms (Credits: 4)
2. `CS602` — Database Management Systems & Architecture (Credits: 4)
3. `CS603` — Computer Networks & Distributed Systems (Credits: 3)
4. `CS604` — Operating Systems & Concurrency (Credits: 4)
5. `CS605` — Artificial Intelligence & Machine Learning (Credits: 4)
6. `CS606` — Theory of Computation & Automata (Credits: 3)

---

## 3. The Four Deterministic Student Scenarios

To demonstrate how MASTERY accurately differentiates student learning states, the demo dataset defines four representative scenarios tracked consistently across all 7 modules:

```text
========================================================================================
Scenario ID   Student Name     Enrollment   Primary Academic State           Risk Class
========================================================================================
Scenario A    Aarav Sharma     CS22-004     Strong, Mastery Progress         LOW (11%)
Scenario B    Diya Patel       CS22-011     Inconsistent Progress, 1-2 Gaps  MODERATE (42%)
Scenario C    Rohan Gupta      CS22-019     Emerging Academic Risk           HIGH (78%)
Scenario D    Ananya Sen       CS22-024     Insufficient Evidence / Missing  INSUFFICIENT (N/A)
========================================================================================
```

### Scenario A: Strong Progress (Aarav Sharma — CS22-004)
- **Attendance:** 92.4% (Verified, consistent).
- **Assessments:** Continuous high performance on Midterm (46/50) and Algorithms Quiz (24/25).
- **Mastery Analytics:** 14 Topics `MASTERED`, 3 `PROGRESSING`, 0 `NEEDS_ATTENTION`. 5/5 Course Learning Outcomes attained.
- **Academic Risk:** 11% Probability — Classified as `LOW RISK`. Dominant protective factors: High assignment completion, excellent topic mastery, robust prior GPA (8.92).
- **Interventions:** Completed enrichment template: "Distributed Algorithms Research Fellowship".
- **Career Readiness:** 88% Core Competency Coverage, 85% Practical Project Coverage for **Full-Stack Engineer** and **Data Systems Engineer**. 4 verified portfolio projects.

### Scenario B: Inconsistent Progress (Diya Patel — CS22-011)
- **Attendance:** 78.5% (Acceptable, occasional illness).
- **Assessments:** Strong in conceptual theory (41/50) but struggled in Concurrency Lab (18/50).
- **Mastery Analytics:** 9 Topics `MASTERED`, 5 `PROGRESSING`, 2 `NEEDS_ATTENTION` (B-Trees, Thread Synchronization).
- **Academic Risk:** 42% Probability — Classified as `MODERATE RISK`. Adverse factor: Volatile lab quiz trajectory. Protective factor: High conceptual midterm score.
- **Interventions:** Active Plan: "Concurrency Debugging Lab Clinic" (Under Faculty Supervision).
- **Career Readiness:** 72% Academic Coverage, 60% Practical Coverage for **AI/ML Engineer**.

### Scenario C: Emerging Academic Risk (Rohan Gupta — CS22-019)
- **Attendance:** 66.2% (Below institutional threshold of 75%).
- **Assessments:** Declining trend across continuous evaluations (Quiz 1: 18/25 → Quiz 2: 11/25 → Midterm: 19/50).
- **Mastery Analytics:** 4 Topics `MASTERED`, 6 `PROGRESSING`, 7 `NEEDS_ATTENTION`. Identified learning gap in Dynamic Programming & Graph Traversal.
- **Academic Risk:** 78% Probability — Classified as `HIGH RISK`. Key adverse factors: Continuous assessment decline (-35%), low attendance, 7 topic deficits. Baseline deterministic rules triggered.
- **Interventions:** Priority Intervention: "Foundation Algorithms Remediation & Faculty Advising", Status: `APPROVED / ACTIVE`.
- **Career Readiness:** Significant skill gaps across core database and algorithm competencies.

### Scenario D: Insufficient Evidence (Ananya Sen — CS22-024)
- **Attendance:** 58.0% (Medical Leave).
- **Assessments:** Missed Midterm Assessment (Excused Absence), only 1 Quiz completed.
- **Mastery Analytics:** Classified explicitly as `INSUFFICIENT_EVIDENCE`. The system **does not treat missing assessments as zero marks**.
- **Academic Risk:** Blocked by Dataset Sufficiency Gate. Risk output: `INSUFFICIENT_EVIDENCE`. Prevents misleading model hallucination.
- **Interventions:** Diagnostic Evidence Pathway: "Make-Up Competency Assessment & Academic Advising".
- **Career Readiness:** 35% Verified Evidence. Role alignment flagged as `PENDING_EVIDENCE`.

---

## 4. Cross-Module Consistency Guarantee

Every data point rendered on the **Unified Dashboard** aligns exactly with the drill-down details visible on:
- Academic Data Hub (`/app/academic-data`)
- Syllabus & Competency (`/app/syllabus`)
- Assessment Engine (`/app/assessments`)
- Mastery Analytics (`/app/mastery`)
- Academic Risk Engine (`/app/risk`)
- Interventions (`/app/interventions`)
- Career Readiness (`/app/career-readiness`)

When a user switches the active scenario in the Demo Toolbar, all seven module views instantaneously refresh their state to reflect that student's complete academic narrative.
