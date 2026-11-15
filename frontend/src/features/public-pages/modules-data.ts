import {
  Database,
  Layers,
  FileCheck2,
  LineChart,
  ShieldAlert,
  Brain,
  Compass,
} from 'lucide-react';

export interface ModuleData {
  slug: string;
  code: string;
  num: string;
  title: string;
  tagline: string;
  description: string;
  problemSolved: string;
  icon: any;
  accent: string;
  badgeColor: string;
  appRoute: string;
  coreCapabilities: string[];
  inputs: string[];
  outputs: string[];
  evidenceGovernance: string;
  technicalArchitecture: string;
  academicImpact: string;
}

export const MODULES_DATA: ModuleData[] = [
  {
    slug: 'syllabus',
    code: 'M01',
    num: '01',
    title: 'AI Syllabus & Competency Intelligence',
    tagline: 'Deterministic parsing of unstructured syllabi into canonical topic hierarchies & prerequisite DAGs.',
    description:
      'Transforms unstructured university course syllabi, curriculum handbooks, and textbook tables of contents into canonical Directed Acyclic Graphs (DAGs) of topics, sub-topics, prerequisites, and Bloom’s Taxonomy-indexed Course Learning Outcomes (CLOs).',
    problemSolved:
      'Curricula are historically trapped in unstructured PDFs and Word documents. Prerequisite dependencies are implicit, leading to hidden knowledge debt and unaligned exam questions.',
    icon: Database,
    accent: 'bg-primary/10 text-primary border-primary/20',
    badgeColor: 'primary',
    appRoute: '/app/syllabus',
    coreCapabilities: [
      'Document Ingestion & Multi-Format OCR (PDF, DOCX, Markdown)',
      'Deterministic Directed Acyclic Graph (DAG) Prerequisite Modeling',
      'Bloom’s Revised Taxonomy Cognitive Level Tagging (L1 Remember to L6 Create)',
      'Automated Course Learning Outcome (CLO) to Topic Semantic Linking',
      'Curriculum Version Control & Cryptographic SHA-256 Checksumming',
    ],
    inputs: [
      'Course Syllabus PDF / Word documents',
      'Institutional Academic Regulation handbooks',
      'Prerequisite declaration matrices',
    ],
    outputs: [
      'Canonical Topic Hierarchy (JSON-LD structured graph)',
      'Prerequisite DAG adjacency matrices',
      'CLO-to-Topic semantic alignment weight maps',
    ],
    evidenceGovernance:
      'Every extracted node is pinned to raw source page coordinates and given an immutable cryptographic content digest to guarantee syllabus integrity.',
    technicalArchitecture:
      'FastAPI async parsing microservice leveraging regularized PDF token extraction, graphlib topological sorting, and pgvector semantic topic embedding.',
    academicImpact:
      'Enables institutions to audit prerequisite health across degree programs and ensures every evaluation question directly links to verified learning objectives.',
  },
  {
    slug: 'academic-data',
    code: 'M02',
    num: '02',
    title: 'Academic Data Intelligence Hub',
    tagline: 'Single source of academic truth reconciling SIS, LMS, and biometric records into an immutable audit trail.',
    description:
      'Ingests, validates, and normalizes disparate student records across legacy ERPs, Moodle/Canvas LMS instances, and attendance systems. Enforces rigorous schema constraints and creates unified academic profiles.',
    problemSolved:
      'Student academic history is scattered across isolated databases with inconsistent grade scales, delayed syncs, and no unified historical audit trail.',
    icon: Layers,
    accent: 'bg-secondary/10 text-secondary border-secondary/20',
    badgeColor: 'secondary',
    appRoute: '/app/academic-data',
    coreCapabilities: [
      'Multi-Format Batch Ingestion (CSV, JSON, SIS REST webhooks)',
      'Grade Scale Normalization (Percentage, 10-point SGPA/CGPA, Letter Grades)',
      'Time-Series Attendance Velocity Tracking & Sudden-Drop Alerts',
      'Strict Schema Validation with Row-Level Rejection Auditing',
      'Immutable Historical Academic Ledgers for Institutional Integrity',
    ],
    inputs: [
      'ERP Student Roster & Demographics',
      'Historical Semester Marksheets & Exam Ledgers',
      'Biometric / RFID Attendance Daily Logs',
    ],
    outputs: [
      'Unified Student Master Academic Profile',
      'Standardized 0–100 Normalized Performance Indexes',
      'Attendance Velocity & Trajectory Metrics',
    ],
    evidenceGovernance:
      'Database-level foreign-key integrity constraints, idempotent batch upserts, and append-only audit event logs for complete provenance.',
    technicalArchitecture:
      'PostgreSQL relational schema with transactional batch ingestion workers, pydantic validation pipelines, and Redis caching for instant retrieval.',
    academicImpact:
      'Provides faculty, advisors, and accreditation boards with reliable, tamper-evident student timelines free from data entry artifacts.',
  },
  {
    slug: 'assessments',
    code: 'M03',
    num: '03',
    title: 'Intelligent Assessment & Attentiveness Engine',
    tagline: 'Evidence-backed evaluation across subjective answers, quizzes, and classroom attentiveness telemetry.',
    description:
      'Evaluates student academic performance across formative quizzes, lab assignments, subjective questions, and classroom engagement. Generates rubric-referenced scoring with transparent justifications.',
    problemSolved:
      'Conventional exams produce a single aggregate score without indicating which specific concepts were misunderstood, while classroom attentiveness is entirely unmeasured.',
    icon: FileCheck2,
    accent: 'bg-success/10 text-success border-success/20',
    badgeColor: 'success',
    appRoute: '/app/assessments',
    coreCapabilities: [
      'Multimodal Assessment Authoring (MCQ, Coding, Descriptive, Lab Exercises)',
      'Rubric-Aligned Semantic Evaluation & Automated Grading Suggestions',
      'Bloom’s Taxonomy Cognitive Level Assessment Profiling',
      'Classroom Attentiveness & Interaction Telemetry Synthesizer',
      'Faculty Grading Override with Mandatory Justification Logging',
    ],
    inputs: [
      'Student Assessment Submissions (Text, Code, Test choices)',
      'Faculty Grading Rubrics with Criteria & Point Distributions',
      'Classroom Attendance & Participation Marker Logs',
    ],
    outputs: [
      'Itemized Question-Level Score Vectors',
      'Criterion-by-Criterion Formative Feedback Summaries',
      'Topic-Mapped Assessment Evidence Records',
    ],
    evidenceGovernance:
      'Submissions are timestamped, permanently hashed, and tied to specific rubric criteria before entering mastery computation.',
    technicalArchitecture:
      'Hybrid evaluation pipeline combining deterministic rule-based checks with supervised LLM grading assistance under strict faculty review workflows.',
    academicImpact:
      'Gives students immediate, actionable feedback on exactly what they missed and why, transforming exams from punitive gates into learning milestones.',
  },
  {
    slug: 'mastery',
    code: 'M04',
    num: '04',
    title: 'Learning Mastery & Performance Analytics',
    tagline: 'Transforming marks into granular topic mastery indices and Course Learning Outcome (CLO) attainment.',
    description:
      'Calculates fine-grained mastery scores (0–100%) for every topic in the syllabus by aggregating multi-source evidence. Evaluates Course Learning Outcome (CLO) attainment without masking gaps behind high overall averages.',
    problemSolved:
      'A student can score 75% on an exam while scoring 0% on critical foundational topics like Memory Allocation, causing severe failure in downstream courses.',
    icon: LineChart,
    accent: 'bg-accent/10 text-accent border-accent/20',
    badgeColor: 'accent',
    appRoute: '/app/mastery',
    coreCapabilities: [
      'Topic-Level Mastery Indexing (0–100% Bayesian Evidence Aggregation)',
      'Course Learning Outcome (CLO) Attainment Calculation for NBA/NAAC Accreditation',
      'Bloom’s Cognitive Level Attainment Distribution Breakdown',
      'Foundational Knowledge Debt & Prerequisite Bottleneck Highlighting',
      'Time-Series Mastery Trajectory & Retention Decay Tracking',
    ],
    inputs: [
      'Question-Level Evaluated Assessment Records',
      'Topic-to-CLO Mapping Matrices from Module 01',
      'Student Academic Velocity Metrics from Module 02',
    ],
    outputs: [
      'Granular Topic Mastery Vector per Student and Section',
      'Formal CLO Attainment Scorecards with Target Thresholds',
      'Identified Topic Deficit & Bottleneck Register',
    ],
    evidenceGovernance:
      'Calculations use weighted time-decay Bayesian models where every percentage point maps back to verifiable assessment submissions.',
    technicalArchitecture:
      'Vectorized NumPy/SciPy analytics engine computing rolling competency scores with PostgreSQL historical snapshot tables.',
    academicImpact:
      'Eliminates the "high mark, zero understanding" paradox and provides real-time data for institutional outcome-based education (OBE) accreditation.',
  },
  {
    slug: 'risk',
    code: 'M05',
    num: '05',
    title: 'Academic Risk Prediction Engine',
    tagline: 'Explainable, early risk prediction with transparent factor attribution and ethical privacy firewalls.',
    description:
      'Identifies students at risk of academic failure, semester backlog, or prerequisite stalls weeks in advance. Provides transparent SHAP factor attributions so advisors know exactly what factors drive the risk score.',
    problemSolved:
      'Institutions identify struggling students only after final semester exam failure—when it is too late for corrective remedial instruction.',
    icon: ShieldAlert,
    accent: 'bg-warning/10 text-warning border-warning/20',
    badgeColor: 'warning',
    appRoute: '/app/risk',
    coreCapabilities: [
      'Early Academic Difficulty Prediction (Weeks 3–6 of Semester)',
      'Calibrated Risk Tier Stratification (Low, Moderate, High, Critical)',
      'Transparent Factor Attribution (Attribution weights on Attendance, Topic Deficits, Velocity)',
      'Temporal Risk Trajectory Analysis (Tracking improvement or deterioration)',
      'Privacy Firewall: Strict Access Control (Placement Officers strictly restricted)',
    ],
    inputs: [
      'Topic Mastery Deficit Indices from Module 04',
      'Recent Attendance Velocity & Drop-Off Rates from Module 02',
      'Formative Assessment Trends & Missing Submission Rates',
    ],
    outputs: [
      'Student Academic Risk Classification Tier',
      'Top 3 Contributory Risk Factors with Explainability Weights',
      'Intervention Recommendation Priority Queue for Faculty Advisors',
    ],
    evidenceGovernance:
      'Explanations are strictly derived from verified academic evidence. No demographic, socio-economic, or protected traits are ingested or computed.',
    technicalArchitecture:
      'Interpretable Gradient Boosting & Calibrated Classifier models paired with SHAP (SHapley Additive exPlanations) attribution engines.',
    academicImpact:
      'Enables proactive academic advising, reducing course failure rates and preventing student dropouts before midterms.',
  },
  {
    slug: 'interventions',
    code: 'M06',
    num: '06',
    title: 'Personalized Academic Intervention Engine',
    tagline: 'Faculty-supervised remedial learning plans addressing specific foundational prerequisite gaps.',
    description:
      'Synthesizes personalized remedial learning itineraries targeting identified topic deficits. Features strict Human-in-the-Loop governance: no intervention is dispatched to students without faculty advisor approval.',
    problemSolved:
      'Struggling students receive generic advice like "study harder" rather than concrete, scaffolded learning plans, and faculty lack time to build custom remedial tracks.',
    icon: Brain,
    accent: 'bg-primary/10 text-primary border-primary/20',
    badgeColor: 'primary',
    appRoute: '/app/interventions',
    coreCapabilities: [
      'Automated Scaffolded Remedial Plan Generation for Identified Deficits',
      'Micro-Learning Step Decomposition (Review, Practice, Verification)',
      'Faculty Approval & Modification Workflow (Human-in-the-Loop Governance)',
      'Intervention Compliance & Progress Tracking (Active, Completed, Escalated)',
      'Post-Intervention Efficacy Measurement & Mastery Recalibration',
    ],
    inputs: [
      'Identified Topic Bottlenecks & Risk Factors from Modules 04 & 05',
      'Student Historical Mastery Profile & Pace Indicators',
      'Faculty Intervention Protocols & Departmental Resources',
    ],
    outputs: [
      'Structured Remedial Learning Action Itineraries',
      'Targeted Reading Materials & Practice Problem Sets',
      'Faculty Review Sign-Off & Verification Audit Records',
    ],
    evidenceGovernance:
      'All AI-recommended interventions require formal faculty sign-off. Changes in student mastery post-intervention are measured for efficacy auditing.',
    technicalArchitecture:
      'Curriculum-aware recommendation engine generating structured JSON intervention plans integrated with real-time notification dispatchers.',
    academicImpact:
      'Provides struggling students with clear, achievable remediation paths while preserving faculty mentorship authority and human oversight.',
  },
  {
    slug: 'career',
    code: 'M07',
    num: '07',
    title: 'Career Readiness & Industry Skill Gap Intelligence',
    tagline: 'Benchmarking verified academic competencies against live industry role taxonomies.',
    description:
      'Bridges the academic-industry gap by evaluating student verified mastery records against standardized industry competency frameworks (e.g. O*NET, ESCO). Produces explainable readiness scores and capstone project roadmaps.',
    problemSolved:
      'Graduates possess high GPAs but lack demonstrable, verified competencies required by industry roles, leading to poor placement outcomes.',
    icon: Compass,
    accent: 'bg-secondary/10 text-secondary border-secondary/20',
    badgeColor: 'secondary',
    appRoute: '/app/career',
    coreCapabilities: [
      'Standardized Industry Role Competency Modeling (Software Engineer, ML Engineer, Data Analyst, Cloud Architect, etc.)',
      'Verified Academic-to-Industry Competency Mapping',
      'Granular Skill Gap Diagnostics (Met, In Progress, Deficient)',
      'Explainable Career Readiness Index (0–100% match breakdown)',
      'Personalized Capstone Project & Portfolio Recommendation Roadmaps',
    ],
    inputs: [
      'Verified Topic Mastery & CLO Records from Module 04',
      'Student Practical / Lab Assessment Artifacts from Module 03',
      'Industry Role Competency Taxonomies & Market Skill Frameworks',
    ],
    outputs: [
      'Role-Specific Career Readiness Ratings & Spider Radar Profiles',
      'Itemized Skill Gap Analysis with Remedial Action Links',
      'Recommended Industry Bridge Projects & Portfolio Evidence Guides',
    ],
    evidenceGovernance:
      'Readiness is computed exclusively from verified academic mastery evidence and verified practical project artifacts—never self-reported claims.',
    technicalArchitecture:
      'Semantic competency embedding models computing cosine similarity between academic mastery vectors and verified industry role skill frameworks.',
    academicImpact:
      'Empowers placement cells with verified competency verification, helping students graduate with career-ready portfolios backed by empirical proof.',
  },
];
