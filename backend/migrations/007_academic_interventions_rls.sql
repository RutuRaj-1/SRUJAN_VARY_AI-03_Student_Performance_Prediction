-- =========================================================================
-- MASTERY: Module 07 — Personalized Academic Intervention Engine
-- Supabase PostgreSQL Row-Level Security (RLS) Policies
-- Migration: 007_academic_interventions_rls.sql
-- =========================================================================

-- Enable RLS across all 6 Phase 08 tables
ALTER TABLE intervention_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE academic_intervention_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE academic_intervention_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE academic_intervention_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE intervention_progress_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE intervention_outcome_observations ENABLE ROW LEVEL SECURITY;

-- -------------------------------------------------------------------------
-- 1. intervention_templates
-- -------------------------------------------------------------------------
DROP POLICY IF EXISTS "templates_tenant_select" ON intervention_templates;
CREATE POLICY "templates_tenant_select" ON intervention_templates
FOR SELECT TO authenticated
USING (
    institution_id = ((current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'institution_id')::uuid)
);

DROP POLICY IF EXISTS "templates_staff_modify" ON intervention_templates;
CREATE POLICY "templates_staff_modify" ON intervention_templates
FOR ALL TO authenticated
USING (
    institution_id = ((current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'institution_id')::uuid)
    AND (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
);

-- -------------------------------------------------------------------------
-- 2. academic_intervention_recommendations
-- -------------------------------------------------------------------------
DROP POLICY IF EXISTS "recommendations_tenant_select" ON academic_intervention_recommendations;
CREATE POLICY "recommendations_tenant_select" ON academic_intervention_recommendations
FOR SELECT TO authenticated
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

DROP POLICY IF EXISTS "recommendations_staff_modify" ON academic_intervention_recommendations;
CREATE POLICY "recommendations_staff_modify" ON academic_intervention_recommendations
FOR ALL TO authenticated
USING (
    institution_id = ((current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'institution_id')::uuid)
    AND (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
);

-- -------------------------------------------------------------------------
-- 3. academic_intervention_plans
-- -------------------------------------------------------------------------
DROP POLICY IF EXISTS "plans_tenant_select" ON academic_intervention_plans;
CREATE POLICY "plans_tenant_select" ON academic_intervention_plans
FOR SELECT TO authenticated
USING (
    institution_id = ((current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'institution_id')::uuid)
    AND (
        (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
        OR (
            (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') = 'STUDENT'
            AND student_id IN (
                SELECT id FROM student_academic_profiles WHERE profile_id = auth.uid()
            )
            AND plan_status IN ('APPROVED', 'ACTIVE', 'COMPLETED')
        )
    )
);

DROP POLICY IF EXISTS "plans_staff_modify" ON academic_intervention_plans;
CREATE POLICY "plans_staff_modify" ON academic_intervention_plans
FOR ALL TO authenticated
USING (
    institution_id = ((current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'institution_id')::uuid)
    AND (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
);

-- -------------------------------------------------------------------------
-- 4. academic_intervention_actions
-- -------------------------------------------------------------------------
DROP POLICY IF EXISTS "actions_tenant_select" ON academic_intervention_actions;
CREATE POLICY "actions_tenant_select" ON academic_intervention_actions
FOR SELECT TO authenticated
USING (
    institution_id = ((current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'institution_id')::uuid)
    AND (
        (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
        OR (
            (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') = 'STUDENT'
            AND plan_id IN (
                SELECT id FROM academic_intervention_plans
                WHERE student_id IN (SELECT id FROM student_academic_profiles WHERE profile_id = auth.uid())
                AND plan_status IN ('APPROVED', 'ACTIVE', 'COMPLETED')
            )
        )
    )
);

DROP POLICY IF EXISTS "actions_staff_modify" ON academic_intervention_actions;
CREATE POLICY "actions_staff_modify" ON academic_intervention_actions
FOR ALL TO authenticated
USING (
    institution_id = ((current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'institution_id')::uuid)
    AND (
        (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
        OR (
            (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') = 'STUDENT'
            AND plan_id IN (
                SELECT id FROM academic_intervention_plans
                WHERE student_id IN (SELECT id FROM student_academic_profiles WHERE profile_id = auth.uid())
                AND plan_status IN ('APPROVED', 'ACTIVE')
            )
        )
    )
);

-- -------------------------------------------------------------------------
-- 5. intervention_progress_events
-- -------------------------------------------------------------------------
DROP POLICY IF EXISTS "progress_events_tenant_select" ON intervention_progress_events;
CREATE POLICY "progress_events_tenant_select" ON intervention_progress_events
FOR SELECT TO authenticated
USING (
    institution_id = ((current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'institution_id')::uuid)
    AND (
        (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
        OR (
            (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') = 'STUDENT'
            AND plan_id IN (
                SELECT id FROM academic_intervention_plans
                WHERE student_id IN (SELECT id FROM student_academic_profiles WHERE profile_id = auth.uid())
            )
        )
    )
);

DROP POLICY IF EXISTS "progress_events_insert" ON intervention_progress_events;
CREATE POLICY "progress_events_insert" ON intervention_progress_events
FOR INSERT TO authenticated
WITH CHECK (
    institution_id = ((current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'institution_id')::uuid)
);

-- -------------------------------------------------------------------------
-- 6. intervention_outcome_observations
-- -------------------------------------------------------------------------
DROP POLICY IF EXISTS "outcomes_tenant_select" ON intervention_outcome_observations;
CREATE POLICY "outcomes_tenant_select" ON intervention_outcome_observations
FOR SELECT TO authenticated
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

DROP POLICY IF EXISTS "outcomes_staff_modify" ON intervention_outcome_observations;
CREATE POLICY "outcomes_staff_modify" ON intervention_outcome_observations
FOR ALL TO authenticated
USING (
    institution_id = ((current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'institution_id')::uuid)
    AND (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
);
