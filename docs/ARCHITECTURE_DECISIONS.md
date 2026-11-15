# MASTERY — Architecture Decision Records (ADR)

This document records the foundational technical and architectural decisions for the MASTERY platform, including context, alternatives considered, and rationale.

---

## ADR-001: Adoption of Modular Monolith over Microservices
- **Status:** Accepted
- **Context:** MASTERY consists of seven interconnected business domains (Academic Data, Syllabus, Assessment, Mastery, Risk, Interventions, Career). The engineering team must deliver high velocity and high data consistency within hackathon constraints.
- **Alternatives Considered:**
  1. *Microservices Architecture:* High operational overhead, complex distributed transactions, cross-service schema duplication, and severe deployment friction for local and hackathon evaluation.
  2. *Unstructured Monolith:* Rapid development initially, but leads to circular spaghetti dependencies between assessment, risk, and career domains.
- **Decision:** Implement a **Modular Monolith**. Each domain lives in isolated directory trees (`app/services/*`, `frontend/src/features/*`) with clear boundaries, shared core infrastructure, and decoupled interfaces.
- **Consequences:** Low deployment complexity, zero network latency between modules, and clean refactoring boundaries for future service extraction if necessary.

---

## ADR-002: Strict Isolation of the Three Intelligence Outputs
- **Status:** Accepted
- **Context:** Educational analytics platforms often collapse attendance, exam grades, and coding tests into one arbitrary aggregate score (e.g., "Student Score: 78%").
- **Alternatives Considered:**
  1. *Single Aggregate Metric:* Easy to display on a simple chart, but obscures whether a student has an academic risk, a conceptual learning gap, or a career skill deficiency.
- **Decision:** Mandate three distinct, unmerged intelligence outputs:
  1. **Academic Risk Score:** Institutional compliance and failure-risk early warning.
  2. **Demonstrated Topic Mastery:** Curriculum-level verified conceptual understanding.
  3. **Career Readiness Radar:** Practical technical competencies mapped to industry role benchmarks.
- **Consequences:** Protects actionable diagnostic signal; prevents misleading assessments.

---

## ADR-003: Pure ASGI Middleware for Access Logging & Timing
- **Status:** Accepted
- **Context:** Standard FastAPI `@app.middleware("http")` relies on Starlette's `BaseHTTPMiddleware`, which wraps requests in `anyio` task groups. In Windows environments and modern Python runtime threading contexts, `BaseHTTPMiddleware` can experience threadpool deadlocks on synchronous/concurrent tasks.
- **Alternatives Considered:**
  1. *Starlette `BaseHTTPMiddleware`:* Prone to event loop deadlocks in Windows Python subshells.
  2. *Omitting access logging middleware:* Leaves API calls unmeasured.
- **Decision:** Implement a lightweight, pure ASGI middleware (`ProcessTimeLoggingMiddleware`) that wraps ASGI `scope`, `receive`, and `send` directly.
- **Consequences:** Eliminates deadlock risk, lowers overhead, and guarantees process-time reporting on all HTTP responses.

---

## ADR-004: Graceful Degradation Without Startup API Credentials
- **Status:** Accepted
- **Context:** The application must boot immediately in fresh environments without crashing if `DATABASE_URL` or `OPENAI_API_KEY` are not yet configured.
- **Alternatives Considered:**
  1. *Fail-Fast on Missing Secrets:* Causes application crashes on clean checkouts or in local frontend preview modes.
  2. *Mocking Secrets with Hardcoded Fakes:* Violates engineering principles and risks credential leakage.
- **Decision:** Implement on-demand client instantiation with explicit health probe statuses:
  - If `DATABASE_URL` is unset, `GET /api/v1/health/database` returns HTTP 200 with `status: "unconfigured"`.
  - The API health check never falsely reports external services as operational when they are unconfigured.
- **Consequences:** Zero-friction onboarding for evaluators; completely auditable configuration state.

---

## ADR-005: Strict Separation of Generative AI from Predictive ML
- **Status:** Accepted
- **Context:** Academic risk scoring must be explainable, deterministic, and auditable. Generative LLMs are prone to hallucination, non-determinism, and opacity when asked to perform statistical classification.
- **Alternatives Considered:**
  1. *Prompting an LLM to predict student dropouts:* Non-deterministic, unexplainable, expensive, and ethically hazardous.
- **Decision:**
  - `app/services/ai`: Dedicated solely to unstructured curriculum PDF processing, question drafting, and remedial text phrasing with Pydantic JSON validation.
  - `app/services/ml`: Dedicated solely to classical predictive classification (Logistic Regression, Random Forest) trained on verified historical academic records with transparent feature attributions.
- **Consequences:** Ensures full scientific auditability and compliance with ethical AI requirements.

---

## ADR-006: Frontend Server State Management with TanStack Query
- **Status:** Accepted
- **Context:** Academic dashboards require frequent health polling, status invalidation, and background synchronization without cluttered global React state.
- **Alternatives Considered:**
  1. *Redux Toolkit:* Excessive boilerplate for simple server-state fetching and caching.
  2. *Plain useEffect hooks:* Prone to memory leaks, race conditions, and lack of automatic background re-probing.
- **Decision:** Standardize on **TanStack Query (React Query v5)** with custom query hooks and centralized API client abstractions.
- **Consequences:** Clean UI components, automated background health checks, and declarative loading/error states.
