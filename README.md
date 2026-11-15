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

## 2. System Architecture & Authentication (Phase 02 Active)

MASTERY is architected as a **Modular Monolith**:
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query, Lucide Icons, `@supabase/supabase-js`.
- **Backend:** Python 3.11+, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2.x, Alembic, PostgreSQL, `pyjwt[crypto]`, `psycopg`.
- **Database / Cloud:** Supabase PostgreSQL with Row Level Security (RLS) & Supabase Auth.
- **JWT Verification:** Asymmetric `ES256` key signature validation via live Supabase JWKS with caching.
- **Role-Based Access Control:** Strict 5-tier role hierarchy (`SUPER_ADMIN`, `INSTITUTION_ADMIN`, `STUDENT`, `FACULTY`, `PLACEMENT_OFFICER`).

```
MASTERY/
|-- frontend/           # React 18 SPA (Vite + TS + Tailwind + TanStack Query + Supabase JS)
|-- backend/            # FastAPI Modular Monolith (app/api, app/core, app/db, app/services)
|-- docs/               # System architecture, database design, API contracts, ADRs
```

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
- Auth Verification: `http://localhost:8000/api/v1/auth/me`

### Frontend Setup & Execution
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
pnpm install

# Start Vite development server
pnpm dev
```
- Frontend UI: `http://localhost:5173`
- Login Page: `http://localhost:5173/login`
- Student Registration: `http://localhost:5173/register`
- Password Recovery: `http://localhost:5173/forgot-password`

---

## 4. Testing & Verification

### Run Backend Automated Tests
```bash
cd backend
.venv\Scripts\python -m pytest tests -v
```
Test suite includes 15 automated test cases:
- Root & Health Probes (Application & Database diagnostic states)
- Unauthenticated access returns 401
- Invalid JWT tokens return 401
- Authenticated student access & permission resolution
- Role enforcement: Student forbidden from administrative routes (403)
- Account status enforcement: PENDING accounts blocked with approval notice (403)
- Institution Admin multi-tenant scoping & cross-institution isolation (403)
- Super Admin full governance (200)
- Profile self-edit protection (role tampering strictly prevented)

### Run Frontend Linting & Build
```bash
cd frontend
pnpm run lint   # Strict TypeScript check (0 errors)
pnpm run build  # Vite production build (0 errors)
```

---

## 5. Architectural Documentation

Complete specifications are located in the `docs/` directory:
- [SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md): Comprehensive system topology, JWKS authentication flows, and RBAC matrix.
- [DATABASE_DESIGN.md](docs/DATABASE_DESIGN.md): Entity relationship models, UUID strategy, initial tables, and RLS policies.
- [API_CONTRACTS.md](docs/API_CONTRACTS.md): Endpoint standards, JSON response formats, error contracts, and Auth/User/Institution routes.
- [MODULE_BOUNDARIES.md](docs/MODULE_BOUNDARIES.md): Detailed responsibilities and dependencies for all 7 product modules.
- [DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md): Sequential roadmap for Prompts 01 through 11.
- [ARCHITECTURE_DECISIONS.md](docs/ARCHITECTURE_DECISIONS.md): Architectural Decision Records (ADRs 001–008).
