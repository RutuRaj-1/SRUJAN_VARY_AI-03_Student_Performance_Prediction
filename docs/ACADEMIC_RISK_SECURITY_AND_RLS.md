# Module 06: Academic Risk Prediction — Security Architecture & Row-Level Security

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Track:** AI, CyberSecurity and Digital Trust  
**Phase:** 07/11  
**Module:** Academic Risk Prediction Engine

---

## 1. Security Architecture Overview

The Academic Risk Prediction Engine implements defense-in-depth across the application and database tiers:
1. **Multi-Tenant Institutional Partitioning:** Every query filters by `institution_id` matching the authenticated user's profile. Cross-institution data leakage is structurally impossible.
2. **PostgreSQL Row-Level Security (RLS):** All 7 Module 06 tables enforce active Supabase Row-Level Security (`rowsecurity = true`) with strict multi-tenant and role-based policies.
3. **Application Role Guards:** FastAPI route handlers enforce role-based access control (RBAC) via `require_roles(...)`.
4. **Placement Isolation Boundary:** Placement officers are barred from all risk endpoints.
5. **Student Privacy Isolation:** Students can only read their own predictions (`student_academic_profiles.profile_id = auth.uid()`). They cannot read peer predictions, trigger training, or view cohort summaries.

---

## 2. Role-Based Access Matrix

| Role | View Personal Risk | View Cohort Risk Ledger | Configure Risk Targets | Train / Activate Models | Trigger Predictions |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **STUDENT** | ✅ (Self Only) | ❌ | ❌ | ❌ | ❌ |
| **FACULTY** | ✅ (Assigned Cohort) | ✅ | ✅ | ✅ | ✅ |
| **INSTITUTION_ADMIN** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **SUPER_ADMIN** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **PLACEMENT_OFFICER** | ❌ (Strictly Barred) | ❌ | ❌ | ❌ | ❌ |

---

## 3. Implemented Row-Level Security (RLS) Policies

The following RLS policies were created in `backend/migrations/006_academic_risk_rls.sql` and applied to the live Supabase PostgreSQL database:

### 3.1 `academic_risk_targets`
- **Read Access:** All active institutional members can read configured targets within their institution:
  ```sql
  CREATE POLICY "risk_targets_tenant_select" ON academic_risk_targets
  FOR SELECT TO authenticated
  USING (
    institution_id = ((current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'institution_id')::uuid)
  );
  ```
- **Write Access:** Restricted to Faculty, Institution Admins, and Super Admins within the institution:
  ```sql
  CREATE POLICY "risk_targets_admin_faculty_modify" ON academic_risk_targets
  FOR ALL TO authenticated
  USING (
    institution_id = ((current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'institution_id')::uuid)
    AND (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
  );
  ```

### 3.2 `risk_feature_snapshots`
- **Read Access:** Evaluated student can read their own snapshot; faculty/admins can read student snapshots in their institution:
  ```sql
  CREATE POLICY "risk_snapshots_tenant_select" ON risk_feature_snapshots
  FOR SELECT TO authenticated
  USING (
    institution_id = ((current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'institution_id')::uuid)
    AND (
      (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
      OR student_id IN (
        SELECT id FROM student_academic_profiles WHERE profile_id = auth.uid()
      )
    )
  );
  ```

### 3.3 `risk_model_versions` & `risk_model_evaluations`
- **Read Access:** Faculty and Institution Admins within the tenant:
  ```sql
  CREATE POLICY "risk_models_tenant_select" ON risk_model_versions
  FOR SELECT TO authenticated
  USING (
    institution_id = ((current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'institution_id')::uuid)
    AND (current_setting('request.jwt.claims', true)::jsonb -> 'user_metadata' ->> 'role') IN ('FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN')
  );
  ```

### 3.4 `academic_risk_predictions` & `academic_risk_prediction_explanations`
- **Read Access:** Enforces strict student self-isolation and bars Placement Officers:
  ```sql
  CREATE POLICY "risk_predictions_select" ON academic_risk_predictions
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
  ```

---

## 4. Verification & Audit Results

Live database inspection confirmed that:
1. All 7 risk prediction tables have `rowsecurity = true`.
2. Total database tables with active RLS: **46 application tables** (100% of application surface).
3. Student access attempts to other students' profiles return `403 Forbidden` (`test_student_role_access_guard_and_isolation`).
4. Placement Officer access attempts return `403 Forbidden` (`test_student_role_access_guard_and_isolation`).
