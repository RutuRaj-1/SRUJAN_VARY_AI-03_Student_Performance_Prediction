# MASTERY — System Architecture Document

**Platform Working Title:** MASTERY — Beyond Marks. Towards Mastery.  
**System Type:** AI-Powered Student Performance Analytics, Academic Risk Prediction, and Career Readiness Platform  
**Architecture Style:** Modular Monolith (Decoupled Frontend & Backend)  
**Phase:** 02/11 — Supabase Integration, Authentication, Role-Based Access Control & Database Foundation  

---

## 1. Executive Summary & Core Philosophy

MASTERY addresses the structural shortcomings of traditional academic performance evaluation in higher education. Institutional marks (internal exam grades, attendance percentages, and assignment submissions) measure compliance and historical scoring, but frequently fail to reveal:
1. What a student actually understands conceptually.
2. Where specific topic gaps and learning impediments exist.
3. Whether a student possesses demonstrable, practical competencies required for professional industry roles.

### The Non-Aggregation Rule
The core architectural invariant of MASTERY is:
> **The three intelligence outputs — Academic Risk, Learning Mastery, and Career Readiness — must never be combined into an arbitrary aggregate student score.**

A student may be:
- At **Academic Risk** (due to missed laboratory sessions or attendance deficit) while simultaneously demonstrating **High Career Readiness** (via proven open-source software contributions and independent database architecture mastery).
- Scoring **High Internal Marks** while possessing severe **Learning Mastery Gaps** (due to rote memorization without practical synthesis capability).

---

## 2. Authentication & Identity Architecture (Phase 02)

MASTERY delegates user identity management to **Supabase Auth** while retaining strict application-level authorization, user profiling, and role-based access control on the FastAPI backend.

```
+---------------------------------------------------------------------------------------+
|                                    CLIENT (BROWSER)                                   |
|                                                                                       |
|   1. User signs in with institutional email & password via `@supabase/supabase-js`    |
|   2. Supabase Auth validates credentials -> Returns authenticated Session & Access JWT |
|   3. Client attaches `Authorization: Bearer <access_token>` on API requests           |
+------------------------------------------+--------------------------------------------+
                                           |
                                           | HTTPS / JSON (Bearer JWT)
                                           v
+------------------------------------------+--------------------------------------------+
|                                  BACKEND API GATEWAY                                  |
|                                                                                       |
|   FastAPI Dependency (`get_current_user` / `get_current_active_user`)                 |
|                                                                                       |
|   Step 1: Parse JWT & retrieve Kid (Key ID)                                           |
|   Step 2: Fetch & verify against live Supabase JWKS (ES256 asymmetric signature)      |
|           Endpoint: `https://<ref>.supabase.co/auth/v1/.well-known/jwks.json`         |
|   Step 3: Validate issuer, audience ("authenticated"), expiration, and sub (user UUID)|
|   Step 4: Load authoritative `Profile` from PostgreSQL database                       |
|   Step 5: Enforce Account Status (`ACTIVE` required, reject `PENDING` / `SUSPENDED`)  |
|   Step 6: Enforce Role Guards (`require_roles` / `require_institution_access`)        |
+------------------------------------------+--------------------------------------------+
                                           |
                                           | Authoritative Query
                                           v
+------------------------------------------+--------------------------------------------+
|                              SUPABASE POSTGRESQL DATABASE                             |
|                                                                                       |
|   - `auth.users`: Supabase identity ledger                                            |
|   - `public.profiles`: Application identity, role, account_status, institution_id     |
|   - `public.institutions`: Multi-tenant educational institutions                     |
|   - `public.institution_memberships`: Scoped user-to-institution roles & approvals    |
|   - Row-Level Security (RLS) active on all public application tables                  |
+---------------------------------------------------------------------------------------+
```

---

## 3. Role-Based Access Control (RBAC) Matrix

| Global Role | Scope | Permitted Capabilities | Prohibited Capabilities |
| :--- | :--- | :--- | :--- |
| **SUPER_ADMIN** | Platform-Wide | Manage institutions, oversee global configuration, view all telemetry, system diagnostics | None |
| **INSTITUTION_ADMIN** | Designated Institution | Approve/suspend student and faculty accounts, manage institution settings, review institution rosters | Cross-institution modifications |
| **FACULTY** | Designated Courses & Cohorts | Upload & verify syllabus PDFs, approve AI-generated questions, review student risk alerts, manage interventions | Modifying other faculty's courses or institutional configurations |
| **PLACEMENT_OFFICER**| Designated Institution | Curate industry roles & benchmarks, evaluate placement readiness radars, verify GitHub/practical evidence | Modifying academic syllabus or internal exam marks |
| **STUDENT** | Self-Only | Take assessments, view personal topic mastery, access remedial roadmaps, track target career roles | Viewing cohort risk rosters or peer private records |

---

## 4. Multi-Layer Database Security Architecture

1. **Backend Application Layer:**
   - Every request verifies the caller's JWT signature via JWKS before executing business logic.
   - SQL queries apply explicit `WHERE user_id = :id` and `WHERE institution_id = :inst_id` filters in repositories.
2. **PostgreSQL Row-Level Security (RLS) Layer:**
   - Active on `institutions`, `profiles`, and `institution_memberships`.
   - Protects direct Supabase Client / PostgREST access so clients can only access their authorized data slice.
3. **Database Trigger Layer:**
   - `public.handle_new_user()` auto-provisions a `profiles` record on `auth.users` insert with default role `STUDENT` and status `PENDING`.
   - Never trusts client-supplied metadata for administrative privilege escalation.
