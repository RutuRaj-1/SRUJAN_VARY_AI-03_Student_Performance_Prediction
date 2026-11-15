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
