# MASTERY — Frontend Structural Audit

**Project:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Track:** AI, CyberSecurity and Digital Trust  
**Date:** November 2026  
**Active Branch:** `main`  
**Starting Commit:** `0b8a16d`  

---

## 1. Executive Summary & Audit Context

A comprehensive structural audit of the MASTERY frontend was performed. While previous visual iterations introduced brand colors (Deep Teal `#237277` and Mint `#D9F0EE`), the overall information architecture, navigation, page composition, and user experience still exhibited major structural deficits:

1. **Over-Concentration on a Single Landing Page:**  
   The landing page (`/`) attempted to contain all information (problem, pipeline, 7 modules, architecture, differentiators, roles, impact) in one lengthy vertical scroll, rather than providing dedicated, navigable public pages for evaluators and institutional stakeholders.
2. **Obsolete Demo Clutter & "Demo References":**  
   The application displayed prominent "Demo Walkthrough", "Demo Guide", "DEMO DATA — SYNTHETIC / NOT REAL STUDENT RECORDS" banners, scenario switchers, and presentation pitch scripts. This degraded the product's credibility, making it look like a student presentation deck rather than an institutional academic intelligence platform.  
   *Mandate:* **Completely remove the Demo Walkthrough, Demo Guide, and all Demo References from the frontend.**
3. **Missing Dedicated Public Information Architecture:**  
   Evaluators could not navigate directly to dedicated pages such as `/problem`, `/solution`, `/modules`, `/architecture`, `/differentiators`, or `/roles`.
4. **Separation of Public Website vs Authenticated Application Workspace:**  
   The distinction between the public product website and the internal academic application workspace (`/app/*`) needed a cleaner layout separation:
   - **Public Website:** Clean public layout with a focused top navbar, dedicated multi-page information architecture, and footer.
   - **Application Workspace:** Professional institutional shell with a collapsible module sidebar, user/persona switcher, breadcrumbs, and zero demo banners.

---

## 2. Information Architecture Gaps Identified

| Architectural Dimension | Existing State | Required Transformed State |
|---|---|---|
| **Public Website Structure** | Single monolithic landing page (`/`) with anchor links only | Modular, dedicated public routes: `/`, `/problem`, `/solution`, `/modules` (with deep dives for all 7 modules), `/architecture`, `/differentiators`, `/roles`. |
| **Demo References** | Banner: "DEMO DATA — SYNTHETIC / NOT REAL STUDENT RECORDS", "Demo Walkthrough" in sidebar and header, pitch scripts | **Completely removed**. All demo walkthroughs, demo references, and synthetic disclaimers removed from frontend UI. |
| **Global Navigation** | Overloaded with demo links and anchor hashes | Compact, professional navbar: Left (Brand & Tagline), Center (The Problem, Our Solution, Seven Modules, Architecture, Differentiators, Role Ecosystem), Right (Explore Platform / Institutional Login). |
| **Application Workspace Shell** | Embedded `DemoBanner` at the top of every internal page | Clean, authoritative institutional header with role perspective selector, breadcrumbs, and unpolluted workspace. |
| **Data Layer** | Explicit "Demo Context" with pitch scenario selectors | Seamless in-memory institutional data layer (`VARY Institute of Technology`) that powers offline/prototype exploration gracefully without broadcasting demo references. |

---

## 3. Detailed Route Map Plan

### 3.1 Public Website Routes (`PublicLayout`)
- `/` — Product Landing Page (Executive Summary, Hero, High-level flow, CTA)
- `/problem` — The Problem (4 core structural failures of legacy grading)
- `/solution` — Our Solution (The end-to-end evidence intelligence pipeline)
- `/modules` — The Seven Business Modules Overview
- `/modules/academic-data` — Module 01: Academic Data Intelligence Hub
- `/modules/syllabus-intelligence` — Module 02: AI Syllabus & Competency Intelligence
- `/modules/assessment` — Module 03: Intelligent Assessment & Attentiveness Engine
- `/modules/mastery` — Module 04: Learning Mastery & Performance Analytics
- `/modules/academic-risk` — Module 05: Academic Risk Prediction Engine
- `/modules/interventions` — Module 06: Personalized Academic Intervention
- `/modules/career-readiness` — Module 07: Career Readiness & Industry Skill Gap Intelligence
- `/architecture` — Dedicated System Architecture (6 Layers)
- `/differentiators` — Technical Differentiators & Ethical AI Governance
- `/roles` — Role-Based Ecosystem (Student, Faculty, Admin, Placement, Platform)

### 3.2 Authenticated Application Routes (`AppLayout` / `RootLayout`)
- `/app` → Redirects to `/app/dashboard`
- `/app/dashboard` — Unified Multi-Persona Intelligence Dashboard
- `/app/academic-data` — Module 01 Workspace
- `/app/syllabus` — Module 02 Workspace
- `/app/assessments` — Module 03 Workspace
- `/app/mastery` — Module 04 Workspace
- `/app/risk` — Module 05 Workspace (Firewalled from Placement)
- `/app/interventions` — Module 06 Workspace
- `/app/career-readiness` — Module 07 Workspace
- `/app/diagnostics` — System Diagnostics (Admins)

---

## 4. Remediation Plan

1. **Delete Obsolete Demo Components & References:**
   - Remove `DemoBanner` (`frontend/src/components/shared/demo-banner.tsx`).
   - Remove `DemoGuidePage` (`frontend/src/features/demo-guide/`).
   - Remove all demo walkthrough references, links, and buttons from headers, sidebars, and landing pages.
   - Refactor `demo-context` into a clean, transparent institutional data context (`institution-context` or `workspace-context`) providing default records for VARY Institute of Technology without "DEMO" labels.
2. **Build Public Website Layout & Dedicated Public Pages:**
   - Create `PublicLayout` with clean navbar and institutional footer.
   - Author dedicated pages:
     - `ProblemPage` (`/problem`)
     - `SolutionPage` (`/solution`)
     - `ModulesOverviewPage` (`/modules`)
     - `ModuleDetailPage` (`/modules/:moduleSlug`)
     - `ArchitecturePage` (`/architecture`)
     - `DifferentiatorsPage` (`/differentiators`)
     - `RolesPage` (`/roles`)
   - Redesign `LandingPage` (`/`) as a concise, compelling entry point linking to these dedicated pages.
3. **Refine Workspace Shell (`RootLayout`):**
   - Clean `Header` and `Sidebar` of all demo labels.
   - Keep smooth persona switching (Student, Faculty, Admin, Placement, Platform Admin) for institutional evaluation without demo disclaimers.
4. **Verification & Testing:**
   - TypeScript check (`tsc --noEmit`), lint, production build (`vite build`), and backend regression tests.
