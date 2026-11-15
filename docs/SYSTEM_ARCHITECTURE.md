# MASTERY — System Architecture Document

**Platform Working Title:** MASTERY — Beyond Marks. Towards Mastery.  
**System Type:** AI-Powered Student Performance Analytics, Academic Risk Prediction, and Career Readiness Platform  
**Architecture Style:** Modular Monolith (Decoupled Frontend & Backend)  
**Phase:** 01/11 — Architecture & Codebase Initiation  

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

Collapsing these dimensions into a single scalar destroys actionable signal and induces misleading diagnostic conclusions.

---

## 2. High-Level Architectural Diagram

```
+---------------------------------------------------------------------------------------+
|                                    CLIENT LAYER                                       |
|                                                                                       |
|   React 18 SPA (TypeScript + Vite + Tailwind CSS + TanStack Query + Lucide Icons)      |
|                                                                                       |
|   +-------------------+  +-------------------+  +-------------------+                 |
|   | Academic Data Hub |  | Syllabus & Outcome|  | Assessment Engine |                 |
|   +-------------------+  +-------------------+  +-------------------+                 |
|   +-------------------+  +-------------------+  +-------------------+                 |
|   | Mastery Analytics |  | Risk Prediction   |  | Interventions Hub |                 |
|   +-------------------+  +-------------------+  +-------------------+                 |
|   +-----------------------------------------------------------------+                 |
|   |             Industry & Career Readiness Intelligence            |                 |
|   +-----------------------------------------------------------------+                 |
+------------------------------------------+--------------------------------------------+
                                           |  HTTPS / JSON REST API
                                           |  CORS Enabled (/api/v1)
+------------------------------------------v--------------------------------------------+
|                                  BACKEND API GATEWAY                                  |
|                                                                                       |
|   FastAPI Application (Python 3.11+ / Uvicorn / Pydantic v2 / Starlette)              |
|                                                                                       |
|   +-------------------------------------------------------------------------------+   |
|   | Core Infrastructure: Config (BaseSettings) | Logging | Security (RBAC Auth)   |   |
|   +-------------------------------------------------------------------------------+   |
|   | Routing Layer: /api/v1/health | /academic | /syllabus | /assessments          |   |
|   |                /mastery       | /risk     | /interventions | /career          |   |
|   +-------------------------------------------------------------------------------+   |
+--------------------+---------------------------------------------+--------------------+
                     |                                             |
+--------------------v--------------------+       +----------------v--------------------+
|         APPLICATION DOMAIN SERVICES     |       |       ISOLATED INTELLIGENCE         |
|                                         |       |                                     |
|  - AcademicDataService                  |       |  [AI Service Layer]                 |
|  - SyllabusExtractionService            |       |  - OpenAI Structured JSON Gateway   |
|  - AssessmentExecutionService           |       |  - Pydantic Schema Enforcement      |
|  - EvidenceCalibrationService           |       |  - No startup API key dependency    |
|  - AcademicRiskScreeningService         |       |                                     |
|  - RemedialInterventionService          |       |  [ML Prediction Service]            |
|  - CareerReadinessService               |       |  - Classical Scikit-Learn Models    |
|                                         |       |  - Trained solely on validated data |
|  - Repository Pattern (SQLAlchemy 2.x)  |       |  - Explainable Feature Attributions |
+--------------------+--------------------+       +-------------------------------------+
                     |
+--------------------v------------------------------------------------------------------+
|                               DATA PERSISTENCE & STORAGE                              |
|                                                                                       |
|   PostgreSQL / Supabase Database (UUID Primary Keys, UTC Timestamps, Provenance Audit)|
|   Supabase Storage (PDF Syllabi, Rubric Documents, Code Submission Artifacts)         |
+---------------------------------------------------------------------------------------+
```

---

## 3. Frontend / Backend Separation of Concerns

### Frontend Responsibilities
- **Zero Business Logic:** Calculations of mastery scores, risk probabilities, and competency percentiles remain strictly on the backend.
- **Server State Caching:** TanStack Query handles caching, deduplication, background invalidation, and optimistic state.
- **Typed API Communication:** A centralized `apiClient` manages baseUrl configuration, custom `ApiClientError` formatting, and request cancellation.
- **Data-Dense SaaS UX:** Information architecture optimized for faculty, student, and counselor personas with clear visual feedback for loading, unconfigured, degraded, and error states.

### Backend Responsibilities
- **Domain Service Encapsulation:** Business logic resides inside domain services, not inside API route handlers.
- **Repository Pattern:** Database queries are decoupled through `BaseRepository[T]` to guarantee isolation from the web framework.
- **Resilient Startup:** External dependencies (Supabase, OpenAI) are checked on-demand rather than at initial boot. The server boots and passes health checks even in air-gapped or unconfigured states.
- **Validated Inputs/Outputs:** Strict Pydantic v2 schemas for all requests and responses with automated 422 error wrapping.

---

## 4. AI & ML Integration Boundaries

A critical architectural requirement is the strict physical separation between:
1. **Generative AI Services (`app.services.ai`):**
   - Used for unstructured text extraction (Syllabus PDF unit extraction), question generation assistance, and personalized remedial plan phrasing.
   - Enforces structured JSON output via Pydantic model schemas.
   - Never makes decisions on academic risk without human verification.
2. **Machine Learning Predictive Services (`app.services.ml`):**
   - Used exclusively for statistical risk classification and early-warning alerts.
   - Built on deterministic, inspectable algorithms (e.g., Logistic Regression, Gradient Boosting).
   - Trained only on verified historical academic records from the institution.
   - Strictly isolated from LLM prompt pipelines to prevent hallucinated risk assessments.

---

## 5. Security & Multi-Role Governance

MASTERY implements Role-Based Access Control (RBAC) across four primary user personas:
1. `STUDENT`: Read access to personal mastery scores, personal risk support notifications, assigned assessments, and career readiness roadmaps.
2. `FACULTY`: Course-level oversight, syllabus upload & approval, question bank curation, manual evaluation overrides, and intervention plan sign-offs.
3. `CAREER_COUNSELOR`: Aggregate cohort placement readiness views, industry role benchmark maintenance, and skill gap review.
4. `ADMIN`: Institutional configuration, academic data import execution, user provisioning, and audit log inspection.
