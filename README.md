Team VARY : SRUJAN 2026 
PS : AI-03 
Track : AI , CyberSecurity and Digital Trust 

---

<p align="center">
  <img src="frontend/public/logo.png" alt="MASTERY — Beyond Marks. Towards Mastery." width="360" />
</p>

# MASTERY — Beyond Marks. Towards Mastery.

> **AI-Powered Student Performance Prediction, Explainable Topic Mastery & Ethical Academic Intelligence Ecosystem**  
> *Developed by Team VARY for SRUJAN 2026 — Problem Statement AI-03 (Student Performance Prediction)*

[![Tests](https://img.shields.io/badge/pytest-73%20passed%20%5B100%25%5D-brightgreen.svg)]()
[![TypeScript](https://img.shields.io/badge/TypeScript-Strict%20%5B0%20errors%5D-blue.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)]()
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%20%2B%20pgvector-336791.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

---

## 1. Executive Summary & The Core Problem

Traditional higher education evaluation relies on **blunt composite marks and retrospective semester-end exams**. This creates four structural failures across universities:

1. **Trapped & Fragmented Data:** Syllabus PDFs, LMS logs, and exam marks sit in disconnected silos without tamper-evident validation or provenance.
2. **Overall Marks Conceal Conceptual Gaps:** A student with a 74% grade can have a complete 0% failure in foundational prerequisites (e.g. pointers, dynamic memory), guaranteeing failure in downstream courses.
3. **Post-Mortem Risk Detection:** Struggling students are discovered only after semester results are published, weeks after the opportunity for corrective remediation has passed.
4. **Academic-Industry Disconnect:** High cumulative GPAs frequently fail to translate into demonstrable practical competencies required by modern industry roles.

### The MASTERY Remedy
**MASTERY** replaces opaque aggregate grading with an **evidence-backed, explainable academic intelligence pipeline**. The platform transforms unstructured curriculum documents into canonical prerequisite graphs, evaluates student assessment evidence down to the individual question level, computes fine-grained Bloom's taxonomy mastery, predicts academic risk with transparent SHAP explanations weeks before midterms, and coordinates faculty-approved remedial interventions.

---

## 2. The Seven Specialized Business Modules

MASTERY is architected as an interconnected modular monolith of seven specialized domain engines:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         MASTERY CLOSED-LOOP PIPELINE                             │
└──────────────────────────────────────────────────────────────────────────────────┘
  [M01: AI Syllabus] ──► [M02: Data Hub] ──► [M03: Assessment Engine]
                                                     │
                                                     ▼
  [M07: Career Intel] ◄── [M06: Interventions] ◄── [M05: Risk Engine] ◄── [M04: Mastery]
```

| Module | Code | Technical Mission | Key Capabilities |
|---|---|---|---|
| **AI Syllabus & Competency Intelligence** | `M01` | Parses unstructured syllabi into canonical Directed Acyclic Graphs (DAGs). | PDF/Word OCR, Bloom's Taxonomy tagging (L1–L6), prerequisite dependency verification, CLO-to-topic semantic mapping. |
| **Academic Data Intelligence Hub** | `M02` | Single source of truth reconciling fragmented institutional records. | CSV/XLSX two-phase ingestion, grade normalization (SGPA/CGPA/Percentage), attendance velocity tracking, immutable audit trails. |
| **Assessment & Attentiveness Engine** | `M03` | Evaluates student submissions against rubric criteria with interaction telemetry. | Multimodal question authoring, rubric-referenced auto-evaluation, Bloom's cognitive level profiling, ethical non-surveillance attentiveness metrics. |
| **Learning Mastery Analytics** | `M04` | Transforms marks into granular topic mastery (0–100%) and OBE attainment. | Bayesian topic evidence aggregation, NBA/NAAC Course Learning Outcome (CLO) attainment scorecards, prerequisite knowledge debt flags. |
| **Academic Risk Prediction Engine** | `M05` | Predicts future academic failure in Weeks 3–6 with transparent explanations. | Calibrated risk tiering (Low, Moderate, High, Critical), SHAP factor attribution vectors, temporal trajectory modeling, zero demographic profiling. |
| **Personalized Academic Intervention** | `M06` | Prescribes scaffolded remedial plans addressing verified prerequisite gaps. | Automated learning itinerary generation, Human-in-the-Loop faculty approval lifecycle (`DRAFT` → `APPROVED` → `ACTIVE` → `COMPLETED`), post-intervention outcome verification. |
| **Career Readiness Intelligence** | `M07` | Benchmarks verified academic competencies against live industry frameworks. | O*NET/ESCO role taxonomy mapping, radar skill gap diagnostics, faculty-verified GitHub/capstone portfolio artifacts. |

---

## 3. Dual-Layer Architecture & Stakeholder Ecosystem

MASTERY separates public institutional storytelling from the secure operational workspace:

### Layer A: Public Product Website (`PublicLayout`)
- `/` — Executive Product Landing Page with institutional metrics and feature overviews.
- `/problem` — Comprehensive breakdown of the 4 structural failures in higher education.
- `/solution` — End-to-end 7-stage interconnected intelligence pipeline specification.
- `/modules` — Catalog of all seven business modules with technical deep dives.
- `/modules/:moduleSlug` — Dynamic specifications for M01 through M07.
- `/architecture` — Six-layer full-stack system architecture and verification telemetry.
- `/differentiators` — Technical differentiators, head-to-head comparison table, and AI charter.
- `/roles` — Detailed persona cards across the 5-stakeholder ecosystem.

### Layer B: Authenticated Academic Workspace (`RootLayout` under `/app/*`)
- **Student Persona:** Self-directed topic mastery trees, identified bottleneck warnings, faculty-approved support plans, and career readiness roadmaps.
- **Faculty Persona:** Cohort diagnostic heatmaps, question-level rubric grading, real-time CLO attainment, and intervention approval authority.
- **Academic Admin / HoD Persona:** Departmental attrition radar, NBA/NAAC accreditation compliance audits, and multi-semester prerequisite friction analysis.
- **Placement Officer Persona:** Verified industry competency profiles benchmarked against O*NET/ESCO. **Permanently firewalled from student risk flags.**
- **Platform Admin Persona:** Tenant administration, batch ingestion pipelines, and cryptographic audit log monitoring.

---

## 4. Ethical AI, Digital Trust & Privacy Firewall

In adherence to the **AI, CyberSecurity and Digital Trust** track:

1. **Placement Privacy Firewall:** Recruiter and placement officer accounts receive HTTP 403 Forbidden responses when querying student academic risk scores, mental health flags, or remedial intervention history.
2. **Temporal Data Leakage Prevention:** All risk prediction models strictly evaluate features timestamped before the prediction cutoff date. Final exam grades are never leaked into mid-semester predictors.
3. **Mandatory Human-in-the-Loop:** AI synthesizes remedial plans, but no intervention is dispatched to students without formal faculty advisor review and cryptographic approval sign-off.
4. **Zero Demographics Ingestion:** Predictive models ingest zero socio-economic, racial, gender, or demographic features. Predictions rely strictly on verified academic telemetry.
5. **Explainability Over Black-Box Scoring:** Every risk score is accompanied by top contributory factors weighted by SHAP (SHapley Additive exPlanations) values.

---

## 5. Technology Stack

```
MASTERY Technology Stack
├── Frontend (Decoupled SPA)
│   ├── Framework: React 18.3 + TypeScript + Vite 5.4
│   ├── Styling: Tailwind CSS (Structured Brutalism + Editorial Academic Design)
│   ├── State & Data: TanStack React Query + Context API
│   ├── Icons & Visuals: Lucide React + Recharts
│   └── Client Auth: @supabase/supabase-js with JWT session management
├── Backend (Modular Monolith)
│   ├── Runtime: Python 3.11+ / FastAPI (Asynchronous ASGI)
│   ├── Validation: Pydantic v2 schemas with strict typing
│   ├── ORM & DB: SQLAlchemy 2.0 + Alembic migrations
│   ├── ML & Analytics: NumPy, SciPy, Scikit-Learn, SHAP, NetworkX
│   └── Security: OAuth2 with asymmetric ES256 Supabase JWKS verification
└── Persistence & Ingress
    ├── Primary DB: PostgreSQL 15 with pgvector extension
    ├── Cache & Memory: Redis (caching) + SQLite In-Memory (testing fallback)
    └── Document OCR: pypdf, python-docx, openpyxl, python-multipart
```

---

## 6. Quick Start & Execution Guide

### Prerequisites
- **Node.js:** v18+ (tested on v20.x and v22.x)
- **Python:** 3.11+ (tested on Python 3.11, 3.12, 3.14)
- **Package Managers:** `npm` or `pnpm`, `pip`

### 1. Clone the Repository
```bash
git clone https://github.com/RutuRaj-1/SRUJAN_VARY_AI-03_Student_Performance_Prediction.git
cd SRUJAN_VARY_AI-03_Student_Performance_Prediction
```

### 2. Backend Setup
```bash
cd backend

# Create and activate virtual environment
python -m venv .venv

# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI development server
uvicorn app.main:app --reload --port 8000
```
- **API Base URL:** `http://localhost:8000`
- **Interactive OpenAPI Documentation:** `http://localhost:8000/docs`
- **System Health Probe:** `http://localhost:8000/api/v1/health`

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
- **Public Product Website:** `http://localhost:5173`
- **Academic Workspace:** `http://localhost:5173/app`
- **Institutional Login:** `http://localhost:5173/login`

---

## 7. Automated Testing & Performance Verification

### Run Complete Test Suite
```bash
# Execute from project root with PYTHONPATH configured
$env:PYTHONPATH="backend"; python -m pytest backend/tests/ -W ignore
```
```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-8.4.2
collected 73 items

backend\tests\test_academic_data.py ........                             [ 10%]
backend\tests\test_assessments.py ........                               [ 21%]
backend\tests\test_auth.py ...........                                   [ 36%]
backend\tests\test_career_readiness.py ......                            [ 45%]
backend\tests\test_health.py ....                                        [ 50%]
backend\tests\test_integration_and_hardening.py .....                    [ 57%]
backend\tests\test_interventions.py ......                               [ 65%]
backend\tests\test_mastery.py .......                                    [ 75%]
backend\tests\test_risk.py .......                                       [ 84%]
backend\tests\test_syllabus.py .....                                     [ 91%]
backend\tests\test_unified_dashboard.py ......                           [100%]

============================= 73 passed in 3.88s ==============================
```

### Run Performance Benchmarking Harness
```bash
python scripts/benchmark_performance.py 15
```
```
======================================================================================
Endpoint                                      | Role              | Median   | p95      | Errors
======================================================================================
/api/v1/dashboard/student/overview            | STUDENT           | 162.77ms | 172.44ms | 0/15
/api/v1/dashboard/faculty/overview            | FACULTY           | 116.76ms | 127.63ms | 0/15
/api/v1/dashboard/institution/overview        | INSTITUTION_ADMIN | 189.76ms | 218.44ms | 0/15
/api/v1/dashboard/placement/overview          | PLACEMENT_OFFICER |  90.96ms | 135.76ms | 0/15
/api/v1/dashboard/admin/overview              | SUPER_ADMIN       |  87.86ms |  95.71ms | 0/15
======================================================================================
```

### Run Frontend Production Bundle Verification
```bash
cd frontend
npm run build
```
```
✓ 1714 modules transformed.
✓ built in 4.11s (dist/index.html, assets/index.css, assets/index.js)
TypeScript check: 0 errors.
```

---

## 8. Architectural Documentation Directory

Comprehensive technical specifications and architectural decision records are maintained in `docs/`:

| Document | Purpose & Scope |
|---|---|
| [PROJECT.md](PROJECT.md) | Exhaustive Project Explainer: Problem, Solution, Algorithms, Architecture, Governance. |
| [FRONTEND_INFORMATION_ARCHITECTURE.md](docs/FRONTEND_INFORMATION_ARCHITECTURE.md) | Dual-layer website vs. workspace route map and UI navigation topology. |
| [FRONTEND_DESIGN_SYSTEM.md](docs/FRONTEND_DESIGN_SYSTEM.md) | Structured Brutalism and Editorial Academic Intelligence token specifications. |
| [FRONTEND_VALIDATION_REPORT.md](docs/FRONTEND_VALIDATION_REPORT.md) | End-to-end frontend quality assurance and build certification. |
| [FRONTEND_TRANSFORMATION_REPORT.md](docs/FRONTEND_TRANSFORMATION_REPORT.md) | Audit results and transformation summary. |
| [SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md) | 6-layer decoupled modular monolith architecture specification. |
| [DATABASE_DESIGN.md](docs/DATABASE_DESIGN.md) | PostgreSQL schema, 58 relational tables, Row-Level Security (RLS) policies. |
| [API_CONTRACTS.md](docs/API_CONTRACTS.md) | Complete OpenAPI endpoint documentation and request/response schemas. |

---

## 9. Team VARY — SRUJAN 2026

- **Institution:** VARY Institute of Technology
- **Problem Statement:** AI-03 — Student Performance Prediction
- **Track:** AI, CyberSecurity and Digital Trust
- **Platform:** MASTERY — Beyond Marks. Towards Mastery.
