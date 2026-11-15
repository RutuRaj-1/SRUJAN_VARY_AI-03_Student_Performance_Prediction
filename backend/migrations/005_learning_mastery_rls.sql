-- =========================================================================
-- MASTERY — Module 05: Learning Mastery & Performance Analytics RLS Policies
-- Migration: 005_learning_mastery_rls.sql
-- Description: Enable RLS and define tenant isolation for Mastery Analytics
-- =========================================================================

-- 1. Enable RLS on all Phase 06 entities
ALTER TABLE mastery_analysis_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE mastery_evidence_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE topic_mastery_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_outcome_attainment_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_gap_findings ENABLE ROW LEVEL SECURITY;

-- 2. Define tenant isolation policies for mastery_analysis_jobs
CREATE POLICY "Institutions can view own mastery analysis jobs"
    ON mastery_analysis_jobs FOR SELECT
    USING (
        institution_id IN (
            SELECT institution_id FROM profiles WHERE id = auth.uid()
        )
    );

CREATE POLICY "Faculty and Admins can create mastery analysis jobs"
    ON mastery_analysis_jobs FOR INSERT
    WITH CHECK (
        institution_id IN (
            SELECT institution_id FROM profiles 
            WHERE id = auth.uid() 
            AND role IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
        )
    );

CREATE POLICY "Faculty and Admins can update mastery analysis jobs"
    ON mastery_analysis_jobs FOR UPDATE
    USING (
        institution_id IN (
            SELECT institution_id FROM profiles 
            WHERE id = auth.uid() 
            AND role IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
        )
    );

-- 3. Define tenant isolation policies for mastery_evidence_records
CREATE POLICY "Users can view eligible mastery evidence records in own institution"
    ON mastery_evidence_records FOR SELECT
    USING (
        institution_id IN (
            SELECT institution_id FROM profiles WHERE id = auth.uid()
        )
        AND (
            -- Students can only view their own evidence
            (EXISTS (
                SELECT 1 FROM student_academic_profiles 
                WHERE id = mastery_evidence_records.student_id 
                AND profile_id = auth.uid()
            ))
            -- Faculty/Admins can view institution evidence
            OR (EXISTS (
                SELECT 1 FROM profiles 
                WHERE id = auth.uid() 
                AND role IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
            ))
        )
    );

CREATE POLICY "Faculty and Admins can insert mastery evidence records"
    ON mastery_evidence_records FOR INSERT
    WITH CHECK (
        institution_id IN (
            SELECT institution_id FROM profiles 
            WHERE id = auth.uid() 
            AND role IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
        )
    );

-- 4. Define tenant isolation policies for topic_mastery_results
CREATE POLICY "Users can view topic mastery results"
    ON topic_mastery_results FOR SELECT
    USING (
        institution_id IN (
            SELECT institution_id FROM profiles WHERE id = auth.uid()
        )
        AND (
            (EXISTS (
                SELECT 1 FROM student_academic_profiles 
                WHERE id = topic_mastery_results.student_id 
                AND profile_id = auth.uid()
            ))
            OR (EXISTS (
                SELECT 1 FROM profiles 
                WHERE id = auth.uid() 
                AND role IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
            ))
        )
    );

CREATE POLICY "Faculty and Admins can manage topic mastery results"
    ON topic_mastery_results FOR ALL
    USING (
        institution_id IN (
            SELECT institution_id FROM profiles 
            WHERE id = auth.uid() 
            AND role IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
        )
    );

-- 5. Define tenant isolation policies for learning_outcome_attainment_results
CREATE POLICY "Users can view outcome attainment results"
    ON learning_outcome_attainment_results FOR SELECT
    USING (
        institution_id IN (
            SELECT institution_id FROM profiles WHERE id = auth.uid()
        )
        AND (
            (EXISTS (
                SELECT 1 FROM student_academic_profiles 
                WHERE id = learning_outcome_attainment_results.student_id 
                AND profile_id = auth.uid()
            ))
            OR (EXISTS (
                SELECT 1 FROM profiles 
                WHERE id = auth.uid() 
                AND role IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
            ))
        )
    );

CREATE POLICY "Faculty and Admins can manage outcome attainment results"
    ON learning_outcome_attainment_results FOR ALL
    USING (
        institution_id IN (
            SELECT institution_id FROM profiles 
            WHERE id = auth.uid() 
            AND role IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
        )
    );

-- 6. Define tenant isolation policies for learning_gap_findings
CREATE POLICY "Users can view learning gap findings"
    ON learning_gap_findings FOR SELECT
    USING (
        institution_id IN (
            SELECT institution_id FROM profiles WHERE id = auth.uid()
        )
        AND (
            (EXISTS (
                SELECT 1 FROM student_academic_profiles 
                WHERE id = learning_gap_findings.student_id 
                AND profile_id = auth.uid()
            ))
            OR (EXISTS (
                SELECT 1 FROM profiles 
                WHERE id = auth.uid() 
                AND role IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
            ))
        )
    );

CREATE POLICY "Faculty and Admins can manage learning gap findings"
    ON learning_gap_findings FOR ALL
    USING (
        institution_id IN (
            SELECT institution_id FROM profiles 
            WHERE id = auth.uid() 
            AND role IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
        )
    );
