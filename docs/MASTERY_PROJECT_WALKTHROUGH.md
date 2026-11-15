# MASTERY End-to-End Project Walkthrough Guide

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Track:** AI, CyberSecurity and Digital Trust  

---

## Presentation Executive Summary

MASTERY is designed to solve a foundational flaw in modern educational technology: **academic systems treat student learning as a series of isolated marks and attendance percentages rather than an evolving, evidence-based mastery journey.**

This walkthrough guides evaluators and hackathon judges through the complete academic intelligence lifecycle across all seven integrated modules:

```text
[Step 1] Public Product Showcase (/)
    ↓
[Step 2] Unified Role-Aware Dashboard (/app/dashboard)
    ↓
[Step 3] Module 01: Academic Data Intelligence Hub (/app/academic-data)
    ↓
[Step 4] Module 02: AI Syllabus & Competency Intelligence (/app/syllabus)
    ↓
[Step 5] Module 03: Intelligent Assessment & Attentiveness Engine (/app/assessments)
    ↓
[Step 6] Module 04: Learning Mastery & Performance Analytics (/app/mastery)
    ↓
[Step 7] Module 05: Academic Risk Prediction Engine (/app/risk)
    ↓
[Step 8] Module 06: Personalized Academic Intervention (/app/interventions)
    ↓
[Step 9] Module 07: Career Readiness & Industry Skill Gap (/app/career-readiness)
    ↓
[Step 10] Ethical AI, Privacy Boundaries & Security Summary
```

---

## Step-by-Step Demonstration Sequence

### Step 1: Public Product Landing Page (`/`)
- **What to Demonstrate:** 
  - Showcase the headline: *"Beyond Marks. Towards Mastery."*
  - Review the 6 structural limitations of legacy academic reporting (fragmented records, disconnected syllabi, scores concealing gaps, late detection, ad-hoc remediation, career misalignment).
  - Walk through the 7-step solution pipeline and the interactive Technical Architecture diagram.
  - Emphasize the core differentiators: temporal leakage prevention, sufficiency checks, human-in-the-loop verification, and the Placement Officer privacy firewall.
- **Presenter Narration:**
  > "Welcome to MASTERY. In conventional universities, a student who scores 65% is treated as average, yet that score hides whether they mastered core data structures or failed fundamental algorithms. Traditional systems only sound the alarm after a student fails an end-semester exam. MASTERY transforms raw academic data into structured learning evidence, predicts difficulty before it becomes failure, provides faculty-supervised interventions, and bridges student competencies with industry role expectations."
- **Action:** Click the primary CTA **"Explore the Platform"** to launch the interactive workspace.

---

### Step 2: Unified Intelligence Dashboard (`/app/dashboard`)
- **What to Demonstrate:**
  - The multi-persona perspective switcher (Student, Faculty, Institution Admin, Placement Officer, Platform Admin).
  - High-level cohort health: Enrolled Students, Sufficient Evidence Rate, Active Interventions, Outcome Attainment.
  - Scenario Selector: Switch between Scenario A (Aarav), Scenario B (Diya), Scenario C (Rohan), and Scenario D (Ananya).
- **Presenter Narration:**
  > "We are now inside the Unified Dashboard. Rather than generating a single arbitrary composite number, MASTERY keeps learning mastery, academic risk, and career readiness in separate, traceable dimensions. Notice that the institution administrator sees cohort-level health, while students see their individual progress."

---

### Step 3: Module 01 — Academic Data Intelligence Hub (`/app/academic-data`)
- **What to Demonstrate:**
  - The verified student directory, attendance ledgers, and assessment records.
  - Two-phase import workflow (preview → validation → faculty verification).
  - Quality scan findings detecting anomalous or unverified marks.
- **Presenter Narration:**
  > "Reliable intelligence begins with reliable evidence. Module 01 acts as the verifiable academic ledger. Every record distinguishes between verified, unverified, excused, and absent records, providing a tamper-evident audit trail."

---

### Step 4: Module 02 — AI Syllabus & Competency Intelligence (`/app/syllabus`)
- **What to Demonstrate:**
  - Automated extraction of Course Learning Outcomes (CLOs), units, topics, and Bloom cognitive taxonomy levels from official syllabus PDFs.
  - Faculty verification status and competency mappings.
- **Presenter Narration:**
  > "Before we can evaluate what a student has learned, we must structure what was taught. Module 02 transforms unstructured PDF syllabi into machine-readable competencies linked directly to course learning outcomes."

---

### Step 5: Module 03 — Intelligent Assessment & Attentiveness Engine (`/app/assessments`)
- **What to Demonstrate:**
  - Question bank mapped to Bloom's taxonomy (Remember, Understand, Apply, Analyze, Evaluate, Create).
  - Student assessment attempt view with structured feedback.
  - Observable interaction telemetry (session interactions, tab focus events).
  - Explicit disclaimer: engagement events are strictly observational and never used as facial surveillance or direct proxy for intelligence.
- **Presenter Narration:**
  > "Assessments in MASTERY are not just mark generators; they generate tagged evidence items. Each question is tied to specific topics and cognitive levels, allowing the system to measure topic-level evidence rather than generic score percentages."

---

### Step 6: Module 04 — Learning Mastery & Performance Analytics (`/app/mastery`)
- **What to Demonstrate:**
  - Topic mastery status: `MASTERED`, `PROGRESSING`, `NEEDS_ATTENTION`, `INSUFFICIENT_EVIDENCE`.
  - Course Learning Outcome attainment percentages.
  - Evidence sufficiency gauges: missing assessments are never assumed to be zero.
- **Presenter Narration:**
  > "Module 04 calculates evidence-based mastery. Here in Scenario C (Rohan Gupta), we see that while he understands Basic Arrays, he has a critical deficit in Dynamic Programming and Graph Algorithms. In Scenario D (Ananya Sen), the system explicitly flags 'Insufficient Evidence' instead of penalizing her with a zero for her excused medical absence."

---

### Step 7: Module 05 — Academic Risk Prediction Engine (`/app/risk`)
- **What to Demonstrate:**
  - Time-bounded prediction horizon (predicting semester difficulty before midterm cutoffs).
  - Feature contributions: Adverse factors (continuous assessment decline, low attendance) vs Protective factors.
  - Model governance: Logistic Regression / Decision Tree baseline with dataset readiness gates.
- **Presenter Narration:**
  > "Module 05 identifies students requiring academic support. For Rohan, the model flags high risk (78%) because his continuous assessment trajectory has dropped by 35% over the last four weeks. Notice the explanation: the model doesn't just output a number; it lists the exact adverse factors driving the prediction."

---

### Step 8: Module 06 — Personalized Academic Intervention (`/app/interventions`)
- **What to Demonstrate:**
  - Automated recommendation queue generated from identified mastery gaps and risk signals.
  - Faculty review and approval workflow (`DRAFT` → `PENDING_REVIEW` → `APPROVED` → `ACTIVE` → `COMPLETED`).
  - Action plans assigned to the student with clear learning milestones.
- **Presenter Narration:**
  > "Insights without action are useless. Module 06 converts risk signals into faculty-supervised intervention plans. The professor reviews the recommended clinic, adjusts the milestones, and monitors the student's progress."

---

### Step 9: Module 07 — Career Readiness & Industry Skill Gap (`/app/career-readiness`)
- **What to Demonstrate:**
  - Target Industry Roles (Full-Stack Engineer, AI/ML Engineer, Data Systems Engineer).
  - Separation of Academic Competency Coverage vs Practical Project Evidence.
  - 5-Tier Skill Gap discovery and targeted career development recommendations.
- **Presenter Narration:**
  > "Module 07 connects academic progress with employability. Aarav Sharma (Scenario A) has 88% core academic coverage and verified practical projects, while Rohan has specific gaps in database indexing and graph APIs. The student receives personalized recommendations for portfolio projects to bridge these gaps."

---

### Step 10: Ethical AI, Governance & Placement Privacy Firewall
- **What to Demonstrate:**
  - Switch the persona to **Placement Officer**.
  - Navigate to `/app/risk`.
  - Demonstrate that the **Placement Officer Privacy Firewall** blocks risk access with an explicit ethical charter notice.
- **Presenter Narration:**
  > "To ensure digital trust and ethical compliance, MASTERY enforces strict algorithmic firewalls. Placement Officers have access to verified competencies and project portfolios, but are completely barred from seeing academic risk predictions or intervention histories. Academic risk is a tool for student support, never an excuse for algorithmic hiring discrimination."
