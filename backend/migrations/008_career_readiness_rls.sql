-- =========================================================================
-- MASTERY: Module 08 — Career Readiness & Industry Skill Gap Intelligence
-- Supabase PostgreSQL Row-Level Security (RLS) Policies
-- Migration: 008_career_readiness_rls.sql
-- =========================================================================

-- Enable RLS across all 5 Phase 09 tables
ALTER TABLE student_project_evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_competency_evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE career_readiness_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE career_skill_gap_findings ENABLE ROW LEVEL SECURITY;
ALTER TABLE career_development_recommendations ENABLE ROW LEVEL SECURITY;

-- -------------------------------------------------------------------------
-- 1. student_project_evidence
-- -------------------------------------------------------------------------
DROP POLICY IF EXISTS "project_evidence_tenant_select" ON student_project_evidence;
CREATE POLICY "project_evidence_tenant_select" ON student_project_evidence
FOR SELECT TO authenticated
USING (
    institution_id = ((current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'institution_id')::uuid)
    AND (
        (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
        OR (
            (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') = 'PLACEMENT_OFFICER'
            AND verification_status = 'VERIFIED'
        )
        OR (
            (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') = 'STUDENT'
            AND student_id IN (
                SELECT id FROM student_academic_profiles WHERE profile_id = auth.uid()
            )
        )
    )
);

DROP POLICY IF EXISTS "project_evidence_student_insert" ON student_project_evidence;
CREATE POLICY "project_evidence_student_insert" ON student_project_evidence
FOR INSERT TO authenticated
WITH CHECK (
    institution_id = ((current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'institution_id')::uuid)
    AND (
        (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
        OR (
            (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') = 'STUDENT'
            AND student_id IN (
                SELECT id FROM student_academic_profiles WHERE profile_id = auth.uid()
            )
        )
    )
);

DROP POLICY IF EXISTS "project_evidence_modify" ON student_project_evidence;
CREATE POLICY "project_evidence_modify" ON student_project_evidence
FOR UPDATE TO authenticated
USING (
    institution_id = ((current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'institution_id')::uuid)
    AND (
        (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
        OR (
            (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') = 'STUDENT'
            AND student_id IN (
                SELECT id FROM student_academic_profiles WHERE profile_id = auth.uid()
            )
            AND verification_status = 'PENDING_REVIEW'
        )
    )
);

-- -------------------------------------------------------------------------
-- 2. student_competency_evidence
-- -------------------------------------------------------------------------
DROP POLICY IF EXISTS "competency_evidence_tenant_select" ON student_competency_evidence;
CREATE POLICY "competency_evidence_tenant_select" ON student_competency_evidence
FOR SELECT TO authenticated
USING (
    institution_id = ((current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'institution_id')::uuid)
    AND (
        (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN', 'PLACEMENT_OFFICER')
        OR (
            (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') = 'STUDENT'
            AND student_id IN (
                SELECT id FROM student_academic_profiles WHERE profile_id = auth.uid()
            )
        )
    )
);

DROP POLICY IF EXISTS "competency_evidence_staff_modify" ON student_competency_evidence;
CREATE POLICY "competency_evidence_staff_modify" ON student_competency_evidence
FOR ALL TO authenticated
USING (
    institution_id = ((current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'institution_id')::uuid)
    AND (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
);

-- -------------------------------------------------------------------------
-- 3. career_readiness_analyses
-- -------------------------------------------------------------------------
DROP POLICY IF EXISTS "readiness_analyses_tenant_select" ON career_readiness_analyses;
CREATE POLICY "readiness_analyses_tenant_select" ON career_readiness_analyses
FOR SELECT TO authenticated
USING (
    institution_id = ((current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'institution_id')::uuid)
    AND (
        (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN', 'PLACEMENT_OFFICER')
        OR (
            (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') = 'STUDENT'
            AND student_id IN (
                SELECT id FROM student_academic_profiles WHERE profile_id = auth.uid()
            )
        )
    )
);

DROP POLICY IF EXISTS "readiness_analyses_staff_modify" ON career_readiness_analyses;
CREATE POLICY "readiness_analyses_staff_modify" ON career_readiness_analyses
FOR ALL TO authenticated
USING (
    institution_id = ((current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'institution_id')::uuid)
    AND (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
);

-- -------------------------------------------------------------------------
-- 4. career_skill_gap_findings
-- -------------------------------------------------------------------------
DROP POLICY IF EXISTS "skill_gaps_tenant_select" ON career_skill_gap_findings;
CREATE POLICY "skill_gaps_tenant_select" ON career_skill_gap_findings
FOR SELECT TO authenticated
USING (
    institution_id = ((current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'institution_id')::uuid)
    AND (
        (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN', 'PLACEMENT_OFFICER')
        OR (
            (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') = 'STUDENT'
            AND student_id IN (
                SELECT id FROM student_academic_profiles WHERE profile_id = auth.uid()
            )
        )
    )
);

DROP POLICY IF EXISTS "skill_gaps_staff_modify" ON career_skill_gap_findings;
CREATE POLICY "skill_gaps_staff_modify" ON career_skill_gap_findings
FOR ALL TO authenticated
USING (
    institution_id = ((current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'institution_id')::uuid)
    AND (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
);

-- -------------------------------------------------------------------------
-- 5. career_development_recommendations
-- -------------------------------------------------------------------------
DROP POLICY IF EXISTS "career_recs_tenant_select" ON career_development_recommendations;
CREATE POLICY "career_recs_tenant_select" ON career_development_recommendations
FOR SELECT TO authenticated
USING (
    institution_id = ((current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'institution_id')::uuid)
    AND (
        (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN', 'PLACEMENT_OFFICER')
        OR (
            (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') = 'STUDENT'
            AND student_id IN (
                SELECT id FROM student_academic_profiles WHERE profile_id = auth.uid()
            )
        )
    )
);

DROP POLICY IF EXISTS "career_recs_modify" ON career_development_recommendations;
CREATE POLICY "career_recs_modify" ON career_development_recommendations
FOR ALL TO authenticated
USING (
    institution_id = ((current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'institution_id')::uuid)
    AND (
        (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
        OR (
            (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') = 'STUDENT'
            AND student_id IN (
                SELECT id FROM student_academic_profiles WHERE profile_id = auth.uid()
            )
        )
    )
);
