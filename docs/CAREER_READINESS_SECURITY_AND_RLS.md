# MASTERY — Career Readiness Security & Row-Level Security (RLS)
## Multi-Tenant Authorization, Data Privacy & Placement Officer Firewall

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Module:** Module 08 — Career Readiness & Industry Skill Gap Intelligence  

---

## 1. Role-Based Access Control (RBAC) Matrix

| Operation / Entity | SUPER_ADMIN | INSTITUTION_ADMIN | FACULTY | STUDENT | PLACEMENT_OFFICER |
|---|---|---|---|---|---|
| **Browse Career Roles** | Full Access | Full Access | Full Access | Full Access | Full Access |
| **Create/Update Roles** | Full Access | Institution Scope | Institution Scope | Denied | Denied |
| **Submit Practical Project** | Full Access | Full Access | On-behalf | Own Records Only | Denied |
| **Verify Practical Project** | Full Access | Full Access | Institution Scope | Denied | Denied |
| **Inspect Competency Evidence** | Full Access | Institution Scope | Institution Scope | Own Records Only | Verified / Eligible Scope |
| **Run Readiness Analysis** | Full Access | Institution Scope | Institution Scope | Own Profile Only | Permitted Candidates |
| **View Phase 07 Academic Risk** | Full Access | Institution Scope | Assigned Scope | Own Profile Only | **STRICTLY BLOCKED (403)** |
| **View Phase 08 Interventions** | Full Access | Institution Scope | Assigned Scope | Own Plans Only | **STRICTLY BLOCKED (403)** |

---

## 2. The Placement Officer Firewall

MASTERY implements a defense-in-depth isolation boundary:

1. **API Layer Firewall:**
   Endpoints under `/api/v1/risk/*` and `/api/v1/interventions/*` enforce strict role verification:
   ```python
   if current_user.role == UserRole.PLACEMENT_OFFICER:
       raise HTTPException(
           status_code=status.HTTP_403_FORBIDDEN,
           detail="Placement Officers are strictly barred from accessing student risk intelligence to prevent systemic hiring bias."
       )
   ```
2. **Database RLS Layer:**
   PostgreSQL Row-Level Security policies on `academic_risk_predictions` and `academic_intervention_plans` omit `PLACEMENT_OFFICER` from all `USING` expressions.
3. **Frontend Isolation:**
   The Placement Officer view in the frontend displays a dedicated ethical notice and omits all risk radar gauges or remedial tags.

---

## 3. Database RLS Policy Audit

Row-Level Security is enabled across all Phase 09 tables (`008_career_readiness_rls.sql`):
- `student_project_evidence` (`rowsecurity = true`)
- `student_competency_evidence` (`rowsecurity = true`)
- `career_readiness_analyses` (`rowsecurity = true`)
- `career_skill_gap_findings` (`rowsecurity = true`)
- `career_development_recommendations` (`rowsecurity = true`)

**Total Platform Status:** All 57 application tables in the `public` schema have `rowsecurity = true`.
