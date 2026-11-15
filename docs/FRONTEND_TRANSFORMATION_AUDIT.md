# MASTERY — Frontend Transformation Audit

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Track:** AI, CyberSecurity and Digital Trust  
**Date:** November 2026  
**Active Git Branch:** `main`  
**Starting Commit:** `6b5f738`

---

## 1. Executive Summary

This pre-implementation audit examines the frontend architecture, routing, design system, API integration points, and component hierarchy of the MASTERY platform. 

The application backend comprises seven fully implemented and tested business modules (Phases 03–10) with verified database models, RLS security policies, and FastAPI endpoints. However, the user-facing frontend exhibits several presentation and operational shortcomings:
1. **Lack of Public Storytelling:** Visiting the root route (`/`) immediately attempts to render the internal Dashboard inside the authenticated shell, offering no public product introduction, problem explanation, or architecture overview.
2. **Development-Oriented Clutter:** UI surfaces display prototype indicators ("Prototype v0.2", "Phase 04/11", "Module 03", "API Docs", "Backend Offline") that confuse evaluators and obscure the business domain.
3. **Hard Error Traps:** When unauthenticated or when the backend database has no active student profile loaded, users are trapped behind generic "Student Profile Not Found" error boxes or redirected to `/login`, making demonstration impossible without live database seeding.
4. **Visual Inconsistency:** Individual module pages mix dark mode panels (`bg-slate-900`) with light mode tables (`bg-white`) and varying border radii, lacking a unified brand design system.
5. **Absence of Frontend Demo Isolation:** Presenters currently have no way to explore cross-module scenarios without running destructive or synthetic writes into the live PostgreSQL database.

---

## 2. Project Documentation Discovery

An audit of the repository documentation yielded the following results:
- **`Project.md` / `PROJECT.md`:** **Not found** in root or `docs/`. In accordance with prompt instructions, product requirements were derived directly from established specifications in `docs/` (`SYSTEM_ARCHITECTURE.md`, `DEVELOPMENT_ROADMAP.md`, `MODULE_BOUNDARIES.md`, `API_CONTRACTS.md`, `UNIFIED_DASHBOARD_ARCHITECTURE.md`, `HACKATHON_DEMO_GUIDE.md`).
- **`DESIGN.md`:** Present in repository root. Identified as a visual design reference document for "FinBridge". As mandated, finance-specific business logic is completely ignored, and only visual design principles are adapted:
  - Light-first and white-first surfaces.
  - Deep teal brand palette (`#237277`, `#123E40`, `#D9F0EE`).
  - Structured Brutalist containers: 1px visible borders, crisp padding, rectangular cards (2px–8px radius), high data density.
  - Restrained semantic status badges (success, warning, danger, info, AI).

---

## 3. Existing Routes & Architecture Audit

### 3.1 Existing Route Table (`frontend/src/app/router/index.tsx`)
| Route | Component | Guard / Access Policy | Issues |
|---|---|---|---|
| `/` | `DashboardPage` inside `RootLayout` | Unguarded index | Traps unauthenticated evaluators in error state; no landing page |
| `/login` | `LoginPage` | Public | Standard email/password; requires Supabase auth |
| `/register` | `RegisterPage` | Public | Registers user |
| `/dashboard/student` | `DashboardPage` | Protected: `STUDENT`, `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN` | Redundant route pointing to same page |
| `/dashboard/faculty` | `DashboardPage` | Protected: `FACULTY`, `INSTITUTION_ADMIN`, `SUPER_ADMIN` | Redundant route pointing to same page |
| `/dashboard/institution` | `DashboardPage` | Protected: `INSTITUTION_ADMIN`, `SUPER_ADMIN` | Redundant route pointing to same page |
| `/dashboard/placement` | `DashboardPage` | Protected: `PLACEMENT_OFFICER`, etc. | Redundant route pointing to same page |
| `/academic-data` | `AcademicDataPage` | Protected: Student, Faculty, Admin | Shows "Phase 04/11", "Module 03" badge |
| `/syllabus` | `SyllabusPage` | Protected: Student, Faculty, Admin | Shows internal phase labels |
| `/assessments` | `AssessmentPage` | Protected: Student, Faculty, Admin | Empty without live records |
| `/mastery` | `MasteryPage` | Protected: Student, Faculty, Placement, Admin | Requires selected student |
| `/academic-risk` | `AcademicRiskPage` | Protected: Student, Faculty, Admin (Firewalled from Placement) | Dark UI styling inconsistent with other pages |
| `/interventions` | `InterventionPage` | Protected: Student, Faculty, Admin | Empty without live records |
| `/career-readiness` | `CareerReadinessPage` | Protected: Student, Placement, Faculty, Admin | Empty without live records |
| `/diagnostics` | `DiagnosticsPage` | Protected: Admin | Development diagnostics |
| `*` | `<Navigate to="/" />` | Wildcard | No custom 404 page |

---

## 4. Seven Business Modules Status Audit

| Module # | Official Business Module Name | Existing Feature Path | Current Implementation Status | Identified Gaps for Transformation |
|---|---|---|---|---|
| **01** | Academic Data Intelligence Hub | `src/features/academic-data/index.tsx` | Highly functional; 1,435 LOC. Ingestion, validation, verification, audit trail. | Labelled incorrectly as "Module 03, Phase 04/11"; lacks frontend demo fixtures. |
| **02** | AI Syllabus & Competency Intelligence | `src/features/syllabus/index.tsx` | Functional; units, topics, CLOs, competency extraction. | Labelled as "Module 02, Phase 03"; needs demo fallback for instant inspection. |
| **03** | Intelligent Assessment & Attentiveness Engine | `src/features/assessments/index.tsx` | Comprehensive; question bank, Bloom distribution, student attempt, evaluation queue. | Labeled as "Module 04"; lacks demo mode interactive student attempt. |
| **04** | Learning Mastery & Performance Analytics | `src/features/mastery/index.tsx` | Fully modeled; topic mastery, CLO attainment, evidence sufficiency, gaps. | Requires student selection; crashes or renders empty if database empty. |
| **05** | Academic Risk Prediction | `src/features/academic-risk/index.tsx` | Time-bounded prediction, feature contributions, Placement firewall. | Heavy dark mode (`bg-slate-900`) clashing with rest of light UI. |
| **06** | Personalized Academic Intervention | `src/features/interventions/index.tsx` | Intervention plans, approval lifecycle, student action tracking. | Relies on backend records; lacks demo scenario data. |
| **07** | Career Readiness & Industry Skill Gap Intelligence | `src/features/career-readiness/index.tsx` | Role profiles, competency mapping, project evidence ledger, gap analysis. | Relies on backend records; lacks preloaded role fixtures. |

---

## 5. UI & Shell Deficiencies Identified

1. **Header (`src/components/shared/header.tsx`):**
   - Displays "Prototype v0.2" pill and "API Docs" link prominently.
   - Constantly displays "Backend Offline" or "Probing Backend..." status indicator in header, alarming evaluators.
   - Blue accent colors (`bg-blue-600`) clash with brand teal identity.
2. **Sidebar (`src/components/shared/sidebar.tsx`):**
   - Inconsistent module numbering: Academic Data Hub is labeled "Module 03", Syllabus is "Module 02", Assessment is "Module 04", Mastery is "Module 05", Risk is "Module 06", Interventions is "Module 07", Career is "Module 08".
   - Missing Demo Walkthrough Guide navigation item.
3. **Empty / Offline State Handling:**
   - Red error banner in `StudentDashboardView` ("Student Profile Not Found") halts demonstration if Supabase user is not yet bound to a `student_academic_profiles` row.
4. **Missing Public Entry Surface:**
   - Evaluators entering the platform at root (`/`) must immediately see the Public Product Landing Page explaining MASTERY, its 7 modules, its technical architecture, and impact, with a clear one-click CTA to launch the interactive demo workspace.

---

## 6. Action Plan for Controlled Transformation

1. **Brand & Design System:**
   - Establish CSS variables and Tailwind tokens for Deep Teal (`#237277`, `#123E40`), Muted Mint (`#D9F0EE`, `#EEF8F7`), Charcoal text (`#172825`), and Structured Brutalist borders (`#DCE6E2`, radius 2–8px).
2. **Frontend-Only Synthetic Demo Architecture (`src/demo/`):**
   - Isolate typed fixtures representing VARY Institute of Technology, 24 students, 6 syllabi, 40+ assessments, mastery records, risk predictions, interventions, and career profiles.
   - Guarantee zero database writes (strict frontend memory boundary).
   - Implement 4 deterministic student scenarios (A: Strong Progress, B: Inconsistent, C: Emerging Risk, D: Insufficient Evidence).
3. **Public Product Website (`/`):**
   - Author a complete, responsive landing page with Top Nav, Hero, Problem Statement, 7-Step Solution Pipeline, 7-Module Showcase, Technical Architecture Diagram, Differentiators, Role Ecosystem, and Impact.
4. **Application Shell Redesign:**
   - Update `Header`, `Sidebar`, and `RootLayout` with brutalist teal styling, role perspective switcher, demo scenario selector, and clean demo data disclaimers.
   - Remove development clutter ("Prototype v0.2", "Backend Offline", "API Docs").
5. **Interactive Demo Walkthrough Guide (`/demo-guide`):**
   - Create a dedicated interactive presentation page providing exact narration prompts, step-by-step navigation, and scenario triggers.
6. **Module Page Resilience & Consistency:**
   - Wire each of the 7 module views to support Demo Mode seamlessly while preserving existing live API capabilities.
7. **Verification & Testing:**
   - Execute TypeScript check, linting, production build, and route integrity tests.
