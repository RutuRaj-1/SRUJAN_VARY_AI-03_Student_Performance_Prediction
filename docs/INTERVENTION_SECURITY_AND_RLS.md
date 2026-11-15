# Module 07: Academic Interventions — Security Architecture & Row-Level Security

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Track:** AI, CyberSecurity and Digital Trust  
**Phase:** 08/11  
**Module:** 07 — Personalized Academic Intervention Engine  

---

## 1. Security Architecture & Multi-Tenant Partitioning

Module 07 enforces strict multi-tenant isolation and role-based permissions across both FastAPI application guards and PostgreSQL Row-Level Security (RLS):

1. **Tenant Isolation:** Every table features an indexed `institution_id` column mapped to `institutions.id`. Cross-institutional data access is impossible.
2. **PostgreSQL Row-Level Security (RLS):** All 6 Module 07 tables enforce active Supabase RLS (`rowsecurity = true`).
3. **Student Privacy Boundary:** Students can only read and interact with their own assigned intervention plans (`student_academic_profiles.profile_id = auth.uid()`).
4. **Placement Officer Quarantine (§ 4.2 Ethical AI Charter):** Placement Officers are strictly barred from accessing academic intervention blueprints, recommendations, plans, or outcomes to eliminate recruitment bias.
5. **Human-in-the-Loop Safeguard:** Unreviewed internal draft plans (`DRAFT`, `PENDING_REVIEW`) are hidden from students until authorized by faculty (`plan_status IN ('APPROVED', 'ACTIVE', 'COMPLETED')`).

---

## 2. Role-Based Access Matrix

| Role | View Templates | Generate / View Recommendations | Create / Review Plans | Assign Plans | Submit Action Evidence | Verify Action Completion | View Outcomes |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **STUDENT** | ✅ | ✅ (Self Only) | ❌ | ❌ | ✅ (Self Only) | ❌ | ✅ (Self Only) |
| **FACULTY** | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| **INSTITUTION_ADMIN** | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| **SUPER_ADMIN** | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| **PLACEMENT_OFFICER** | ❌ (Strictly Barred) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 3. Row-Level Security Policies (`007_academic_interventions_rls.sql`)

The following policies were applied to the live Supabase PostgreSQL database:

### 3.1 `academic_intervention_plans`
```sql
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
```

### 3.2 `academic_intervention_actions`
```sql
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
```

---

## 4. Live Database Verification Results

Live PostgreSQL catalog queries confirmed:
- Total tables in public schema: **53**
- Tables with Row-Level Security enabled: **52** (100% of all application tables; the remaining 1 table is `alembic_version`).
- Multi-role permission tests (`test_security_rbac_and_placement_officer_boundary`):
  - Student A accessing Student B's plan $\rightarrow$ `403 Forbidden`
  - Placement Officer accessing intervention routes $\rightarrow$ `403 Forbidden`
  - Student attempting to approve plan $\rightarrow$ `403 Forbidden`
