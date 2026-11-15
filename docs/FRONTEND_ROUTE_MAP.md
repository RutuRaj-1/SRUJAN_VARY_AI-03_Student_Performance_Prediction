# MASTERY Frontend Route Map

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Architecture:** React Router DOM v6 with Dual Mode (Public Showcase & Interactive Application Shell)  

---

## 1. Unified Route Hierarchy

```text
/                                -> Public Landing Page (Showcase, Architecture, Modules)
/platform                        -> Alias / Anchor to Landing Page Platform Overview
/architecture                    -> Alias / Anchor to Landing Page System Architecture
/demo-guide                      -> Interactive Demo Walkthrough & Presentation Guide

/app                             -> Application Shell Index (Redirects to /app/dashboard)
/app/dashboard                   -> Unified Intelligence Dashboard (Multi-Persona Overview)
/app/academic-data               -> Module 01: Academic Data Intelligence Hub
/app/syllabus                    -> Module 02: AI Syllabus & Competency Intelligence
/app/assessments                 -> Module 03: Intelligent Assessment & Attentiveness Engine
/app/mastery                     -> Module 04: Learning Mastery & Performance Analytics
/app/risk                        -> Module 05: Academic Risk Prediction Engine
/app/academic-risk               -> Alias for Module 05
/app/interventions               -> Module 06: Personalized Academic Intervention
/app/career-readiness            -> Module 07: Career Readiness & Industry Skill Gap
/app/diagnostics                 -> System Diagnostics & Health (Admins)

/dashboard                       -> Backward-compatible redirect to /app/dashboard
/academic-data                   -> Backward-compatible redirect to /app/academic-data
/syllabus                        -> Backward-compatible redirect to /app/syllabus
/assessments                     -> Backward-compatible redirect to /app/assessments
/mastery                         -> Backward-compatible redirect to /app/mastery
/academic-risk                   -> Backward-compatible redirect to /app/risk
/interventions                   -> Backward-compatible redirect to /app/interventions
/career-readiness                -> Backward-compatible redirect to /app/career-readiness

/login                           -> Public Auth: Institutional Login
/register                        -> Public Auth: Institutional Registration
/forgot-password                 -> Public Auth: Password Reset
/unauthorized                    -> RBAC Boundary Enforcement Notice
*                                -> Custom Designed 404 Not Found Page
```

---

## 2. Access Control & Demo Mode Policy

1. **Public Routes (`/`, `/demo-guide`, `/login`, `/register`):**
   - Completely unguarded; requires no active Supabase token.
   - Guaranteed never to redirect to `/login` or throw authentication errors.
2. **Interactive Demo Mode:**
   - When a user enters the platform without an active authenticated profile, or toggles "Demo Mode" via the top utility bar, the application loads isolated in-memory synthetic fixtures.
   - Protected routes grant read access to the synthetic scenario under the active demo persona (Student, Faculty, Institution Admin, Placement Officer, Super Admin).
3. **Placement Officer Privacy Firewall:**
   - Both in Live Mode and Demo Mode, users viewing the platform as `PLACEMENT_OFFICER` are strictly barred from `/app/risk` (Academic Risk Prediction). The route renders the Ethical AI Boundary Notice.
4. **Live Mode Continuity:**
   - When authenticated with valid institutional credentials, the existing React Query services continue to communicate with FastAPI endpoints without modification.
