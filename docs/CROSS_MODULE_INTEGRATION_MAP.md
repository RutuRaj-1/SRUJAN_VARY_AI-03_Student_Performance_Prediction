# MASTERY — Cross-Module Integration Map
## End-to-End Workflows & Inter-Module Data Provenance

**Platform:** MASTERY — Beyond Marks. Towards Mastery.  
**Team:** VARY — SRUJAN 2026  
**Problem Statement:** AI-03 — Student Performance Prediction  
**Track:** AI, CyberSecurity and Digital Trust  
**Phase:** 10/11 — Unified Intelligence Dashboard & Cross-Module Integration  

---

## 1. Cross-Module Workflow Architectures

Phase 10 connects the seven business modules through verified, explainable workflows.

### Workflow A: Curriculum to Learning Mastery

```mermaid
flowchart TD
    Syllabus["Module 02: Approved Syllabus & Topics (SyllabusTopic)"]
    CLO["Module 02: Course Learning Outcomes (LearningOutcome)"]
    Assessments["Module 04: Assessment Questions & Attempts (AssessmentAttempt)"]
    AcademicRecords["Module 03: Verified Marks (StudentAssessmentRecord)"]
    Analytics["Module 05: Deterministic Calibration Engine (MasteryAnalysisJob)"]
    MasteryResults["Module 05: Topic Mastery (TopicMasteryResult)"]
    Attainment["Module 05: CLO Attainment (LearningOutcomeAttainmentResult)"]
    Gaps["Module 05: Flagged Gaps (LearningGapFinding)"]

    Syllabus & CLO --> Assessments
    Assessments & AcademicRecords --> Analytics
    Analytics --> MasteryResults & Attainment & Gaps
```

- **Data Guarantee:** Mastery calculations require that every assessment question references valid syllabus topics and CLOs approved in Module 02.
- **Traceability:** Downstream attainment records reference the exact curriculum regulation version.

---

### Workflow B: Learning Mastery to Academic Risk

```mermaid
flowchart TD
    VerifiedRecords["Module 03: Attendance & Internal Marks"]
    MasteryGaps["Module 05: Topic Mastery Deficits & Gaps"]
    FeatureSnapshot["Module 06: Time-Bounded Feature Snapshot (RiskFeatureSnapshot)"]
    Validator["Module 06: Temporal Leakage Validator"]
    ModelEngine["Module 06: Statistical Inference (RiskModelVersion)"]
    Prediction["Module 06: Academic Risk Prediction (AcademicRiskPrediction)"]
    Explanation["Module 06: Feature Explanations (AcademicRiskPredictionExplanation)"]

    VerifiedRecords & MasteryGaps --> FeatureSnapshot
    FeatureSnapshot --> Validator
    Validator --> ModelEngine
    ModelEngine --> Prediction
    Prediction --> Explanation
```

- **Data Guarantee:** All feature extraction strictly precedes the prediction cutoff date.
- **Explainability:** Predictions are accompanied by specific adverse and protective factors grounded in actual student attendance and assessment history.

---

### Workflow C: Academic Risk to Personalized Intervention

```mermaid
flowchart TD
    RiskPrediction["Module 06: High/Moderate Risk Prediction"]
    TopicGaps["Module 05: Flagged Learning Gaps"]
    RecEngine["Module 07: Recommendation Engine (InterventionRecommendation)"]
    FacultyReview["Module 07: Human-in-the-Loop Faculty Review"]
    SupportPlan["Module 07: Approved Support Plan (AcademicInterventionPlan)"]
    StudentActions["Module 07: Action Items & Practice Labs"]
    Observations["Module 07: Observational Outcome Tracking"]

    RiskPrediction & TopicGaps --> RecEngine
    RecEngine --> FacultyReview
    FacultyReview --> SupportPlan
    SupportPlan --> StudentActions
    StudentActions --> Observations
```

- **Human-in-the-Loop:** Automated recommendations do not become active plans without explicit faculty approval and assignment.
- **Non-Causal Monitoring:** Post-intervention performance improvements are documented as observational associations, not causal proofs.

---

### Workflow D: Curriculum to Career Readiness

```mermaid
flowchart TD
    CurriculumCompetencies["Module 02: Academic Competencies"]
    RoleFrameworks["Module 08: Industry Role Requirements (Bloom Depth 1-5)"]
    EvidenceLedger["Module 08: Multi-Modal Competency Evidence Ledger"]
    TopicMastery["Module 05: Demonstrated Topic Mastery"]
    CodingAssessments["Module 04: Practical Evaluation Submissions"]
    StudentProjects["Module 08: Verified Practical Projects (GitHub / Live)"]
    AnalysisEngine["Module 08: Career Readiness Analysis Engine"]
    SkillGaps["Module 08: 5-Tier Skill Gap Discovery"]
    Recommendations["Module 08: Career Development Roadmaps"]

    CurriculumCompetencies & RoleFrameworks --> EvidenceLedger
    TopicMastery & CodingAssessments & StudentProjects --> EvidenceLedger
    EvidenceLedger --> AnalysisEngine
    AnalysisEngine --> SkillGaps & Recommendations
```

- **Separation of Metrics:** Core competency coverage is reported separately from practical project coverage. No single composite employability percentage is ever generated.

---

### Workflow E: Integrated Student Journey

```mermaid
flowchart LR
    Records["1. Academic Records (Module 03)"]
    Assessments["2. Assessments (Module 04)"]
    Mastery["3. Topic Mastery (Module 05)"]
    Risk["4. Risk Screening (Module 06)"]
    Interventions["5. Support Plans (Module 07)"]
    Career["6. Career Readiness (Module 08)"]

    Records --> Assessments --> Mastery --> Risk --> Interventions --> Career
```

- **Navigation & Transparency:** The unified dashboard synthesizes these six stages into clear cards with explicit module provenance, timestamped freshness, and direct navigational links.
