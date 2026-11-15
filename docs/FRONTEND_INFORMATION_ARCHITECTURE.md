# MASTERY — Frontend Information Architecture Specification

**Project:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Track:** AI, CyberSecurity and Digital Trust  
**Version:** 2.0 (Post-Audit Structural Transformation)  

---

## 1. Architectural Strategy: Clear Decoupling of Public Site & Application Shell

MASTERY adopts a clean, dual-layer information architecture:
1. **Public Product Website Layer (`PublicLayout`):**
   - Serves prospective institutions, evaluators, faculty deans, and external stakeholders.
   - Explains the academic problem, the 7-step intelligence pipeline, the seven business modules, the 6-layer system architecture, technical differentiators, and role capabilities.
   - Fully accessible without authentication.
   - **Zero Demo Walkthroughs, Zero Demo References, Zero Synthetic Disclaimers.** The site communicates the authoritative product vision directly.
2. **Academic Application Workspace Layer (`RootLayout`):**
   - Serves logged-in institutional users (Students, Faculty, Institution Admins, Placement Officers, Platform Admins).
   - Houses the Unified Dashboard and the interactive workspaces for the seven business modules.
   - Provides clean role perspective switching for institutional review.
   - Protects confidential records (Placement Officer privacy firewall blocking risk scores).

---

## 2. Complete Public Route Hierarchy

```text
PublicLayout (Navbar + Page Content + Footer)
├── /                                -> Executive Landing Page (Hero, Summary, Highlights, CTA)
├── /problem                         -> The Problem (4 Structural Failures of Legacy Grading)
├── /solution                        -> Our Solution (The Interconnected Evidence Pipeline)
├── /modules                         -> The Seven Business Modules Suite
│   ├── /modules/academic-data       -> Module 01: Academic Data Intelligence Hub
│   ├── /modules/syllabus-intelligence -> Module 02: AI Syllabus & Competency Intelligence
│   ├── /modules/assessment          -> Module 03: Intelligent Assessment & Attentiveness Engine
│   ├── /modules/mastery             -> Module 04: Learning Mastery & Performance Analytics
│   ├── /modules/academic-risk       -> Module 05: Academic Risk Prediction Engine
│   ├── /modules/interventions       -> Module 06: Personalized Academic Intervention
│   └── /modules/career-readiness    -> Module 07: Career Readiness & Industry Skill Gap
├── /architecture                    -> System Architecture (6 Layers & Technical Stack)
├── /differentiators                 -> Technical Differentiators & Ethical AI Governance
└── /roles                           -> Multi-Persona Role Ecosystem (5 Personas)
```

---

## 3. Complete Application Workspace Route Hierarchy

```text
RootLayout (Header + Module Sidebar + Main Workspace Area)
├── /app                             -> Redirects to /app/dashboard
├── /app/dashboard                   -> Unified Intelligence Dashboard
├── /app/academic-data               -> Module 01 Workspace (Directory, Ledger, Validation)
├── /app/syllabus                    -> Module 02 Workspace (Unit, Topic, CLO & Competency Explorer)
├── /app/assessments                 -> Module 03 Workspace (Question Bank, Delivery, Telemetry)
├── /app/mastery                     -> Module 04 Workspace (Topic Mastery Radar, CLO Gauges)
├── /app/risk                        -> Module 05 Workspace (Time-Bounded Risk Horizon, Explanations)
├── /app/interventions               -> Module 06 Workspace (Faculty Support Plans, Action Items)
├── /app/career-readiness            -> Module 07 Workspace (Role Profiles, Practical Portfolios)
└── /app/diagnostics                 -> Platform Diagnostics (System Health, DB Telemetry)
```

---

## 4. Global Navigation Specifications

### 4.1 Navbar Layout
- **Left:**
  - MASTERY Logo mark (`M` in Deep Teal container)
  - Wordmark: "MASTERY"
  - Tagline: "Beyond Marks. Towards Mastery."
- **Center Links:**
  - `The Problem` (`/problem`)
  - `Our Solution` (`/solution`)
  - `Seven Modules` (`/modules` with active indicator)
  - `Architecture` (`/architecture`)
  - `Differentiators` (`/differentiators`)
  - `Role Ecosystem` (`/roles`)
- **Right Action Buttons:**
  - `Institutional Login` (`/login`)
  - `Enter Workspace` (`/app/dashboard`) — Primary Button
- **Mobile Responsive Drawer:**
  - Full touch-friendly menu with all routes accessible on mobile screens (375px–430px).

---

## 5. Structural Removal of Demo Clutter

In strict adherence to user instructions:
- **`DemoBanner`:** Removed from all layouts.
- **`DemoGuidePage` / `/demo-guide`:** Removed from navigation, router, and UI.
- **"DEMO DATA — SYNTHETIC / NOT REAL STUDENT RECORDS":** Removed completely from headers and pages.
- **"Scenario A / B / C / D" Pitch Pills:** Removed from global banners.
- In-memory data is maintained transparently under institutional data services (`VARY Institute of Technology`) to guarantee that offline or uninitialized backend states render rich, realistic records without broken screens or loud disclaimers.
