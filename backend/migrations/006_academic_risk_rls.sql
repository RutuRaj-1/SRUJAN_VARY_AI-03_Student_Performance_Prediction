-- =========================================================================
-- Phase 07: Academic Risk Prediction Row-Level Security (RLS)
-- Platform: MASTERY — Beyond Marks. Towards Mastery.
-- =========================================================================

-- 1. Enable and Force RLS on all 7 Phase 07 tables
ALTER TABLE academic_risk_targets ENABLE ROW LEVEL SECURITY;
ALTER TABLE academic_risk_targets FORCE ROW LEVEL SECURITY;

ALTER TABLE risk_feature_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE risk_feature_snapshots FORCE ROW LEVEL SECURITY;

ALTER TABLE risk_model_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE risk_model_versions FORCE ROW LEVEL SECURITY;

ALTER TABLE risk_model_evaluations ENABLE ROW LEVEL SECURITY;
ALTER TABLE risk_model_evaluations FORCE ROW LEVEL SECURITY;

ALTER TABLE academic_risk_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE academic_risk_predictions FORCE ROW LEVEL SECURITY;

ALTER TABLE academic_risk_prediction_explanations ENABLE ROW LEVEL SECURITY;
ALTER TABLE academic_risk_prediction_explanations FORCE ROW LEVEL SECURITY;

ALTER TABLE risk_prediction_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE risk_prediction_jobs FORCE ROW LEVEL SECURITY;

-- =========================================================================
-- 2. Drop existing policies if any
-- =========================================================================
DROP POLICY IF EXISTS super_admin_targets ON academic_risk_targets;
DROP POLICY IF EXISTS inst_admin_faculty_targets ON academic_risk_targets;
DROP POLICY IF EXISTS student_targets ON academic_risk_targets;

DROP POLICY IF EXISTS super_admin_snapshots ON risk_feature_snapshots;
DROP POLICY IF EXISTS inst_admin_faculty_snapshots ON risk_feature_snapshots;
DROP POLICY IF EXISTS student_snapshots ON risk_feature_snapshots;

DROP POLICY IF EXISTS super_admin_models ON risk_model_versions;
DROP POLICY IF EXISTS inst_admin_faculty_models ON risk_model_versions;

DROP POLICY IF EXISTS super_admin_evaluations ON risk_model_evaluations;
DROP POLICY IF EXISTS inst_admin_faculty_evaluations ON risk_model_evaluations;

DROP POLICY IF EXISTS super_admin_predictions ON academic_risk_predictions;
DROP POLICY IF EXISTS inst_admin_faculty_predictions ON academic_risk_predictions;
DROP POLICY IF EXISTS student_predictions ON academic_risk_predictions;

DROP POLICY IF EXISTS super_admin_explanations ON academic_risk_prediction_explanations;
DROP POLICY IF EXISTS inst_admin_faculty_explanations ON academic_risk_prediction_explanations;
DROP POLICY IF EXISTS student_explanations ON academic_risk_prediction_explanations;

DROP POLICY IF EXISTS super_admin_jobs ON risk_prediction_jobs;
DROP POLICY IF EXISTS inst_admin_faculty_jobs ON risk_prediction_jobs;

-- =========================================================================
-- 3. Academic Risk Targets Policies
-- =========================================================================
CREATE POLICY super_admin_targets ON academic_risk_targets
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
            AND profiles.role = 'SUPER_ADMIN'
        )
    );

CREATE POLICY inst_admin_faculty_targets ON academic_risk_targets
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
            AND profiles.role IN ('INSTITUTION_ADMIN', 'FACULTY')
            AND profiles.institution_id = academic_risk_targets.institution_id
        )
    );

CREATE POLICY student_targets ON academic_risk_targets
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
            AND profiles.role = 'STUDENT'
            AND profiles.institution_id = academic_risk_targets.institution_id
        )
    );

-- =========================================================================
-- 4. Risk Feature Snapshots Policies
-- =========================================================================
CREATE POLICY super_admin_snapshots ON risk_feature_snapshots
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
            AND profiles.role = 'SUPER_ADMIN'
        )
    );

CREATE POLICY inst_admin_faculty_snapshots ON risk_feature_snapshots
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
            AND profiles.role IN ('INSTITUTION_ADMIN', 'FACULTY')
            AND profiles.institution_id = risk_feature_snapshots.institution_id
        )
    );

CREATE POLICY student_snapshots ON risk_feature_snapshots
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM student_academic_profiles
            WHERE student_academic_profiles.id = risk_feature_snapshots.student_id
            AND student_academic_profiles.profile_id = auth.uid()
        )
    );

-- =========================================================================
-- 5. Risk Model Versions & Evaluations Policies
-- =========================================================================
CREATE POLICY super_admin_models ON risk_model_versions
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
            AND profiles.role = 'SUPER_ADMIN'
        )
    );

CREATE POLICY inst_admin_faculty_models ON risk_model_versions
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
            AND profiles.role IN ('INSTITUTION_ADMIN', 'FACULTY')
            AND profiles.institution_id = risk_model_versions.institution_id
        )
    );

CREATE POLICY super_admin_evaluations ON risk_model_evaluations
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
            AND profiles.role = 'SUPER_ADMIN'
        )
    );

CREATE POLICY inst_admin_faculty_evaluations ON risk_model_evaluations
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM risk_model_versions
            JOIN profiles ON profiles.institution_id = risk_model_versions.institution_id
            WHERE risk_model_versions.id = risk_model_evaluations.model_version_id
            AND profiles.id = auth.uid()
            AND profiles.role IN ('INSTITUTION_ADMIN', 'FACULTY')
        )
    );

-- =========================================================================
-- 6. Academic Risk Predictions Policies
-- =========================================================================
CREATE POLICY super_admin_predictions ON academic_risk_predictions
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
            AND profiles.role = 'SUPER_ADMIN'
        )
    );

CREATE POLICY inst_admin_faculty_predictions ON academic_risk_predictions
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
            AND profiles.role IN ('INSTITUTION_ADMIN', 'FACULTY')
            AND profiles.institution_id = academic_risk_predictions.institution_id
        )
    );

CREATE POLICY student_predictions ON academic_risk_predictions
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM student_academic_profiles
            WHERE student_academic_profiles.id = academic_risk_predictions.student_id
            AND student_academic_profiles.profile_id = auth.uid()
        )
    );

-- =========================================================================
-- 7. Academic Risk Prediction Explanations Policies
-- =========================================================================
CREATE POLICY super_admin_explanations ON academic_risk_prediction_explanations
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
            AND profiles.role = 'SUPER_ADMIN'
        )
    );

CREATE POLICY inst_admin_faculty_explanations ON academic_risk_prediction_explanations
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM academic_risk_predictions
            JOIN profiles ON profiles.institution_id = academic_risk_predictions.institution_id
            WHERE academic_risk_predictions.id = academic_risk_prediction_explanations.prediction_id
            AND profiles.id = auth.uid()
            AND profiles.role IN ('INSTITUTION_ADMIN', 'FACULTY')
        )
    );

CREATE POLICY student_explanations ON academic_risk_prediction_explanations
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM academic_risk_predictions
            JOIN student_academic_profiles ON student_academic_profiles.id = academic_risk_predictions.student_id
            WHERE academic_risk_predictions.id = academic_risk_prediction_explanations.prediction_id
            AND student_academic_profiles.profile_id = auth.uid()
        )
    );

-- =========================================================================
-- 8. Risk Prediction Jobs Policies
-- =========================================================================
CREATE POLICY super_admin_jobs ON risk_prediction_jobs
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
            AND profiles.role = 'SUPER_ADMIN'
        )
    );

CREATE POLICY inst_admin_faculty_jobs ON risk_prediction_jobs
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
            AND profiles.role IN ('INSTITUTION_ADMIN', 'FACULTY')
            AND profiles.institution_id = risk_prediction_jobs.institution_id
        )
    );
