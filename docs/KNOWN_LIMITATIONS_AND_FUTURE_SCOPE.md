# MASTERY — Known Limitations & Future Scope
## Transparent Prototype Boundaries, Technical Debt Analysis & Post-Hackathon Roadmap

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Track:** AI, CyberSecurity and Digital Trust  
**Phase:** 11/11 — Final Platform Hardening & Release Preparation  

---

## 1. Explicit Statement of Prototype Boundaries

In keeping with the track's commitment to **Digital Trust and Scientific Integrity**, this document explicitly outlines the technical limitations, design boundaries, and areas where MASTERY operates as an advanced prototype rather than a fully scaled commercial enterprise deployment.

---

## 2. Technical Limitations & Accepted Trade-offs

### 2.1 AI Provider Independence & Graceful Degradation
- **Current Architecture:** MASTERY is designed to be **100% functional without an external LLM provider**. All cognitive mastery algorithms, Bloom's taxonomy calculators, academic risk classifiers (L2 Logistic Regression / Decision Tree), and career alignment vectors execute deterministically using standard mathematical and heuristic engines.
- **Limitation:** While optional OpenAI API integration is supported in `backend/app/services/syllabus/`, syllabus parsing falls back to deterministic PyMuPDF regex extractors when an API key is omitted. These heuristics work effectively on standard university syllabi (e.g., VTU, SPPU, Mumbai University), but may require manual review for non-standard syllabus formats.

### 2.2 Machine Learning Sample Size & Readiness Gates
- **Dataset Readiness Gate:** The Academic Risk Engine mandates a minimum of 50 historical student records before training predictive statistical models. In small institutions or initial deployments where training cohorts are $< 50$, the system automatically and transparently falls back to calibrated expert pedagogical rules.
- **Limitation:** The current hackathon demonstration utilizes synthetic cohorts ($N=10$ demonstration students and $N=30$ benchmark profiles). Production training requires longitudinal institutional data spanning multiple academic semesters.

### 2.3 Row-Level Security (RLS) Service-Role Execution
- **Current Architecture:** All 57 application tables have PostgreSQL Row-Level Security enabled. However, because the FastAPI backend communicates with Supabase PostgreSQL using a pooled database connection string (`DATABASE_URL`), database queries execute with service-role privileges.
- **Mitigation:** The application mirrors and strictly enforces tenant, role, and student self-isolation checks programmatically within FastAPI route dependencies (`get_current_user`, `require_roles`, `_assert_not_placement_officer`). Direct client-to-Supabase connections would require passing the caller's JWT directly to PostgreSQL via PostgREST.

### 2.4 Frontend Bundle Optimization
- **Current Bundle Size:** The production JavaScript bundle is `839.91 kB` uncompressed (`207.12 kB` gzipped).
- **Limitation:** While completely functional, Vite issues a build warning regarding chunks exceeding 500 kB. Implementing dynamic route splitting (`React.lazy`) is scheduled for future performance polish.

### 2.5 Placement Officer Data Boundary
- **Current Implementation:** Placement Officers are strictly blocked from accessing `/api/v1/dashboard/student/overview`, `/api/v1/dashboard/student/risk-summary`, and `/api/v1/dashboard/student/intervention-summary` (enforced with `HTTP 403 Forbidden`).
- **Limitation:** While firewalled programmatically, institutional policies must also govern physical interview processes to ensure recruiters do not informally request transcripts that reveal remedial intervention notes.

---

## 3. Post-Hackathon Architectural Roadmap

```
+---------------------------------------------------------------------------------------+
|                              MASTERY FUTURE ARCHITECTURE ROADMAP                      |
+--------------------+------------------------------------------------------------------+
| Milestone          | Scope & Planned Capabilities                                     |
+--------------------+------------------------------------------------------------------+
| **Milestone 1**    | **LTI 1.3 LMS Integration:** Native Canvas, Moodle, and Blackboard|
|                    | plugins for automated gradebook and assessment synchronization.  |
| **Milestone 2**    | **Temporal Clickstream Neural Models:** Sequence-aware LSTM and  |
|                    | Transformer models for subtle, non-invasive early warning signals.|
| **Milestone 3**    | **Verifiable Credentials (W3C Standards):** Cryptographically    |
|                    | signed verifiable mastery credentials stored on digital wallets.  |
| **Milestone 4**    | **Native Mobile PWA:** Offline-first mobile interface for student|
|                    | action checklists and notification alerts.                       |
| **Milestone 5**    | **Explainable AI Fairness Audits:** Continuous disparate impact  |
|                    | monitoring to guarantee algorithmic fairness across demographics.|
+--------------------+------------------------------------------------------------------+
```

---

## 4. Closing Scientific Governance Principle

MASTERY maintains that **no algorithmic prediction should ever be treated as a definitive sentence of academic failure or human capability**. Predictive indicators are early signals intended to mobilize faculty guidance, institutional support, and student self-agency.
