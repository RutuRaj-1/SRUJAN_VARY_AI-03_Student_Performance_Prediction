# MASTERY — Frontend Route Map

**Project:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Routing Architecture:** React Router DOM v6 with Decoupled Public Website & Internal Application Workspace  

---

## 1. Complete Route Table

| Path | Layout | Component | Access Policy | Purpose |
|---|---|---|---|---|
| `/` | `PublicLayout` | `LandingPage` | Public / Unguarded | Executive summary, hero, problem highlights, pipeline preview, closing CTA |
| `/problem` | `PublicLayout` | `ProblemPage` | Public / Unguarded | Deep dive into the 4 structural failures of legacy grading |
| `/solution` | `PublicLayout` | `SolutionPage` | Public / Unguarded | Visual, end-to-end evidence intelligence workflow |
| `/modules` | `PublicLayout` | `ModulesOverviewPage` | Public / Unguarded | Comprehensive showcase of all seven business modules |
| `/modules/academic-data` | `PublicLayout` | `ModuleDetailPage` (M01) | Public / Unguarded | Module 01: Academic Data Intelligence Hub deep dive |
| `/modules/syllabus-intelligence` | `PublicLayout` | `ModuleDetailPage` (M02) | Public / Unguarded | Module 02: AI Syllabus & Competency Intelligence deep dive |
| `/modules/assessment` | `PublicLayout` | `ModuleDetailPage` (M03) | Public / Unguarded | Module 03: Intelligent Assessment & Attentiveness Engine deep dive |
| `/modules/mastery` | `PublicLayout` | `ModuleDetailPage` (M04) | Public / Unguarded | Module 04: Learning Mastery & Performance Analytics deep dive |
| `/modules/academic-risk` | `PublicLayout` | `ModuleDetailPage` (M05) | Public / Unguarded | Module 05: Academic Risk Prediction Engine deep dive |
| `/modules/interventions` | `PublicLayout` | `ModuleDetailPage` (M06) | Public / Unguarded | Module 06: Personalized Academic Intervention deep dive |
| `/modules/career-readiness` | `PublicLayout` | `ModuleDetailPage` (M07) | Public / Unguarded | Module 07: Career Readiness & Industry Skill Gap deep dive |
| `/architecture` | `PublicLayout` | `ArchitecturePage` | Public / Unguarded | 6-layer system architecture and verified tech stack |
| `/differentiators` | `PublicLayout` | `DifferentiatorsPage` | Public / Unguarded | Implemented differentiators & ethical AI boundaries |
| `/roles` | `PublicLayout` | `RolesPage` | Public / Unguarded | Multi-persona ecosystem (Student, Faculty, Admin, Placement, Platform) |
| `/login` | Standalone | `LoginPage` | Public Auth | Institutional login |
| `/register` | Standalone | `RegisterPage` | Public Auth | Institutional registration |
| `/forgot-password` | Standalone | `ForgotPasswordPage` | Public Auth | Password reset |
| `/unauthorized` | Standalone | `UnauthorizedPage` | Public Auth | RBAC boundary notice |
| `/app` | `RootLayout` | Redirect to `/app/dashboard` | Workspace Entry | Redirects to dashboard |
| `/app/dashboard` | `RootLayout` | `DashboardPage` | Protected / Workspace | Multi-persona unified intelligence dashboard |
| `/app/academic-data` | `RootLayout` | `AcademicDataPage` | Protected: Student, Faculty, Admin | Module 01 functional workspace |
| `/app/syllabus` | `RootLayout` | `SyllabusPage` | Protected: Student, Faculty, Admin | Module 02 functional workspace |
| `/app/assessments` | `RootLayout` | `AssessmentPage` | Protected: Student, Faculty, Admin | Module 03 functional workspace |
| `/app/mastery` | `RootLayout` | `MasteryPage` | Protected: Student, Faculty, Placement, Admin | Module 04 functional workspace |
| `/app/risk` | `RootLayout` | `AcademicRiskPage` | Protected (Firewalled from Placement) | Module 05 functional workspace |
| `/app/academic-risk` | `RootLayout` | Redirect to `/app/risk` | Workspace Alias | Alias for Module 05 |
| `/app/interventions` | `RootLayout` | `InterventionPage` | Protected: Student, Faculty, Admin | Module 06 functional workspace |
| `/app/career-readiness` | `RootLayout` | `CareerReadinessPage` | Protected: Student, Placement, Faculty, Admin | Module 07 functional workspace |
| `/app/diagnostics` | `RootLayout` | `DiagnosticsPage` | Protected: Admin | System telemetry and diagnostics |
| `*` | Standalone | `NotFoundPage` | Public Catch-All | Custom 404 page with return home links |

---

## 2. Backward-Compatible Top-Level Redirects

To prevent broken links from bookmarks or earlier phases:
- `/dashboard` → `/app/dashboard`
- `/academic-data` → `/app/academic-data`
- `/syllabus` → `/app/syllabus`
- `/assessments` → `/app/assessments`
- `/mastery` → `/app/mastery`
- `/risk` & `/academic-risk` → `/app/risk`
- `/interventions` → `/app/interventions`
- `/career-readiness` → `/app/career-readiness`
- `/diagnostics` → `/app/diagnostics`
- `/demo-guide` & `/walkthrough` → `/solution` (clean redirect to public solution workflow)
