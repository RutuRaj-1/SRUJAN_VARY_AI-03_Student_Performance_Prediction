# MASTERY — Hackathon Demonstration & Judging Guide
## Complete Walkthrough, Setup Instructions & 7-Minute Live Demonstration Script

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Track:** AI, CyberSecurity and Digital Trust  
**Audience:** Hackathon Technical Judges, Academic Evaluators, and Demonstrators  

---

## 1. Prerequisites & Environment Setup

### 1.1 Software Requirements
- **Python:** Version 3.11, 3.12, 3.13, or 3.14.
- **Node.js:** Version 18.x or 20.x (with `pnpm` or `npm`).
- **Git:** Version 2.40+.
- **Database:** PostgreSQL (Supabase Cloud project or local PostgreSQL instance).

### 1.2 Repository Clone & Environment Configuration
```bash
# 1. Clone repository
git clone https://github.com/RutuRaj-1/SRUJAN_VARY_AI-03_Student_Performance_Prediction.git
cd SRUJAN_VARY_AI-03_Student_Performance_Prediction

# 2. Configure Backend Environment
cp backend/.env.example backend/.env
# Update backend/.env with your SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, and DATABASE_URL

# 3. Configure Frontend Environment
cp frontend/.env.example frontend/.env
# Update frontend/.env with VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 1.3 Backend Setup & Database Seeding
```bash
# 1. Activate virtual environment and install dependencies
cd backend
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt

# 2. Run Database Migrations to Head (if not already applied)
alembic upgrade head

# 3. Seed Reference Industry Roles & Synthetic Demonstration Cohort
cd ..
python scripts/seed_demo_data.py
```

### 1.4 Frontend Setup & Launch
```bash
# In a separate terminal:
cd frontend
pnpm install # or npm install
npm run dev
```

The frontend application will be live at `http://localhost:5173`.  
The FastAPI backend OpenAPI interactive documentation is live at `http://localhost:8000/docs`.

---

## 2. Demonstration Accounts & Personas

The synthetic demonstration script seeds the institution **Srujan Institute of Advanced Technology (SIAT)** with realistic personas representing every major institutional role:

| Persona Role | Account Email | Name / Department | Primary Demonstration Capability |
|---|---|---|---|
| **Super Admin** | `superadmin@mastery.edu` | Platform Administrator | Multi-tenant platform health, diagnostic pulse, tenant statistics. |
| **Institution Admin** | `admin@siat.edu` | Dean Rajesh Kulkarni | Executive institution metrics, department benchmarks, intervention ROI. |
| **Faculty Member** | `faculty@siat.edu` | Dr. Ananya Iyer (CSE) | Course intelligence, mastery distribution, risk cohorts, review queues. |
| **Placement Officer** | `placement@siat.edu` | Prof. Vikram Malhotra | Firewalled talent pipeline, industry competency alignment, verified projects. |
| **Student 1 (Top Tier)** | `aarav.sharma@siat.edu` | Aarav Sharma (Sem 5) | Demonstrated mastery across algorithms, 8% risk, verified concurrent Go cache. |
| **Student 2 (Grade Mismatch)**| `riya.sen@siat.edu` | Riya Sen (Sem 5) | 88% exam mark but unassessed critical topics (grade inflation/evidence gap). |
| **Student 3 (Academic Risk)** | `kabir.mehta@siat.edu` | Kabir Mehta (Sem 5) | 38% marks, 62% attendance, 84% failure risk, active remedial intervention plan. |
| **Student 4 (Diagnostic)** | `neha.patel@siat.edu` | Neha Patel (Transfer) | Insufficient evidence without failure label, formative diagnostic queued. |
| **Student 6 (Intervention)** | `sneha.rao@siat.edu` | Sneha Rao (Sem 5) | Active support plan, submitted code exercises, verified faculty progress log. |
| **Student 9 (Open Source)** | `tanmay.deshmukh@siat.edu` | Tanmay Deshmukh (Sem 5) | Verified Raft consensus protocol in Rust, 98% practical coverage for backend role. |

---

## 3. Coherent 7-Minute Live Demonstration Script

```
+---------------------------------------------------------------------------------------------------------+
|                                    7-MINUTE DEMONSTRATION TIMELINE                                      |
+---------+----------------------------------+------------------------------------------------------------+
| Minute  | Demonstration Stage              | Key Talking Points & Visual Screen                         |
+---------+----------------------------------+------------------------------------------------------------+
| 0:00    | The Problem & Opening            | Conventional marks hide conceptual gaps and risk.          |
| 1:00    | 1. Syllabus & Competency Engine  | Syllabus PDF parsed to Bloom's taxonomy & competencies.   |
| 2:00    | 2. Intelligent Assessment Engine | Traceable question-level responses without answer leakage. |
| 3:00    | 3. Learning Mastery Analytics    | Topic mastery heatmaps (0-100%) vs aggregate marks.        |
| 4:00    | 4. Academic Risk Prediction      | Time-bounded explainable risk with protective factors.    |
| 5:00    | 5. Personalized Interventions    | Human-in-the-loop faculty review & student progress tasks. |
| 6:00    | 6. Career Readiness & Firewall   | Multi-dimensional role alignment; Placement firewall (403).|
| 6:30    | 7. Unified Intelligence & Close  | 5-persona dashboard with instant perspective switching.   |
+---------+----------------------------------+------------------------------------------------------------+
```

### Minute 0:00–1:00 — The Problem Statement
> *"Respected judges, in traditional higher education, academic difficulty is discovered only after a student fails their final exam. Worse, a student with an 85% average might secretly lack fundamental algorithmic thinking because exam questions favored rote memorization. MASTERY shifts higher education from superficial marks towards explainable learning mastery and proactive digital trust."*

### Minute 1:00–2:00 — Academic Foundation (Syllabus Intelligence)
- Navigate to **Module 02: Syllabus Intelligence** (`/syllabus`).
- Open **CS-301: Advanced Data Structures & Algorithms**.
- Highlight how unstructured PDF syllabi are decomposed into structured Units, Topics, and Bloom's Revised Taxonomy levels.
- Point out the **Faculty Review Checkpoint**: Unverified AI mappings remain quarantined until approved by course instructors.

### Minute 2:00–3:00 — Assessment Evidence & Attentiveness
- Navigate to **Module 04: Assessment Engine** (`/assessments`).
- Display an active assessment session with granular question-to-CLO mappings.
- Emphasize **Digital Trust & Student Privacy**:
  - Answer keys are withheld on the server side.
  - Attentiveness telemetry monitors platform engagement latency without intrusive webcam, microphone, or biometric tracking.

### Minute 3:00–4:00 — Learning Mastery Analytics (Beyond Marks)
- Navigate to **Module 05: Mastery Analytics** (`/mastery`).
- Contrast Student 1 (Aarav Sharma) and Student 2 (Riya Sen):
  - Both scored $> 80\%$ on their mid-term test.
  - However, the topic mastery radar reveals Riya has **zero evidence** for B-Trees and Graph Algorithms.
  - MASTERY preserves explicit `NULL` rather than coercing unassessed topics to zero or assuming false competence.

### Minute 4:00–5:00 — Time-Bounded Explainable Academic Risk
- Navigate to **Module 06: Academic Risk** (`/risk`).
- Show Student 3 (Kabir Mehta): High Risk ($p = 0.84$).
- Highlight the **Explainability Decomposition**:
  - MASTERY does not output a black-box probability.
  - It attributes risk directly to directional features: 62% attendance and persistent deficit in Graph Traversal.
- Show Student 4 (Neha Patel): Classified as `INSUFFICIENT_EVIDENCE` rather than receiving a punitive high-risk or failing prediction.

### Minute 5:00–6:00 — Personalized Academic Intervention
- Navigate to **Module 07: Academic Interventions** (`/interventions`).
- Show the intervention assigned to Sneha Rao (`ACTIVE`).
- Highlight **Human-in-the-Loop Governance**:
  - Interventions cannot be issued automatically by an algorithm.
  - A faculty member must approve the objective and blueprint.
- View the append-only progress log showing student code submission and faculty verification.

### Minute 6:00–6:30 — Career Readiness & The Placement Firewall
- Navigate to **Module 08: Career Readiness** (`/career-readiness`).
- Inspect Student 9 (Tanmay Deshmukh) against the **Software Development Engineer - Backend** role.
- Notice the separate metrics: **94% Core Competency Coverage** vs **98% Practical Project Coverage** (Raft consensus engine).
- **DEMONSTRATE THE CRITICAL FIREWALL:**
  - Switch perspective to **Placement Officer** (`placement@siat.edu`).
  - Show that the Placement Officer can view candidate skill alignment pipelines.
  - Try to access student risk predictions or confidential academic interventions: The system returns a strict `HTTP 403 Forbidden` firewall rejection!

### Minute 6:30–7:00 — Unified Intelligence Dashboard & Conclusion
- Navigate to **Unified Intelligence Dashboard** (`/dashboard`).
- Use the **Administrative Perspective Switcher** in the top bar to seamlessly transition between:
  - **Student View:** Self-growth checklist and verified achievements.
  - **Faculty View:** Teaching load, mastery distribution, and approval queue.
  - **Placement Officer View:** Ethical career matching without academic stigma.
  - **Dean / Institution Admin View:** Executive institutional health metrics.
- Conclude with MASTERY's core principle: **"Evidence before prediction. Human oversight before action. Digital trust at every layer."**

---

## 4. Troubleshooting & FAQ

1. **Database connection probe fails:** Verify `DATABASE_URL` in `backend/.env`. If running without live Supabase, tests and mock endpoints degrade gracefully in standalone mode.
2. **Missing demonstration students in frontend:** Run `python scripts/seed_demo_data.py` to populate all 10 synthetic personas.
3. **Frontend fails to fetch API:** Ensure FastAPI server is running on `http://localhost:8000` with `CORS_ORIGINS=["http://localhost:5173"]`.
