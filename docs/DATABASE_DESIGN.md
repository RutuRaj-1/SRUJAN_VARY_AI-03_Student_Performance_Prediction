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
