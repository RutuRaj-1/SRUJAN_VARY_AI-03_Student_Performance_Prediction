# MASTERY — Role-Based Dashboard Access Control
## Authorization Matrix, Tenant Scoping & Firewall Policies

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Track:** AI, CyberSecurity and Digital Trust  
**Phase:** 10/11 — Unified Intelligence Dashboard & Cross-Module Integration  

---

## 1. Access Control Matrix

| Endpoint Group | `STUDENT` | `FACULTY` | `INSTITUTION_ADMIN` | `PLACEMENT_OFFICER` | `SUPER_ADMIN` |
|---|---|---|---|---|---|
| **`/api/v1/dashboard/student/overview`** | **Allowed** (Self Only) | **Allowed** (Assigned) | **Allowed** (Tenant) | **BLOCKED (403)** | **Allowed** |
| **`/api/v1/dashboard/student/academic-summary`** | **Allowed** (Self Only) | **Allowed** (Assigned) | **Allowed** (Tenant) | **BLOCKED (403)** | **Allowed** |
| **`/api/v1/dashboard/student/mastery-summary`** | **Allowed** (Self Only) | **Allowed** (Assigned) | **Allowed** (Tenant) | **BLOCKED (403)** | **Allowed** |
| **`/api/v1/dashboard/student/risk-summary`** | **Allowed** (Self Only) | **Allowed** (Assigned) | **Allowed** (Tenant) | **BLOCKED (403)** | **Allowed** |
| **`/api/v1/dashboard/student/intervention-summary`** | **Allowed** (Self Only) | **Allowed** (Assigned) | **Allowed** (Tenant) | **BLOCKED (403)** | **Allowed** |
| **`/api/v1/dashboard/student/career-summary`** | **Allowed** (Self Only) | **Allowed** (Assigned) | **Allowed** (Tenant) | **Allowed** | **Allowed** |
| **`/api/v1/dashboard/faculty/overview`** | **BLOCKED (403)** | **Allowed** (Tenant) | **Allowed** (Tenant) | **BLOCKED (403)** | **Allowed** |
| **`/api/v1/dashboard/faculty/verification-queue`** | **BLOCKED (403)** | **Allowed** (Tenant) | **Allowed** (Tenant) | **BLOCKED (403)** | **Allowed** |
| **`/api/v1/dashboard/faculty/cohort-risk`** | **BLOCKED (403)** | **Allowed** (Tenant) | **Allowed** (Tenant) | **BLOCKED (403)** | **Allowed** |
| **`/api/v1/dashboard/institution/overview`** | **BLOCKED (403)** | **BLOCKED (403)** | **Allowed** (Tenant) | **BLOCKED (403)** | **Allowed** |
| **`/api/v1/dashboard/institution/*`** | **BLOCKED (403)** | **BLOCKED (403)** | **Allowed** (Tenant) | **BLOCKED (403)** | **Allowed** |
| **`/api/v1/dashboard/placement/overview`** | **BLOCKED (403)** | **Allowed** | **Allowed** | **Allowed** | **Allowed** |
| **`/api/v1/dashboard/placement/*`** | **BLOCKED (403)** | **Allowed** | **Allowed** | **Allowed** | **Allowed** |
| **`/api/v1/dashboard/admin/overview`** | **BLOCKED (403)** | **BLOCKED (403)** | **Allowed** | **BLOCKED (403)** | **Allowed** |
| **`/api/v1/dashboard/admin/*`** | **BLOCKED (403)** | **BLOCKED (403)** | **Allowed** | **BLOCKED (403)** | **Allowed** |

---

## 2. Policy Enforcements

### 2.1 Student Self-Ownership
When a user authenticated as `STUDENT` requests `/api/v1/dashboard/student/overview`, the backend enforces:
```python
if current_user.role == UserRole.STUDENT:
    if student_id:
        profile = db.query(StudentAcademicProfile).filter(StudentAcademicProfile.id == student_id).first()
        if not profile or profile.profile_id != user_uuid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students may only access their own dashboard."
            )
```
Students cannot override query parameters to view peer academic records, risk scores, or intervention actions.

### 2.2 Placement Officer Firewall (Defense-in-Depth)
Placement Officers are legally and ethically separated from diagnostic risk predictions and remediation records:
- The endpoint helper `_assert_not_placement_officer(current_user)` returns `HTTP 403 Forbidden` if a Placement Officer attempts to access `/api/v1/dashboard/student/overview`, `/api/v1/dashboard/student/risk-summary`, or `/api/v1/dashboard/student/intervention-summary`.
- Database Row-Level Security (RLS) on `academic_risk_predictions` and `academic_intervention_plans` permits access only to authorized faculty and institutional staff.

### 2.3 Tenant Isolation
All institution administrators, faculty, and students have their queries strictly scoped by `institution_id`. Super Admins can supply an optional `institution_id` parameter to inspect specific partner institutions.
