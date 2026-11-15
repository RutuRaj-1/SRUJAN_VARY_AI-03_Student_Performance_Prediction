-- ====================================================================
-- MASTERY Platform: Row-Level Security (RLS) & Profile Provisioning Trigger
-- Phase 02: Supabase Integration & RBAC
-- ====================================================================

-- 1. Automatic Profile Provisioning Trigger
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (
    id,
    full_name,
    email,
    role,
    account_status,
    created_at,
    updated_at
  )
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'full_name', split_part(NEW.email, '@', 1)),
    NEW.email,
    'STUDENT',
    'PENDING',
    NOW(),
    NOW()
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Bind trigger to auth.users if running in Supabase environment
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'auth') THEN
    DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
    CREATE TRIGGER on_auth_user_created
      AFTER INSERT ON auth.users
      FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
  END IF;
END $$;


-- 2. Enable Row-Level Security
ALTER TABLE public.institutions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.institution_memberships ENABLE ROW LEVEL SECURITY;


-- 3. RLS Policies: institutions
DROP POLICY IF EXISTS "Active institutions readable by authenticated" ON public.institutions;
CREATE POLICY "Active institutions readable by authenticated"
  ON public.institutions
  FOR SELECT
  TO authenticated
  USING (is_active = true);

DROP POLICY IF EXISTS "Super admins manage institutions" ON public.institutions;
CREATE POLICY "Super admins manage institutions"
  ON public.institutions
  FOR ALL
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.profiles
      WHERE id = auth.uid() AND role = 'SUPER_ADMIN'
    )
  );


-- 4. RLS Policies: profiles
DROP POLICY IF EXISTS "Users can read own profile" ON public.profiles;
CREATE POLICY "Users can read own profile"
  ON public.profiles
  FOR SELECT
  TO authenticated
  USING (id = auth.uid());

DROP POLICY IF EXISTS "Users can update own self-profile" ON public.profiles;
CREATE POLICY "Users can update own self-profile"
  ON public.profiles
  FOR UPDATE
  TO authenticated
  USING (id = auth.uid())
  WITH CHECK (id = auth.uid());

DROP POLICY IF EXISTS "Staff can read institution member profiles" ON public.profiles;
CREATE POLICY "Staff can read institution member profiles"
  ON public.profiles
  FOR SELECT
  TO authenticated
  USING (
    institution_id IS NOT NULL AND institution_id IN (
      SELECT institution_id FROM public.institution_memberships
      WHERE user_id = auth.uid()
        AND membership_status = 'ACTIVE'
        AND membership_role IN ('ADMIN', 'FACULTY')
    )
  );


-- 5. RLS Policies: institution_memberships
DROP POLICY IF EXISTS "Users can view own memberships" ON public.institution_memberships;
CREATE POLICY "Users can view own memberships"
  ON public.institution_memberships
  FOR SELECT
  TO authenticated
  USING (user_id = auth.uid());

DROP POLICY IF EXISTS "Institution admins manage memberships" ON public.institution_memberships;
CREATE POLICY "Institution admins manage memberships"
  ON public.institution_memberships
  FOR ALL
  TO authenticated
  USING (
    institution_id IN (
      SELECT institution_id FROM public.institution_memberships
      WHERE user_id = auth.uid()
        AND membership_status = 'ACTIVE'
        AND membership_role = 'ADMIN'
    )
  );
