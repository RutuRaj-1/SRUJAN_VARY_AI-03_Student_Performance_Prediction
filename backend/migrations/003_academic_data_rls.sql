-- ====================================================================
-- MASTERY Platform: Row-Level Security (RLS) for Module 03
-- Academic Data Intelligence Hub
-- ====================================================================

-- 1. Enable RLS on all Module 03 tables
ALTER TABLE public.student_academic_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.student_subject_enrollments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.academic_assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.student_assessment_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.student_attendance_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.academic_import_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.academic_import_errors ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.academic_data_quality_findings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.academic_record_audits ENABLE ROW LEVEL SECURITY;

-- 2. Student Academic Profiles RLS
DROP POLICY IF EXISTS "Students can read own academic profile" ON public.student_academic_profiles;
CREATE POLICY "Students can read own academic profile"
  ON public.student_academic_profiles FOR SELECT TO authenticated
  USING (
    profile_id = auth.uid()
    OR EXISTS (
      SELECT 1 FROM public.institution_memberships
      WHERE user_id = auth.uid()
        AND institution_id = student_academic_profiles.institution_id
        AND membership_status = 'ACTIVE'
        AND membership_role IN ('ADMIN', 'FACULTY')
    )
    OR EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN')
  );

DROP POLICY IF EXISTS "Staff manage student academic profiles" ON public.student_academic_profiles;
CREATE POLICY "Staff manage student academic profiles"
  ON public.student_academic_profiles FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.institution_memberships
      WHERE user_id = auth.uid()
        AND institution_id = student_academic_profiles.institution_id
        AND membership_status = 'ACTIVE'
        AND membership_role IN ('ADMIN', 'FACULTY')
    )
    OR EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN')
  );

-- 3. Academic Assessments & Performance Records RLS
DROP POLICY IF EXISTS "Institution members read assessments" ON public.academic_assessments;
CREATE POLICY "Institution members read assessments"
  ON public.academic_assessments FOR SELECT TO authenticated
  USING (
    institution_id IN (
      SELECT institution_id FROM public.institution_memberships
      WHERE user_id = auth.uid() AND membership_status = 'ACTIVE'
    )
    OR EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN')
  );

DROP POLICY IF EXISTS "Staff manage academic assessments" ON public.academic_assessments;
CREATE POLICY "Staff manage academic assessments"
  ON public.academic_assessments FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.institution_memberships
      WHERE user_id = auth.uid()
        AND institution_id = academic_assessments.institution_id
        AND membership_status = 'ACTIVE'
        AND membership_role IN ('ADMIN', 'FACULTY')
    )
    OR EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN')
  );

DROP POLICY IF EXISTS "Students read own performance records" ON public.student_assessment_records;
CREATE POLICY "Students read own performance records"
  ON public.student_assessment_records FOR SELECT TO authenticated
  USING (
    student_id IN (SELECT id FROM public.student_academic_profiles WHERE profile_id = auth.uid())
    OR EXISTS (
      SELECT 1 FROM public.institution_memberships
      WHERE user_id = auth.uid()
        AND institution_id = student_assessment_records.institution_id
        AND membership_status = 'ACTIVE'
        AND membership_role IN ('ADMIN', 'FACULTY')
    )
    OR EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN')
  );

DROP POLICY IF EXISTS "Staff manage student assessment records" ON public.student_assessment_records;
CREATE POLICY "Staff manage student assessment records"
  ON public.student_assessment_records FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.institution_memberships
      WHERE user_id = auth.uid()
        AND institution_id = student_assessment_records.institution_id
        AND membership_status = 'ACTIVE'
        AND membership_role IN ('ADMIN', 'FACULTY')
    )
    OR EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN')
  );

-- 4. Attendance Records RLS
DROP POLICY IF EXISTS "Students read own attendance records" ON public.student_attendance_records;
CREATE POLICY "Students read own attendance records"
  ON public.student_attendance_records FOR SELECT TO authenticated
  USING (
    student_id IN (SELECT id FROM public.student_academic_profiles WHERE profile_id = auth.uid())
    OR EXISTS (
      SELECT 1 FROM public.institution_memberships
      WHERE user_id = auth.uid()
        AND institution_id = student_attendance_records.institution_id
        AND membership_status = 'ACTIVE'
        AND membership_role IN ('ADMIN', 'FACULTY')
    )
    OR EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN')
  );

DROP POLICY IF EXISTS "Staff manage student attendance records" ON public.student_attendance_records;
CREATE POLICY "Staff manage student attendance records"
  ON public.student_attendance_records FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.institution_memberships
      WHERE user_id = auth.uid()
        AND institution_id = student_attendance_records.institution_id
        AND membership_status = 'ACTIVE'
        AND membership_role IN ('ADMIN', 'FACULTY')
    )
    OR EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN')
  );

-- 5. Import Jobs & Errors RLS
DROP POLICY IF EXISTS "Staff manage academic import jobs" ON public.academic_import_jobs;
CREATE POLICY "Staff manage academic import jobs"
  ON public.academic_import_jobs FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.institution_memberships
      WHERE user_id = auth.uid()
        AND institution_id = academic_import_jobs.institution_id
        AND membership_status = 'ACTIVE'
        AND membership_role IN ('ADMIN', 'FACULTY')
    )
    OR EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN')
  );

-- 6. Quality Findings & Audit Logs RLS
DROP POLICY IF EXISTS "Staff read academic quality findings" ON public.academic_data_quality_findings;
CREATE POLICY "Staff read academic quality findings"
  ON public.academic_data_quality_findings FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.institution_memberships
      WHERE user_id = auth.uid()
        AND institution_id = academic_data_quality_findings.institution_id
        AND membership_status = 'ACTIVE'
        AND membership_role IN ('ADMIN', 'FACULTY')
    )
    OR EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN')
  );

DROP POLICY IF EXISTS "Staff read academic record audits" ON public.academic_record_audits;
CREATE POLICY "Staff read academic record audits"
  ON public.academic_record_audits FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.institution_memberships
      WHERE user_id = auth.uid()
        AND institution_id = academic_record_audits.institution_id
        AND membership_status = 'ACTIVE'
        AND membership_role IN ('ADMIN', 'FACULTY')
    )
    OR EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN')
  );
