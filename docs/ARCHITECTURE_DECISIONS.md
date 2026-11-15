# MASTERY — Architecture Decision Records (ADR)

This document records the foundational technical and architectural decisions for the MASTERY platform, including context, alternatives considered, and rationale.

---

## ADR-001: Adoption of Modular Monolith over Microservices
- **Status:** Accepted
- **Context:** MASTERY consists of seven interconnected business domains. The engineering team must deliver high velocity and high data consistency within hackathon constraints.
- **Decision:** Implement a **Modular Monolith**. Each domain lives in isolated directory trees with clear boundaries, shared core infrastructure, and decoupled interfaces.
- **Consequences:** Low deployment complexity, zero network latency between modules, and clean refactoring boundaries.

---

## ADR-002: Strict Isolation of the Three Intelligence Outputs
- **Status:** Accepted
- **Context:** Educational analytics platforms often collapse attendance, exam grades, and coding tests into one arbitrary aggregate score.
- **Decision:** Mandate three distinct, unmerged intelligence outputs:
  1. **Academic Risk Score:** Institutional compliance and failure-risk early warning.
  2. **Demonstrated Topic Mastery:** Curriculum-level verified conceptual understanding.
  3. **Career Readiness Radar:** Practical technical competencies mapped to industry role benchmarks.
- **Consequences:** Protects actionable diagnostic signal; prevents misleading assessments.

---

## ADR-003: Pure ASGI Middleware for Access Logging & Timing
- **Status:** Accepted
- **Context:** Starlette's `BaseHTTPMiddleware` wraps requests in `anyio` task groups, causing threadpool deadlocks on Windows Python subshells.
- **Decision:** Implement a lightweight, pure ASGI middleware (`ProcessTimeLoggingMiddleware`) that wraps ASGI `scope`, `receive`, and `send` directly.
- **Consequences:** Eliminates deadlock risk, lowers overhead, and guarantees process-time reporting on all HTTP responses.

---

## ADR-004: Graceful Degradation Without Startup API Credentials
- **Status:** Accepted
- **Context:** The application must boot immediately in fresh environments without crashing if `DATABASE_URL` or `OPENAI_API_KEY` are not yet configured.
- **Decision:** Implement on-demand client instantiation with explicit health probe statuses. The API health check never falsely reports external services as operational when they are unconfigured.
- **Consequences:** Zero-friction onboarding for evaluators; completely auditable configuration state.

---

## ADR-005: Strict Separation of Generative AI from Predictive ML
- **Status:** Accepted
- **Context:** Academic risk scoring must be explainable, deterministic, and auditable. Generative LLMs are prone to hallucination, non-determinism, and opacity when asked to perform statistical classification.
- **Decision:**
  - `app/services/ai`: Dedicated solely to unstructured curriculum PDF processing, question drafting, and remedial text phrasing with Pydantic JSON validation.
  - `app/services/ml`: Dedicated solely to classical predictive classification trained on verified historical academic records with transparent feature attributions.
- **Consequences:** Ensures full scientific auditability and compliance with ethical AI requirements.

---

## ADR-006: Frontend Server State Management with TanStack Query
- **Status:** Accepted
- **Context:** Academic dashboards require frequent health polling, status invalidation, and background synchronization without cluttered global React state.
- **Decision:** Standardize on **TanStack Query (React Query v5)** with custom query hooks and centralized API client abstractions.
- **Consequences:** Clean UI components, automated background health checks, and declarative loading/error states.

---

## ADR-007: Cryptographic JWT Verification via Supabase JWKS (ES256)
- **Status:** Accepted (Phase 02)
- **Context:** Supabase projects now default to asymmetric ECDSA keys (`ES256`) rather than legacy symmetric HS256 shared secrets. Backend JWT validation must verify genuine signatures from Supabase Auth without trusting arbitrary client tokens.
- **Alternatives Considered:**
  1. *Decoding tokens without verification:* Critical security vulnerability allowing role spoofing.
  2. *Hardcoding a static public key:* Fails when Supabase rotates keys.
- **Decision:** Integrate `jwt.PyJWKClient` pointing dynamically to `https://<ref>.supabase.co/auth/v1/.well-known/jwks.json` with key caching. Fallback to `SUPABASE_SECRET_KEY` for symmetric tokens.
- **Consequences:** Automatic rotation support, zero reliance on insecure legacy secrets, and robust cryptographic verification.

---

## ADR-008: Dual-Layer Database Security & Non-Privilege Escalation
- **Status:** Accepted (Phase 02)
- **Context:** Registration requests originate from public clients. Users must never be able to assign themselves administrative roles or bypass institutional approval.
- **Alternatives Considered:**
  1. *Trusting user metadata supplied in signup form:* Enables trivial privilege escalation to `SUPER_ADMIN`.
- **Decision:**
  1. Public signups are forced to `STUDENT` role and `PENDING` account status.
  2. `handle_new_user()` database trigger uses `SECURITY DEFINER` and enforces default role assignment.
  3. `PATCH /api/v1/users/me` strictly filters to `full_name`, `phone`, and `avatar_url`.
  4. Backend checks user role and institution scope on every protected endpoint.
  5. Row-Level Security (RLS) is enabled on `institutions`, `profiles`, and `institution_memberships`.
- **Consequences:** Complete multi-tenant isolation and defense-in-depth across frontend, API gateway, and database tiers.
