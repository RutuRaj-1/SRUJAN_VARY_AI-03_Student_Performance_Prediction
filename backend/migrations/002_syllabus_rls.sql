-- ====================================================================
-- MASTERY Platform: Row-Level Security (RLS) for Module 02
-- Syllabus & Competency Intelligence Engine
-- ====================================================================

-- 1. Enable RLS on all Module 02 tables
ALTER TABLE public.academic_programs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.academic_subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.syllabus_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.syllabus_units ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.syllabus_topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.learning_outcomes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.competencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subject_competency_mappings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.industry_role_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.industry_competency_requirements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.curriculum_gap_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.syllabus_review_history ENABLE ROW LEVEL SECURITY;

-- 2. Reference Data: Industry Roles & Requirements (Readable by all authenticated)
DROP POLICY IF EXISTS "Industry roles readable by authenticated" ON public.industry_role_profiles;
CREATE POLICY "Industry roles readable by authenticated"
  ON public.industry_role_profiles FOR SELECT TO authenticated USING (true);

DROP POLICY IF EXISTS "Industry requirements readable by authenticated" ON public.industry_competency_requirements;
CREATE POLICY "Industry requirements readable by authenticated"
  ON public.industry_competency_requirements FOR SELECT TO authenticated USING (true);

-- 3. Academic Programs & Subjects (Readable by members of the institution)
DROP POLICY IF EXISTS "Programs readable by institution members" ON public.academic_programs;
CREATE POLICY "Programs readable by institution members"
  ON public.academic_programs FOR SELECT TO authenticated
  USING (
    institution_id IN (
      SELECT institution_id FROM public.institution_memberships
      WHERE user_id = auth.uid() AND membership_status = 'ACTIVE'
    )
    OR EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN')
  );

DROP POLICY IF EXISTS "Subjects readable by institution members" ON public.academic_subjects;
CREATE POLICY "Subjects readable by institution members"
  ON public.academic_subjects FOR SELECT TO authenticated
  USING (
    institution_id IN (
      SELECT institution_id FROM public.institution_memberships
      WHERE user_id = auth.uid() AND membership_status = 'ACTIVE'
    )
    OR EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN')
  );

-- 4. Syllabus Documents & Extraction Data
DROP POLICY IF EXISTS "Documents readable by institution members" ON public.syllabus_documents;
CREATE POLICY "Documents readable by institution members"
  ON public.syllabus_documents FOR SELECT TO authenticated
  USING (
    institution_id IN (
      SELECT institution_id FROM public.institution_memberships
      WHERE user_id = auth.uid() AND membership_status = 'ACTIVE'
    )
    OR EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN')
  );

DROP POLICY IF EXISTS "Faculty and admin manage documents" ON public.syllabus_documents;
CREATE POLICY "Faculty and admin manage documents"
  ON public.syllabus_documents FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.institution_memberships
      WHERE user_id = auth.uid()
        AND institution_id = syllabus_documents.institution_id
        AND membership_status = 'ACTIVE'
        AND membership_role IN ('ADMIN', 'FACULTY')
    )
    OR EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN')
  );

-- 5. Competencies (System competencies or institutional competencies)
DROP POLICY IF EXISTS "Competencies readable by authenticated" ON public.competencies;
CREATE POLICY "Competencies readable by authenticated"
  ON public.competencies FOR SELECT TO authenticated
  USING (
    institution_id IS NULL
    OR institution_id IN (
      SELECT institution_id FROM public.institution_memberships
      WHERE user_id = auth.uid() AND membership_status = 'ACTIVE'
    )
    OR EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'SUPER_ADMIN')
  );
