-- MASTERY: Module 04 Assessment & Attentiveness Engine Row-Level Security (RLS)
-- Enables RLS and tenant-isolation policies on all Phase 05 assessment tables.

-- 1. Enable RLS on all Phase 05 tables
ALTER TABLE assessment_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessment_question_options ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessment_question_mappings ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessment_learning_outcome_mappings ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessment_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessment_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessment_rubrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessment_rubric_criteria ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessment_rubric_evaluations ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_engagement_events ENABLE ROW LEVEL SECURITY;

-- 2. Drop existing policies if any
DROP POLICY IF EXISTS p_assessment_questions_policy ON assessment_questions;
DROP POLICY IF EXISTS p_assessment_options_policy ON assessment_question_options;
DROP POLICY IF EXISTS p_assessment_question_mappings_policy ON assessment_question_mappings;
DROP POLICY IF EXISTS p_assessment_outcome_mappings_policy ON assessment_learning_outcome_mappings;
DROP POLICY IF EXISTS p_assessment_attempts_policy ON assessment_attempts;
DROP POLICY IF EXISTS p_assessment_responses_policy ON assessment_responses;
DROP POLICY IF EXISTS p_assessment_rubrics_policy ON assessment_rubrics;
DROP POLICY IF EXISTS p_assessment_rubric_criteria_policy ON assessment_rubric_criteria;
DROP POLICY IF EXISTS p_assessment_rubric_eval_policy ON assessment_rubric_evaluations;
DROP POLICY IF EXISTS p_learning_engagement_events_policy ON learning_engagement_events;

-- 3. Create Tenant & Role Scoped Policies

-- assessment_questions
CREATE POLICY p_assessment_questions_policy ON assessment_questions
    FOR ALL
    USING (
        institution_id IN (
            SELECT institution_id FROM profiles WHERE id = auth.uid()
        )
        OR EXISTS (
            SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN'
        )
    );

-- assessment_question_options
CREATE POLICY p_assessment_options_policy ON assessment_question_options
    FOR ALL
    USING (
        question_id IN (
            SELECT id FROM assessment_questions WHERE institution_id IN (
                SELECT institution_id FROM profiles WHERE id = auth.uid()
            )
        )
        OR EXISTS (
            SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN'
        )
    );

-- assessment_question_mappings
CREATE POLICY p_assessment_question_mappings_policy ON assessment_question_mappings
    FOR ALL
    USING (
        assessment_id IN (
            SELECT id FROM academic_assessments WHERE institution_id IN (
                SELECT institution_id FROM profiles WHERE id = auth.uid()
            )
        )
        OR EXISTS (
            SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN'
        )
    );

-- assessment_learning_outcome_mappings
CREATE POLICY p_assessment_outcome_mappings_policy ON assessment_learning_outcome_mappings
    FOR ALL
    USING (
        institution_id IN (
            SELECT institution_id FROM profiles WHERE id = auth.uid()
        )
        OR EXISTS (
            SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN'
        )
    );

-- assessment_attempts
CREATE POLICY p_assessment_attempts_policy ON assessment_attempts
    FOR ALL
    USING (
        institution_id IN (
            SELECT institution_id FROM profiles WHERE id = auth.uid()
        )
        OR EXISTS (
            SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN'
        )
    );

-- assessment_responses
CREATE POLICY p_assessment_responses_policy ON assessment_responses
    FOR ALL
    USING (
        institution_id IN (
            SELECT institution_id FROM profiles WHERE id = auth.uid()
        )
        OR EXISTS (
            SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN'
        )
    );

-- assessment_rubrics
CREATE POLICY p_assessment_rubrics_policy ON assessment_rubrics
    FOR ALL
    USING (
        institution_id IN (
            SELECT institution_id FROM profiles WHERE id = auth.uid()
        )
        OR EXISTS (
            SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN'
        )
    );

-- assessment_rubric_criteria
CREATE POLICY p_assessment_rubric_criteria_policy ON assessment_rubric_criteria
    FOR ALL
    USING (
        rubric_id IN (
            SELECT id FROM assessment_rubrics WHERE institution_id IN (
                SELECT institution_id FROM profiles WHERE id = auth.uid()
            )
        )
        OR EXISTS (
            SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN'
        )
    );

-- assessment_rubric_evaluations
CREATE POLICY p_assessment_rubric_eval_policy ON assessment_rubric_evaluations
    FOR ALL
    USING (
        response_id IN (
            SELECT id FROM assessment_responses WHERE institution_id IN (
                SELECT institution_id FROM profiles WHERE id = auth.uid()
            )
        )
        OR EXISTS (
            SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN'
        )
    );

-- learning_engagement_events
CREATE POLICY p_learning_engagement_events_policy ON learning_engagement_events
    FOR ALL
    USING (
        institution_id IN (
            SELECT institution_id FROM profiles WHERE id = auth.uid()
        )
        OR EXISTS (
            SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN'
        )
    );
