# MASTERY Video Demonstration Scripts
## Official Pitch & Technical Evaluation Narration

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Track:** AI, CyberSecurity and Digital Trust  

---

# PART A: SHORT VERSION — 3 MINUTES (HACKATHON QUICK PITCH)

### 00:00 – 00:35 | Opening & The Problem
- **Screen:** Public Landing Page (`/`)
- **Action:** Scroll smoothly past Hero to Problem Statement section.
- **Narration:**
  > "Hello evaluators. In universities today, student performance is measured by marks, attendance, and end-semester exams. But a grade of 65% conceals critical gaps: did the student master data structures, or did they fail recursion? Most dangerously, academic difficulty is discovered only after semester failure. We built **MASTERY: Beyond Marks. Towards Mastery.** MASTERY is an evidence-driven academic intelligence platform connecting seven integrated modules from curriculum extraction to career readiness."
- **Key Takeaway:** Traditional marks obscure learning gaps and sound the alarm too late.

### 00:35 – 01:20 | The Unified Dashboard & 4 Scenarios
- **Screen:** `/app/dashboard`
- **Action:** Click "Explore Demo". Show the top toolbar. Click through Scenario A (Aarav) and Scenario C (Rohan).
- **Narration:**
  > "Inside the Unified Dashboard, MASTERY separates learning mastery, academic risk, and career readiness rather than fabricating a single composite score. In Scenario A, Aarav demonstrates high topic mastery and low risk. But when we switch to Scenario C, Rohan Gupta, the platform reveals an emerging risk of 78%. Why? Because our time-bounded model detected a 35% drop in continuous assessment scores over the last month."
- **Key Takeaway:** Multi-dimensional tracking with explainable, time-bounded risk signals.

### 01:20 – 02:15 | From Risk to Supervised Intervention
- **Screen:** `/app/mastery` then `/app/interventions`
- **Action:** Show Rohan's topic gap in Dynamic Programming, then navigate to Interventions to show the approved Faculty Support Plan.
- **Narration:**
  > "In Mastery Analytics, we see the exact topic causing Rohan's difficulty: Dynamic Programming. Immediately, Module 06 converts this gap into an actionable, faculty-supervised academic intervention. His advisor approves a targeted lab clinic with clear milestones. Notice that interventions are never automated punishments; they require human-in-the-loop verification."
- **Key Takeaway:** Human-supervised closed-loop support turns diagnostic insights into recovery.

### 02:15 – 03:00 | Career Readiness & The Ethical Firewall
- **Screen:** `/app/career-readiness`, then switch role to **Placement Officer** and click `/app/risk`.
- **Action:** Show Career Readiness competency radar, switch persona to Placement Officer, attempt to open Risk page, and display the firewall block.
- **Narration:**
  > "Finally, Module 07 aligns verified academic and practical competencies with industry roles like Full-Stack and AI Engineer. But digital trust requires ethical boundaries. When our user switches to the Placement Officer role, they can view verified portfolio skills, but our privacy firewall completely blocks access to academic risk scores. Risk is for student support, never for hiring discrimination. MASTERY: Beyond Marks. Towards Mastery."
- **Key Takeaway:** Ethical AI boundary prevents algorithmic recruitment bias.

---

# PART B: STANDARD VERSION — 5 TO 7 MINUTES (JURY DEMO)

### [00:00 – 01:00] Step 1: Introduction & The Core Philosophy
- **Route:** `/`
- **Visuals:** Public Landing Page, Hero Section, 7-Stage Intelligence Pipeline.
- **Narration:**
  > "Welcome to the presentation of MASTERY, submitted by Team VARY for Problem Statement AI-03. Traditional educational management systems are historical ledgers—they log attendance and record examination marks. But they fail to answer fundamental educational questions: Which specific syllabus topics did a student master? Which competencies have sufficient assessment evidence? And how can faculty intervene before an academic failure occurs?
  > MASTERY redefines this journey across seven integrated modules: from automated syllabus extraction to career skill gap analysis, all anchored in verifiable evidence."

### [01:00 – 02:00] Step 2: The Foundation — Academic Data & AI Syllabus
- **Route:** `/app/academic-data` then `/app/syllabus`
- **Visuals:** Student Directory, Quality Findings, Syllabus Unit & CLO Extraction.
- **Narration:**
  > "We begin in Module 01, the Academic Data Intelligence Hub. Here, institutions import attendance and internal exam records through a two-phase validation workflow. Notice our data quality scanner, which detects unverified marks or attendance anomalies before data enters the intelligence engine.
  > Moving to Module 02, the AI Syllabus Engine parses curriculum documents into Course Learning Outcomes, units, and Bloom's cognitive taxonomy levels. You cannot evaluate what a student has learned until you have structured what was taught."

### [02:00 – 03:30] Step 3: Assessment Telemetry & Explainable Mastery
- **Route:** `/app/assessments` then `/app/mastery`
- **Visuals:** Question Bank, Bloom distribution, Scenario C (Rohan Gupta) vs Scenario D (Ananya Sen).
- **Narration:**
  > "Module 03 delivers assessments mapped to Bloom's taxonomy. Every student response creates granular evidence tagged to topics. 
  > In Module 04, Learning Mastery Analytics transforms this evidence into topic attainment. Let's look at Scenario C, Rohan Gupta. Rohan has mastered basic array operations, but shows a red 'Needs Attention' tag in Dynamic Programming and Graph Algorithms. 
  > Now look at Scenario D, Ananya Sen. Ananya missed assessments due to medical leave. Crucially, MASTERY does not calculate a zero score; it explicitly flags her status as 'Insufficient Evidence', preventing false failure penalties."

### [03:30 – 04:45] Step 4: Academic Risk Engine & Personalized Interventions
- **Route:** `/app/risk` then `/app/interventions`
- **Visuals:** Time-bounded risk horizon, Adverse vs Protective factor breakdown, Intervention Plan workflow.
- **Narration:**
  > "In Module 05, our Academic Risk Engine evaluates students before critical semester milestones. For Rohan, the model predicts High Risk (78%). Importantly, our system is explainable: the interface details the exact adverse factors—a declining continuous assessment slope of -35% and attendance dropping below the 75% threshold.
  > In Module 06, this insight immediately triggers an Intervention Recommendation. Faculty members review the proposed remediation plan, customize milestones, and track student recovery. It is a complete, human-supervised cycle."

### [04:45 – 06:00] Step 5: Career Readiness & Ethical AI Governance
- **Route:** `/app/career-readiness`, then switch role to Placement Officer and open `/app/risk`.
- **Visuals:** Role Profiles (Full-Stack, Data Systems), Practical Project Evidence Ledger, Privacy Firewall dialog.
- **Narration:**
  > "Module 07 bridges university learning with industry requirements. We evaluate students against market profiles like Full-Stack Engineer and AI Specialist, separating academic exam coverage from practical project evidence.
  > But under the CyberSecurity and Digital Trust track, privacy is paramount. When we switch our persona to Placement Officer, the platform immediately locks out the Academic Risk Engine. Recruiters see verified practical competencies, but student academic risk remains strictly confidential between students and faculty.
  > That is MASTERY: verifiable, explainable, supportive, and ethical."

---

# PART C: DETAILED VERSION — 10 TO 12 MINUTES (TECHNICAL DEEP DIVE)

| Time | Route | Visible Screen Elements | Recommended Actions | Spoken Script & Technical Highlights |
|---|---|---|---|---|
| 00:00–01:30 | `/` | Hero, Architecture Diagram, Differentiators | Scroll to layered system diagram | Explain technical stack: FastAPI modular monolith, PostgreSQL, Supabase RLS, React + Vite frontend, scikit-learn model services, temporal leakage protection. |
| 01:30–02:45 | `/app/dashboard` | Multi-Persona Overview, Metric Cards | Toggle between Student, Faculty, and Admin personas | Contrast institutional aggregate metrics with student-specific feedback. Highlight lack of ungrounded composite metrics. |
| 02:45–04:00 | `/app/academic-data` | Audit Ledger, Validation Center | Click into Student Details and Data Quality Findings | Demonstrate separation of verified, unverified, excused, and absent records. Explain cryptographic audit trail and immutability. |
| 04:00–05:15 | `/app/syllabus` | Unit Breakdown, Bloom's Taxonomy Distribution | Select CS601 (Algorithms), expand units | Explain automated extraction of CLOs and topic-to-competency linkages with faculty verification status. |
| 05:15–06:30 | `/app/assessments` | Question Bank, Student Attempt Interface | Demonstrate question evaluation and observable telemetry | Emphasize ethical telemetry: interaction events are strictly local/observational, with zero intrusive facial/gaze surveillance. |
| 06:30–07:45 | `/app/mastery` | Topic Mastery Grid, CLO Attainment Gauges | Switch between Scenario A (Aarav) and Scenario D (Ananya) | Deep dive into the evidence eligibility algorithm. Missing evidence is never scored as zero; insufficient evidence states are clearly highlighted. |
| 07:45–09:00 | `/app/risk` | ROC-AUC / Model Metrics, Feature Importance Chart | Inspect Rohan Gupta's risk breakdown | Explain time-bounded cutoff policies that prevent data leakage from future final exams. Review deterministic baseline and ML fallback. |
| 09:00–10:15 | `/app/interventions` | Intervention Lifecycle Pipeline | Move plan from `PENDING_REVIEW` to `APPROVED` | Detail the observational nature of intervention tracking: MASTERY never claims unverified causation for student recovery. |
| 10:15–11:30 | `/app/career-readiness` | 5-Tier Skill Gap Matrix, Practical Project Ledger | Select "AI/ML Engineer" profile | Review core vs elective competencies and practical GitHub/lab portfolio verification by faculty. |
| 11:30–12:00 | `/app/risk` (as Placement) | Placement Firewall Lockout Screen | Switch persona to Placement Officer | Conclude on Digital Trust: strict algorithmic firewall prevents recruitment discrimination. |
