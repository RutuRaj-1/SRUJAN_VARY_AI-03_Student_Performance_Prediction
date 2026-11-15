# MASTERY — Database Architecture & Entity Relationship Design

**Database Engine:** PostgreSQL 15+ (Hosted on Supabase)  
**ORM:** SQLAlchemy 2.0+ Declarative Mapping  
**Migration Framework:** Alembic  
**Phase:** 02/11 — Supabase Integration & Identity Foundation  

---

## 1. Database Design Principles

1. **UUID Primary Keys:** All primary entity identifiers use UUIDv4 (`uuid.uuid4()`). The `profiles.id` directly matches `auth.users(id)`.
2. **Standard Audit Mixin:** Every table implements `created_at` and `updated_at` timestamps stored in UTC (`DateTime(timezone=True)`).
3. **Evidence Provenance & Immutability:** Academic assessment attempts, submission telemetry, and diagnostic logs are append-only.
4. **Decoupled Intelligence Schemas:**
   - Formal institutional records (attendance, internal marks) are stored separately from calibrated mastery records.
   - Academic risk predictions are stored with their model version and feature snapshot.
   - Industry competency evaluations are mapped to role benchmarks without polluting student academic gradebooks.
5. **Multi-Institution Tenancy:** Users belong to institutions via `institution_memberships` with independent `membership_role` and `membership_status`.

---

## 2. Phase 02 Initial Tables

### `institutions`
Represents educational institutions (universities, autonomous colleges, polytechnics).
```sql
CREATE TABLE institutions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    institution_code VARCHAR(50) NOT NULL UNIQUE,
    institution_type VARCHAR(100) NOT NULL DEFAULT 'Autonomous Engineering Institute',
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL DEFAULT 'India',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `profiles`
Connects Supabase Auth identities (`auth.users`) with application-level user profiles.
```sql
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(50),
    avatar_url VARCHAR(1024),
    role VARCHAR(50) NOT NULL DEFAULT 'STUDENT',
    institution_id UUID REFERENCES institutions(id) ON DELETE SET NULL,
    account_status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `institution_memberships`
Establishes user-to-institution relationships with institutional roles and approval lifecycles.
```sql
CREATE TABLE institution_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    membership_role VARCHAR(50) NOT NULL DEFAULT 'STUDENT',
    membership_status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_institution_user UNIQUE (institution_id, user_id)
);
```

---

## 3. Row-Level Security (RLS) Policy Specifications

### `institutions` Table
- **Policy 1:** `Active institutions readable by authenticated`
  - Command: `SELECT`
  - Target: `authenticated`
  - Expression: `USING (is_active = true)`
- **Policy 2:** `Super admins manage institutions`
  - Command: `ALL`
  - Target: `authenticated`
  - Expression: `USING (EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN'))`

### `profiles` Table
- **Policy 1:** `Users can read own profile`
  - Command: `SELECT`
  - Target: `authenticated`
  - Expression: `USING (id = auth.uid())`
- **Policy 2:** `Users can update own self-profile`
  - Command: `UPDATE`
  - Target: `authenticated`
  - Expression: `USING (id = auth.uid()) WITH CHECK (id = auth.uid())`
- **Policy 3:** `Staff can read institution member profiles`
  - Command: `SELECT`
  - Target: `authenticated`
  - Expression: `USING (institution_id IN (SELECT institution_id FROM institution_memberships WHERE user_id = auth.uid() AND membership_status = 'ACTIVE' AND membership_role IN ('ADMIN', 'FACULTY')))`

### `institution_memberships` Table
- **Policy 1:** `Users can view own memberships`
  - Command: `SELECT`
  - Target: `authenticated`
  - Expression: `USING (user_id = auth.uid())`
- **Policy 2:** `Institution admins manage memberships`
  - Command: `ALL`
  - Target: `authenticated`
  - Expression: `USING (institution_id IN (SELECT institution_id FROM institution_memberships WHERE user_id = auth.uid() AND membership_status = 'ACTIVE' AND membership_role = 'ADMIN'))`


---

## 4. Phase 03: AI Syllabus & Competency Intelligence Tables

### `academic_programs`
Degree programs offered by an institution (e.g. B.Tech Computer Science).
```sql
CREATE TABLE academic_programs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL,
    degree_type VARCHAR(100) NOT NULL DEFAULT 'Bachelor of Technology',
    duration_years INTEGER NOT NULL DEFAULT 4,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_academic_programs_institution_id ON academic_programs(institution_id);
```

### `academic_subjects`
Individual courses/subjects under a degree program.
```sql
CREATE TABLE academic_subjects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    program_id UUID NOT NULL REFERENCES academic_programs(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL,
    semester INTEGER NOT NULL,
    academic_year VARCHAR(50) NOT NULL DEFAULT '2024-2025',
    regulation_version VARCHAR(50) NOT NULL DEFAULT 'R22',
    credits INTEGER NOT NULL DEFAULT 4,
    total_hours INTEGER NOT NULL DEFAULT 45,
    description TEXT,
    prerequisites JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_academic_subjects_code ON academic_subjects(code);
CREATE INDEX ix_academic_subjects_institution_id ON academic_subjects(institution_id);
CREATE INDEX ix_academic_subjects_program_id ON academic_subjects(program_id);
```

### `syllabus_documents`
Raw curriculum files uploaded for extraction and processing lifecycle tracking.
```sql
CREATE TABLE syllabus_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    subject_id UUID REFERENCES academic_subjects(id) ON DELETE SET NULL,
    uploaded_by UUID REFERENCES profiles(id) ON DELETE SET NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    storage_path VARCHAR(512) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'UPLOADED',
    raw_text TEXT,
    extraction_metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_syllabus_documents_status ON syllabus_documents(status);
CREATE INDEX ix_syllabus_documents_institution_id ON syllabus_documents(institution_id);
CREATE INDEX ix_syllabus_documents_subject_id ON syllabus_documents(subject_id);
```

### `syllabus_units` & `syllabus_topics`
Hierarchical curriculum tree representation of units, topics, and subtopics.
```sql
CREATE TABLE syllabus_units (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES syllabus_documents(id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES academic_subjects(id) ON DELETE CASCADE,
    unit_number INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    estimated_hours INTEGER NOT NULL DEFAULT 9,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE syllabus_topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    unit_id UUID NOT NULL REFERENCES syllabus_units(id) ON DELETE CASCADE,
    topic_name VARCHAR(255) NOT NULL,
    subtopics JSONB DEFAULT '[]'::jsonb,
    order_index INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `learning_outcomes`
Course Learning Outcomes (CLOs) classified by Bloom's Taxonomy.
```sql
CREATE TABLE learning_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id UUID NOT NULL REFERENCES academic_subjects(id) ON DELETE CASCADE,
    unit_id UUID REFERENCES syllabus_units(id) ON DELETE SET NULL,
    outcome_code VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    bloom_level VARCHAR(50) NOT NULL DEFAULT 'APPLY',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `competencies` & `subject_competency_mappings`
Extracted technical capabilities classified into Theoretical, Programming, Tools/Technologies, Analytical, and Practical.
```sql
CREATE TABLE competencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID REFERENCES institutions(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL DEFAULT 'THEORETICAL',
    bloom_level VARCHAR(50) NOT NULL DEFAULT 'UNDERSTAND',
    depth_level INTEGER NOT NULL DEFAULT 3,
    syllabus_evidence TEXT,
    is_verified BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE subject_competency_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id UUID NOT NULL REFERENCES academic_subjects(id) ON DELETE CASCADE,
    unit_id UUID REFERENCES syllabus_units(id) ON DELETE SET NULL,
    topic_id UUID REFERENCES syllabus_topics(id) ON DELETE SET NULL,
    outcome_id UUID REFERENCES learning_outcomes(id) ON DELETE SET NULL,
    competency_id UUID NOT NULL REFERENCES competencies(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `industry_role_profiles` & `industry_competency_requirements`
Reference benchmark technical roles (Backend SDE, Full-Stack, Data Engineer, ML Engineer, DevOps).
```sql
CREATE TABLE industry_role_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_title VARCHAR(255) NOT NULL,
    role_family VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    experience_tier VARCHAR(50) NOT NULL DEFAULT 'Entry-Level / Fresher',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE industry_competency_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id UUID NOT NULL REFERENCES industry_role_profiles(id) ON DELETE CASCADE,
    competency_name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL DEFAULT 'PROGRAMMING',
    required_depth INTEGER NOT NULL DEFAULT 3,
    importance VARCHAR(50) NOT NULL DEFAULT 'HIGH',
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `curriculum_gap_analyses`
Explainable alignment evaluation between academic competencies and industry benchmarks.
```sql
CREATE TABLE curriculum_gap_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id UUID NOT NULL REFERENCES academic_subjects(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES industry_role_profiles(id) ON DELETE CASCADE,
    industry_competency_id UUID NOT NULL REFERENCES industry_competency_requirements(id) ON DELETE CASCADE,
    academic_competency_id UUID REFERENCES competencies(id) ON DELETE SET NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'MISSING',
    rationale TEXT NOT NULL,
    evidence TEXT,
    recommendation TEXT,
    analyzed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `syllabus_review_history`
Immutable audit log recording faculty reviews, approvals, and unit/topic edits.
```sql
CREATE TABLE syllabus_review_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES syllabus_documents(id) ON DELETE CASCADE,
    reviewed_by UUID REFERENCES profiles(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    previous_value JSONB,
    new_value JSONB,
    comments TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```


---

## 4. Phase 04 Tables: Academic Data Intelligence Hub

### `student_academic_profiles`
Maintains institutional student identities, enrollment details, and optional links to Supabase auth accounts.
```sql
CREATE TABLE student_academic_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    profile_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    program_id UUID REFERENCES academic_programs(id) ON DELETE SET NULL,
    enrollment_number VARCHAR(100) NOT NULL,
    admission_number VARCHAR(100),
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(255),
    department VARCHAR(150) NOT NULL,
    admission_year INTEGER NOT NULL DEFAULT 2024,
    current_semester INTEGER NOT NULL DEFAULT 1,
    academic_status VARCHAR(50) NOT NULL DEFAULT 'ENROLLED',
    verification_status VARCHAR(50) NOT NULL DEFAULT 'UNVERIFIED',
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_student_inst_enrollment UNIQUE (institution_id, enrollment_number)
);
```

### `student_subject_enrollments`
Course registrations per student, subject, semester, and academic year.
```sql
CREATE TABLE student_subject_enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES student_academic_profiles(id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES academic_subjects(id) ON DELETE CASCADE,
    academic_year VARCHAR(50) NOT NULL,
    semester INTEGER NOT NULL,
    enrollment_status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_student_sub_term UNIQUE (student_id, subject_id, academic_year, semester)
);
```

### `academic_assessments`
Assessment definitions, types, maximum marks, and weightages.
```sql
CREATE TABLE academic_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES academic_subjects(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    assessment_type VARCHAR(50) NOT NULL,
    max_marks NUMERIC(6, 2) NOT NULL,
    passing_marks NUMERIC(6, 2),
    weightage_percentage NUMERIC(5, 2),
    academic_year VARCHAR(50) NOT NULL,
    semester INTEGER NOT NULL,
    assessment_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `student_assessment_records`
Individual student scores, snapshots, and non-numeric states (`PASSED`, `FAILED`, `ABSENT`, `NOT_SUBMITTED`, `EXEMPTED`).
```sql
CREATE TABLE student_assessment_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    assessment_id UUID NOT NULL REFERENCES academic_assessments(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES student_academic_profiles(id) ON DELETE CASCADE,
    marks_obtained NUMERIC(6, 2),
    max_marks_snapshot NUMERIC(6, 2) NOT NULL,
    result_status VARCHAR(50) NOT NULL DEFAULT 'PASSED',
    verification_status VARCHAR(50) NOT NULL DEFAULT 'UNVERIFIED',
    verified_by_user_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    verified_at TIMESTAMPTZ,
    evaluation_remarks TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_student_assessment UNIQUE (assessment_id, student_id)
);
```

### `student_attendance_records`
Session-level attendance records per student and subject.
```sql
CREATE TABLE student_attendance_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES student_academic_profiles(id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES academic_subjects(id) ON DELETE CASCADE,
    session_date DATE NOT NULL,
    session_name VARCHAR(150) NOT NULL DEFAULT 'Lecture',
    status VARCHAR(50) NOT NULL,
    minutes_attended INTEGER,
    remarks TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_student_attendance_session UNIQUE (student_id, subject_id, session_date, session_name)
);
```

### `academic_import_jobs`, `academic_import_errors`, `academic_data_quality_findings`, `academic_record_audits`
Supporting tables for batch ingestion, multi-severity data quality analysis, and immutable compliance auditing.

---

## 5. Module 04: Assessment & Engagement Engine Schema (Phase 05)

### `assessment_questions` & `assessment_question_options`
Curriculum-aligned multi-modal question bank with server-side answer key protection.
```sql
CREATE TABLE assessment_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES academic_subjects(id) ON DELETE CASCADE,
    syllabus_unit_id UUID REFERENCES syllabus_units(id) ON DELETE SET NULL,
    syllabus_topic_id UUID REFERENCES syllabus_topics(id) ON DELETE SET NULL,
    learning_outcome_id UUID REFERENCES learning_outcomes(id) ON DELETE SET NULL,
    competency_id UUID REFERENCES competencies(id) ON DELETE SET NULL,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL,
    difficulty VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
    bloom_level VARCHAR(50) NOT NULL DEFAULT 'APPLY',
    default_marks FLOAT NOT NULL DEFAULT 1.0,
    evaluation_method VARCHAR(50) NOT NULL DEFAULT 'AUTOMATED_EXACT',
    explanation TEXT,
    expected_answer TEXT,
    code_language VARCHAR(50),
    code_template TEXT,
    created_by UUID REFERENCES profiles(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE assessment_question_options (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL REFERENCES assessment_questions(id) ON DELETE CASCADE,
    option_text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL DEFAULT false,
    display_order INTEGER NOT NULL DEFAULT 1,
    feedback TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `assessment_question_mappings` & `assessment_learning_outcome_mappings`
Maps questions and learning outcomes to scheduled assessments.
```sql
CREATE TABLE assessment_question_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID NOT NULL REFERENCES academic_assessments(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES assessment_questions(id) ON DELETE CASCADE,
    display_order INTEGER NOT NULL DEFAULT 1,
    marks_allocated FLOAT NOT NULL DEFAULT 1.0,
    required BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_assessment_question UNIQUE (assessment_id, question_id)
);
```

### `assessment_attempts` & `assessment_responses`
Student test session execution, deadline enforcement, autosave, and revision tracking.
```sql
CREATE TABLE assessment_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    assessment_id UUID NOT NULL REFERENCES academic_assessments(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES student_academic_profiles(id) ON DELETE CASCADE,
    attempt_number INTEGER NOT NULL DEFAULT 1,
    attempt_status VARCHAR(50) NOT NULL DEFAULT 'IN_PROGRESS',
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    submitted_at TIMESTAMPTZ,
    deadline_at TIMESTAMPTZ,
    total_marks FLOAT NOT NULL,
    marks_obtained FLOAT,
    evaluation_status VARCHAR(50) NOT NULL DEFAULT 'NOT_EVALUATED',
    evaluator_feedback TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE assessment_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    attempt_id UUID NOT NULL REFERENCES assessment_attempts(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES assessment_questions(id) ON DELETE CASCADE,
    response_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    marks_awarded FLOAT,
    feedback TEXT,
    evaluation_status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    is_auto_evaluated BOOLEAN NOT NULL DEFAULT false,
    revision_count INTEGER NOT NULL DEFAULT 0,
    saved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_attempt_question UNIQUE (attempt_id, question_id)
);
```

### `learning_engagement_events`
Non-invasive observable user-system interaction telemetry.
```sql
CREATE TABLE learning_engagement_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES student_academic_profiles(id) ON DELETE CASCADE,
    assessment_id UUID REFERENCES academic_assessments(id) ON DELETE CASCADE,
    attempt_id UUID REFERENCES assessment_attempts(id) ON DELETE CASCADE,
    event_type VARCHAR(80) NOT NULL,
    event_metadata JSONB DEFAULT '{}'::jsonb,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 9. Module 05: Learning Mastery & Performance Analytics Tables (Phase 06)

### `mastery_analysis_jobs`
Tracks recalculation jobs, batch parameters, performance execution runtimes, and status.
```sql
CREATE TABLE mastery_analysis_jobs (
    id VARCHAR(36) PRIMARY KEY,
    institution_id VARCHAR(36) NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    subject_id VARCHAR(36) NOT NULL REFERENCES academic_subjects(id) ON DELETE CASCADE,
    triggered_by_profile_id VARCHAR(36) REFERENCES profiles(id) ON DELETE SET NULL,
    job_type VARCHAR(50) NOT NULL DEFAULT 'FULL_SUBJECT_RECALCULATION',
    target_student_id VARCHAR(36) REFERENCES student_academic_profiles(id) ON DELETE CASCADE,
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    parameters_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    records_processed INTEGER NOT NULL DEFAULT 0,
    evidence_included_count INTEGER NOT NULL DEFAULT 0,
    evidence_excluded_count INTEGER NOT NULL DEFAULT 0,
    error_details TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `mastery_evidence_records`
Granular, immutable evidence with inclusion/exclusion audit reasons.
```sql
CREATE TABLE mastery_evidence_records (
    id VARCHAR(36) PRIMARY KEY,
    institution_id VARCHAR(36) NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    job_id VARCHAR(36) REFERENCES mastery_analysis_jobs(id) ON DELETE SET NULL,
    student_id VARCHAR(36) NOT NULL REFERENCES student_academic_profiles(id) ON DELETE CASCADE,
    subject_id VARCHAR(36) NOT NULL REFERENCES academic_subjects(id) ON DELETE CASCADE,
    topic_id VARCHAR(36) REFERENCES syllabus_topics(id) ON DELETE SET NULL,
    outcome_id VARCHAR(36) REFERENCES learning_outcomes(id) ON DELETE SET NULL,
    source_type VARCHAR(50) NOT NULL,
    source_attempt_id VARCHAR(36) REFERENCES assessment_attempts(id) ON DELETE SET NULL,
    source_response_id VARCHAR(36) REFERENCES assessment_responses(id) ON DELETE SET NULL,
    source_performance_id VARCHAR(36) REFERENCES student_assessment_performances(id) ON DELETE SET NULL,
    marks_obtained NUMERIC(6, 2) NOT NULL,
    marks_possible NUMERIC(6, 2) NOT NULL,
    normalized_percentage NUMERIC(5, 2) NOT NULL,
    weight NUMERIC(4, 2) NOT NULL DEFAULT 1.0,
    assessment_type VARCHAR(50) NOT NULL,
    bloom_level VARCHAR(50),
    attempt_timestamp TIMESTAMPTZ NOT NULL,
    eligibility_status VARCHAR(30) NOT NULL DEFAULT 'INCLUDED',
    exclusion_reason VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_mastery_evidence_source UNIQUE (student_id, source_type, source_response_id, source_performance_id)
);
```

### `topic_mastery_results`
Calculated topic performance, sufficiency levels, and confidence tiers.
```sql
CREATE TABLE topic_mastery_results (
    id VARCHAR(36) PRIMARY KEY,
    institution_id VARCHAR(36) NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    job_id VARCHAR(36) REFERENCES mastery_analysis_jobs(id) ON DELETE SET NULL,
    student_id VARCHAR(36) NOT NULL REFERENCES student_academic_profiles(id) ON DELETE CASCADE,
    subject_id VARCHAR(36) NOT NULL REFERENCES academic_subjects(id) ON DELETE CASCADE,
    topic_id VARCHAR(36) NOT NULL REFERENCES syllabus_topics(id) ON DELETE CASCADE,
    demonstrated_percentage NUMERIC(5, 2),
    raw_points_earned NUMERIC(8, 2) NOT NULL DEFAULT 0.0,
    raw_points_possible NUMERIC(8, 2) NOT NULL DEFAULT 0.0,
    evidence_count INTEGER NOT NULL DEFAULT 0,
    distinct_assessment_types_count INTEGER NOT NULL DEFAULT 0,
    sufficiency_level VARCHAR(30) NOT NULL DEFAULT 'INSUFFICIENT',
    confidence_category VARCHAR(30) NOT NULL DEFAULT 'LOW',
    mastery_status VARCHAR(30) NOT NULL DEFAULT 'INSUFFICIENT_EVIDENCE',
    first_evaluated_at TIMESTAMPTZ,
    last_evaluated_at TIMESTAMPTZ,
    bloom_level_distribution_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    scientific_disclaimer TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_student_subject_topic_mastery UNIQUE (student_id, subject_id, topic_id)
);
```

### `learning_outcome_attainment_results`
Course Learning Outcome attainment measured against institutional target thresholds.
```sql
CREATE TABLE learning_outcome_attainment_results (
    id VARCHAR(36) PRIMARY KEY,
    institution_id VARCHAR(36) NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    job_id VARCHAR(36) REFERENCES mastery_analysis_jobs(id) ON DELETE SET NULL,
    student_id VARCHAR(36) NOT NULL REFERENCES student_academic_profiles(id) ON DELETE CASCADE,
    subject_id VARCHAR(36) NOT NULL REFERENCES academic_subjects(id) ON DELETE CASCADE,
    outcome_id VARCHAR(36) NOT NULL REFERENCES learning_outcomes(id) ON DELETE CASCADE,
    attainment_percentage NUMERIC(5, 2),
    evidence_count INTEGER NOT NULL DEFAULT 0,
    attainment_status VARCHAR(30) NOT NULL DEFAULT 'INSUFFICIENT_EVIDENCE',
    threshold_percentage NUMERIC(5, 2) NOT NULL DEFAULT 60.0,
    scientific_disclaimer TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_student_outcome_attainment UNIQUE (student_id, outcome_id)
);
```

### `learning_gap_findings`
Identified curriculum gaps, separating low scores from unassessed topics.
```sql
CREATE TABLE learning_gap_findings (
    id VARCHAR(36) PRIMARY KEY,
    institution_id VARCHAR(36) NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    job_id VARCHAR(36) REFERENCES mastery_analysis_jobs(id) ON DELETE SET NULL,
    student_id VARCHAR(36) NOT NULL REFERENCES student_academic_profiles(id) ON DELETE CASCADE,
    subject_id VARCHAR(36) NOT NULL REFERENCES academic_subjects(id) ON DELETE CASCADE,
    topic_id VARCHAR(36) REFERENCES syllabus_topics(id) ON DELETE SET NULL,
    outcome_id VARCHAR(36) REFERENCES learning_outcomes(id) ON DELETE SET NULL,
    gap_type VARCHAR(50) NOT NULL,
    severity VARCHAR(30) NOT NULL DEFAULT 'MEDIUM',
    observed_percentage NUMERIC(5, 2),
    description TEXT NOT NULL,
    supporting_evidence_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_resolved BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 8. Phase 07: Academic Risk Prediction Tables

### `academic_risk_targets`
Defines institutional academic risk definitions, target classification policies, passing thresholds, and prediction horizons.
```sql
CREATE TABLE academic_risk_targets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES academic_subjects(id) ON DELETE CASCADE,
    target_code VARCHAR(64) NOT NULL,
    target_name VARCHAR(255) NOT NULL,
    outcome_definition TEXT NOT NULL,
    positive_label_definition TEXT NOT NULL,
    negative_label_definition TEXT NOT NULL,
    passing_threshold_percentage FLOAT NOT NULL DEFAULT 50.0,
    prediction_horizon_weeks INTEGER NOT NULL DEFAULT 4,
    is_institution_policy BOOLEAN NOT NULL DEFAULT false,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_risk_target_inst_subj_code UNIQUE (institution_id, subject_id, target_code)
);
```

### `risk_feature_snapshots`
Time-bounded snapshot of calculated academic feature vectors before observation cutoffs.
```sql
CREATE TABLE risk_feature_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES student_academic_profiles(id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES academic_subjects(id) ON DELETE CASCADE,
    target_id UUID REFERENCES academic_risk_targets(id) ON DELETE SET NULL,
    observation_cutoff_date TIMESTAMPTZ NOT NULL,
    feature_vector_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    data_provenance_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_risk_feature_snap_stud_subj_cutoff UNIQUE (student_id, subject_id, observation_cutoff_date)
);
```

### `risk_model_versions`
Institutional model registry storing trained machine learning algorithms and deterministic rule baselines.
```sql
CREATE TABLE risk_model_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    target_id UUID NOT NULL REFERENCES academic_risk_targets(id) ON DELETE CASCADE,
    version_tag VARCHAR(64) NOT NULL,
    model_type VARCHAR(32) NOT NULL,
    algorithm_name VARCHAR(128) NOT NULL,
    training_cutoff_date TIMESTAMPTZ NOT NULL,
    training_sample_count INTEGER NOT NULL DEFAULT 0,
    positive_sample_count INTEGER NOT NULL DEFAULT 0,
    negative_sample_count INTEGER NOT NULL DEFAULT 0,
    feature_names JSONB NOT NULL DEFAULT '[]'::jsonb,
    hyperparameters_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    parameters_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    model_artifact_path VARCHAR(512),
    is_active BOOLEAN NOT NULL DEFAULT false,
    model_status VARCHAR(32) NOT NULL DEFAULT 'TRAINED',
    trained_by_profile_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `risk_model_evaluations`
Quantitative validation benchmarks and evaluation metrics computed over cross-validation splits.
```sql
CREATE TABLE risk_model_evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    model_version_id UUID NOT NULL REFERENCES risk_model_versions(id) ON DELETE CASCADE,
    evaluation_type VARCHAR(32) NOT NULL,
    sample_size INTEGER NOT NULL,
    accuracy FLOAT,
    precision FLOAT,
    recall FLOAT,
    f1_score FLOAT,
    roc_auc FLOAT,
    brier_score FLOAT,
    confusion_matrix_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    evaluation_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `academic_risk_predictions`
Individual student inference predictions evaluated against a target policy.
```sql
CREATE TABLE academic_risk_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    target_id UUID NOT NULL REFERENCES academic_risk_targets(id) ON DELETE CASCADE,
    model_version_id UUID NOT NULL REFERENCES risk_model_versions(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES student_academic_profiles(id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES academic_subjects(id) ON DELETE CASCADE,
    cutoff_date TIMESTAMPTZ NOT NULL,
    risk_score FLOAT,
    risk_classification VARCHAR(32) NOT NULL,
    evidence_sufficiency VARCHAR(32) NOT NULL DEFAULT 'MODERATE',
    prediction_status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    scientific_disclaimer TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `academic_risk_prediction_explanations`
Grounded explanatory attributions and directional feature contributions.
```sql
CREATE TABLE academic_risk_prediction_explanations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prediction_id UUID NOT NULL REFERENCES academic_risk_predictions(id) ON DELETE CASCADE,
    feature_name VARCHAR(64) NOT NULL,
    feature_value FLOAT NOT NULL,
    contribution_weight FLOAT NOT NULL,
    explanation_text TEXT NOT NULL,
    source_evidence_reference VARCHAR(255) NOT NULL,
    is_adverse_factor BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `risk_prediction_jobs`
Batch execution audit trail for asynchronous cohort inference and screening.
```sql
CREATE TABLE risk_prediction_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES academic_subjects(id) ON DELETE CASCADE,
    target_id UUID NOT NULL REFERENCES academic_risk_targets(id) ON DELETE CASCADE,
    model_version_id UUID REFERENCES risk_model_versions(id) ON DELETE SET NULL,
    job_type VARCHAR(32) NOT NULL DEFAULT 'BATCH_INFERENCE',
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    total_students INTEGER NOT NULL DEFAULT 0,
    processed_students INTEGER NOT NULL DEFAULT 0,
    high_risk_detected_count INTEGER NOT NULL DEFAULT 0,
    error_summary TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);
```

---

## 9. Phase 08: Personalized Academic Intervention Tables

### `intervention_templates`
Reusable and institution-approved intervention catalog blueprints.
```sql
CREATE TABLE intervention_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    subject_id UUID REFERENCES academic_subjects(id) ON DELETE SET NULL,
    template_code VARCHAR(64) NOT NULL,
    template_name VARCHAR(255) NOT NULL,
    intervention_type VARCHAR(50) NOT NULL DEFAULT 'TARGETED_REVISION',
    description TEXT,
    target_level VARCHAR(30) NOT NULL DEFAULT 'TOPIC',
    suggested_duration_hours FLOAT NOT NULL DEFAULT 2.0,
    suggested_completion_days INTEGER NOT NULL DEFAULT 7,
    recommended_actions_template JSONB NOT NULL DEFAULT '[]'::jsonb,
    required_resources JSONB NOT NULL DEFAULT '[]'::jsonb,
    expected_evidence_type VARCHAR(100),
    requires_faculty_review BOOLEAN NOT NULL DEFAULT true,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_by_profile_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_intervention_template_inst_code UNIQUE (institution_id, template_code)
);
```

### `academic_intervention_recommendations`
Evidence-grounded candidate recommendations produced by the recommendation engine.
```sql
CREATE TABLE academic_intervention_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES student_academic_profiles(id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES academic_subjects(id) ON DELETE CASCADE,
    topic_id UUID REFERENCES syllabus_topics(id) ON DELETE SET NULL,
    learning_outcome_id UUID REFERENCES learning_outcomes(id) ON DELETE SET NULL,
    risk_prediction_id UUID REFERENCES academic_risk_predictions(id) ON DELETE SET NULL,
    learning_gap_id UUID REFERENCES learning_gap_findings(id) ON DELETE SET NULL,
    template_id UUID REFERENCES intervention_templates(id) ON DELETE SET NULL,
    recommendation_type VARCHAR(50) NOT NULL DEFAULT 'TARGETED_REVISION',
    priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
    rationale TEXT NOT NULL,
    source_evidence_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
    evidence_sufficiency VARCHAR(30) NOT NULL DEFAULT 'MODERATE',
    proposed_action_title VARCHAR(255) NOT NULL,
    proposed_action_description TEXT NOT NULL,
    suggested_duration_days INTEGER NOT NULL DEFAULT 7,
    status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
    scientific_disclaimer TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `academic_intervention_plans`
Structured, faculty-reviewed academic support plan assigned to a student.
```sql
CREATE TABLE academic_intervention_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES student_academic_profiles(id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES academic_subjects(id) ON DELETE CASCADE,
    topic_id UUID REFERENCES syllabus_topics(id) ON DELETE SET NULL,
    learning_outcome_id UUID REFERENCES learning_outcomes(id) ON DELETE SET NULL,
    recommendation_id UUID REFERENCES academic_intervention_recommendations(id) ON DELETE SET NULL,
    plan_title VARCHAR(255) NOT NULL,
    learning_objective TEXT NOT NULL,
    plan_status VARCHAR(30) NOT NULL DEFAULT 'DRAFT',
    assigned_faculty_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    reviewed_by_faculty_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMPTZ,
    faculty_review_notes TEXT,
    start_date TIMESTAMPTZ,
    target_completion_date TIMESTAMPTZ,
    actual_completion_date TIMESTAMPTZ,
    expected_outcome_evidence TEXT,
    scientific_disclaimer TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `academic_intervention_actions`
Individual actionable tasks within an academic intervention plan.
```sql
CREATE TABLE academic_intervention_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES academic_intervention_plans(id) ON DELETE CASCADE,
    action_order INTEGER NOT NULL DEFAULT 1,
    action_title VARCHAR(255) NOT NULL,
    action_type VARCHAR(50) NOT NULL DEFAULT 'TARGETED_REVISION',
    instructions TEXT NOT NULL,
    resource_references JSONB NOT NULL DEFAULT '[]'::jsonb,
    estimated_effort_hours FLOAT NOT NULL DEFAULT 1.0,
    due_date TIMESTAMPTZ,
    action_status VARCHAR(30) NOT NULL DEFAULT 'PROPOSED',
    student_completion_notes TEXT,
    student_submission_url VARCHAR(512),
    submitted_at TIMESTAMPTZ,
    faculty_feedback TEXT,
    verified_by_faculty_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `intervention_progress_events`
Append-only chronological audit ledger for all plan and action status changes.
```sql
CREATE TABLE intervention_progress_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES academic_intervention_plans(id) ON DELETE CASCADE,
    action_id UUID REFERENCES academic_intervention_actions(id) ON DELETE SET NULL,
    actor_profile_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL,
    previous_status VARCHAR(30),
    new_status VARCHAR(30) NOT NULL,
    event_notes TEXT,
    event_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `intervention_outcome_observations`
Post-intervention observational evidence linking subsequent assessment or mastery results.
```sql
CREATE TABLE intervention_outcome_observations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES academic_intervention_plans(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES student_academic_profiles(id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES academic_subjects(id) ON DELETE CASCADE,
    topic_id UUID REFERENCES syllabus_topics(id) ON DELETE SET NULL,
    learning_outcome_id UUID REFERENCES learning_outcomes(id) ON DELETE SET NULL,
    baseline_mastery_percentage FLOAT,
    followup_assessment_id UUID REFERENCES academic_assessments(id) ON DELETE SET NULL,
    followup_score_obtained FLOAT,
    followup_maximum_marks FLOAT,
    followup_mastery_percentage FLOAT,
    observation_notes TEXT,
    scientific_disclaimer TEXT NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```
```
```
