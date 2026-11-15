Team VARY : SRUJAN 2026 
PS : AI-03 
Track : AI , CyberSecurity and Digital Trust 

---

# MASTERY — Beyond Marks. Towards Mastery.

**AI-powered Student Performance Analytics, Academic Risk Prediction and Career Readiness Platform.**

## 1. Project Philosophy & Core Principle

MASTERY is an evidence-driven student development platform designed to understand:
- What a student actually knows conceptually.
- Where their specific learning gaps and academic difficulties exist.
- What practical industry competencies they can independently demonstrate.

### The Non-Aggregation Rule
Traditional systems frequently collapse attendance, marks, and coding assessments into one arbitrary score. **MASTERY maintains three distinct intelligence outputs that are never combined into a single number:**
1. **Academic Risk Engine:** Screening for students who need academic support (early warnings, attendance deficits, assessment lag).
2. **Learning Mastery Engine:** Measuring demonstrated topic-level understanding from continuous assessments.
3. **Career Readiness Engine:** Evaluating practical competencies against verified industry role benchmarks (coding, SQL, GitHub evidence).

---

## 2. System Architecture

MASTERY is architected as a **Modular Monolith**:
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query, Lucide Icons.
- **Backend:** Python 3.11+, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2.x, Alembic, PostgreSQL.
- **Database / Cloud:** PostgreSQL / Supabase, with automatic graceful degradation when unconfigured.
- **AI / ML Layer:** Isolated AI service abstraction for structured extraction; decoupled classical ML service for deterministic risk scoring.

```
MASTERY/
|-- frontend/           # React 18 SPA (Vite + TS + Tailwind + TanStack Query)
|-- backend/            # FastAPI Modular Monolith (app/api, app/core, app/db, app/services)
|-- docs/               # System architecture, database design, API contracts, ADRs
|-- docker-compose.yml  # Local multi-container development orchestration
```

---

## 3. Quick Start & Execution Guide

### Prerequisites
- Node.js v18+ (tested on v22.19.0) and `pnpm` (or `npm`)
- Python 3.11+ (tested on Python 3.14 / 3.11+)

### Backend Setup & Execution
```bash
# Navigate to backend directory
cd backend

# Create and activate Python virtual environment
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI development server
uvicorn app.main:app --reload --port 8000
```
- API Base URL: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- Health Diagnostic Probe: `http://localhost:8000/api/v1/health`
- Database Probe: `http://localhost:8000/api/v1/health/database`

### Frontend Setup & Execution
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
pnpm install
# (or npm install)

# Start Vite development server
pnpm dev
# (or npm run dev)
```
- Frontend UI: `http://localhost:5173`

---

## 4. Testing & Verification

### Run Backend Automated Tests
```bash
cd backend
.venv\Scripts\python -m pytest tests -v
```
Test coverage includes:
- `test_root_endpoint`: Verifies service branding and version info.
- `test_health_endpoint`: Verifies application status and service states.
- `test_database_health_unconfigured`: Verifies graceful degradation when database is unset.
- `test_custom_exception_handler`: Verifies standard 404/422 JSON error responses.

### Run Frontend Linting & Build
```bash
cd frontend
pnpm run lint   # Strict TypeScript check (zero errors)
pnpm run build  # Vite production build
```

---

## 5. Architectural Documentation

Complete specifications are located in the `docs/` directory:
- [SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md): Comprehensive system topology, data flows, and AI/ML boundaries.
- [DATABASE_DESIGN.md](docs/DATABASE_DESIGN.md): Entity relationship models, future schemas, audit mixins, and RLS strategy.
- [API_CONTRACTS.md](docs/API_CONTRACTS.md): Endpoint standards, JSON response formats, error contracts, and domain routes.
- [MODULE_BOUNDARIES.md](docs/MODULE_BOUNDARIES.md): Detailed responsibilities and dependencies for all 7 product modules.
- [DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md): Sequential roadmap for Prompts 01 through 11.
- [ARCHITECTURE_DECISIONS.md](docs/ARCHITECTURE_DECISIONS.md): Architectural Decision Records (ADRs 001–006).

---

## 6. The Seven Product Modules

1. **Module 01 — Academic Data Intelligence Hub:** Ingestion, validation, and historical timeline of institutional records.
2. **Module 02 — AI Syllabus & Competency Intelligence:** Curriculum PDF processing, unit/topic breakdown, and learning outcomes.
3. **Module 03 — Continuous Learning & Assessment Engine:** Multi-modal formative testing, coding & SQL challenges.
4. **Module 04 — Evidence Calibration & Student Mastery Analytics:** Demonstrated understanding triangulation and mastery heatmaps.
5. **Module 05 — Explainable Academic Risk Prediction:** Early-warning risk screening and faculty review checkpoints.
6. **Module 06 — Personalized Intervention & Student Growth:** Tailored remedial roadmaps, mentorship, and recovery tracking.
7. **Module 07 — Industry & Placement Readiness Intelligence:** Role benchmarking, practical skill proofs, and placement radars.
