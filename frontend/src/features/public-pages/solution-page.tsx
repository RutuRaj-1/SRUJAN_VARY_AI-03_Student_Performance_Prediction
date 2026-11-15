import { Link } from 'react-router-dom';
import {
  ArrowRight,
  Database,
  Brain,
  ShieldAlert,
  Compass,
  CheckCircle2,
  FileCheck2,
  Layers,
  LineChart,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';

const PIPELINE_STAGES = [
  {
    num: '01',
    title: 'Curriculum & Competency Parsing',
    module: 'Module 01: AI Syllabus & Competency Intelligence',
    modulePath: '/modules/syllabus',
    icon: Database,
    accent: 'bg-primary/10 text-primary border-primary/20',
    description:
      'Transforms unstructured university course syllabi, curriculum handbooks, and textbook tables of contents into canonical Directed Acyclic Graphs (DAGs) of topics, prerequisites, and Bloom’s Taxonomy-indexed Course Learning Outcomes (CLOs).',
    inputs: ['PDF / DOCX Syllabus files', 'Curriculum regulation handbooks', 'Subject prerequisites'],
    outputs: ['JSON-LD Canonical Topic Hierarchy', 'Prerequisite DAG graphs', 'CLO-to-Topic semantic mappings'],
    evidenceType: 'Deterministic structural validation & cryptographic SHA-256 ingestion hashes',
  },
  {
    num: '02',
    title: 'Academic Data Ingestion & Reconciliation',
    module: 'Module 02: Academic Data Intelligence Hub',
    modulePath: '/modules/academic-data',
    icon: Layers,
    accent: 'bg-secondary/10 text-secondary border-secondary/20',
    description:
      'Reconciles fragmented academic data across disparate ERPs, SIS databases, LMS systems, and paper evaluation records. Normalizes grade scales, computes attendance velocity, and logs immutable audit trails.',
    inputs: ['LMS logs (Moodle, Canvas)', 'ERP grade sheets (Marks, SGPA)', 'Biometric & RFID attendance logs'],
    outputs: ['Unified student academic timeline', 'Normalized GPA/mark indices', 'Time-series attendance trends'],
    evidenceType: 'Source ledger reconciliation & row-level audit verification stamps',
  },
  {
    num: '03',
    title: 'Evidence-Backed Assessment & Multimodal Evaluation',
    module: 'Module 03: Assessment & Attentiveness Engine',
    modulePath: '/modules/assessments',
    icon: FileCheck2,
    accent: 'bg-success/10 text-success border-success/20',
    description:
      'Evaluates student responses against syllabus-aligned rubrics. Synthesizes formative tests, subjective assignments, code submissions, and lab attentiveness into granular per-question evidence records.',
    inputs: ['Subjective & objective student submissions', 'Rubric criteria & sample keys', 'Classroom engagement markers'],
    outputs: ['Question-level score vectors', 'Detailed semantic feedback matrices', 'Attentiveness & participation scores'],
    evidenceType: 'Rubric criterion-level justification & timestamped submission telemetry',
  },
  {
    num: '04',
    title: 'Granular Topic Mastery & CLO Attainment',
    module: 'Module 04: Learning Mastery Analytics',
    modulePath: '/modules/mastery',
    icon: LineChart,
    accent: 'bg-accent/10 text-accent border-accent/20',
    description:
      'Aggregates multi-source evidence across time to compute fine-grained mastery scores (0–100%) for every topic and sub-topic. Measures Bloom’s taxonomy attainment without masking deficiencies behind cumulative averages.',
    inputs: ['Normalized assessment records', 'Topic semantic linkage weights', 'Historical evaluation trendlines'],
    outputs: ['Per-topic mastery percentages', 'Bloom’s taxonomy attainment vectors', 'Sub-competency bottleneck flags'],
    evidenceType: 'Confidence-weighted Bayesian evidence aggregation & historical decay curves',
  },
  {
    num: '05',
    title: 'Explainable Academic Risk Prediction',
    module: 'Module 05: Academic Risk Engine',
    modulePath: '/modules/risk',
    icon: ShieldAlert,
    accent: 'bg-warning/10 text-warning border-warning/20',
    description:
      'Identifies students at risk of academic failure, semester dropouts, or prerequisite stalls weeks before midterms. Delivers transparent SHAP/LIME-style factor attributions rather than opaque black-box risk scores.',
    inputs: ['Mastery score vectors', 'Attendance decline velocity', 'Prerequisite DAG deficiency status'],
    outputs: ['Calibrated risk tier (Low, Medium, High, Critical)', 'Top contributory risk factors with SHAP weights', 'Predicted failure probability'],
    evidenceType: 'Deterministic decision trees & feature-importance attribution vectors',
  },
  {
    num: '06',
    title: 'Prescriptive Academic Interventions',
    module: 'Module 06: Personalized Intervention',
    modulePath: '/modules/interventions',
    icon: Brain,
    accent: 'bg-primary/10 text-primary border-primary/20',
    description:
      'Synthesizes personalized, remedial learning itineraries addressing specific prerequisite weaknesses. Ensures Human-in-the-Loop governance by requiring faculty approval before intervention dispatch.',
    inputs: ['Identified topic bottlenecks', 'Student learning pace telemetry', 'Faculty intervention playbooks'],
    outputs: ['Remedial reading micro-plans', 'Targeted practice problem sets', 'Office hour & mentor assignment triggers'],
    evidenceType: 'Faculty approval cryptographic signature & post-intervention verification audits',
  },
  {
    num: '07',
    title: 'Industry Competency & Career Readiness Mapping',
    module: 'Module 07: Career Readiness Intelligence',
    modulePath: '/modules/career',
    icon: Compass,
    accent: 'bg-secondary/10 text-secondary border-secondary/20',
    description:
      'Bridges academia and industry by benchmarking student verified academic competencies against live industry role taxonomies (e.g., O*NET, ESCO, real-world job role profiles). Delivers explainable readiness ratings and project gap bridges.',
    inputs: ['Verified topic mastery profiles', 'Capstone project evaluation artifacts', 'Live job role competency matrices'],
    outputs: ['Role-specific readiness ratings (0-100%)', 'Targeted competency gap reports', 'Suggested industry bridge projects'],
    evidenceType: 'Competency-to-market cosine similarity indices & portfolio evidence verification',
  },
];

export function SolutionPage() {
  return (
    <div className="py-16">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="max-w-3xl">
          <Badge variant="outline" className="text-primary font-mono text-xs uppercase tracking-wider mb-4">
            The MASTERY Architecture & Pipeline
          </Badge>
          <h1 className="text-4xl md:text-5xl font-black text-slate-900 tracking-tight">
            Our Solution: The 7-Stage Interconnected Academic Intelligence Pipeline
          </h1>
          <p className="mt-5 text-lg text-slate-600 leading-relaxed">
            MASTERY replaces speculative grading and fragmented legacy systems with a closed-loop, evidence-backed
            pipeline. Each stage ingests verifiable academic artifacts, preserves complete provenance, and produces actionable
            intelligence for students, faculty, and institutions.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to="/app">
              <Button size="lg" className="font-semibold shadow-sm">
                Enter Academic Workspace
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link to="/modules">
              <Button variant="outline" size="lg" className="font-semibold">
                Explore All 7 Modules
              </Button>
            </Link>
          </div>
        </div>

        {/* Closed Loop Visual Indicator */}
        <div className="mt-16 bg-white border border-slate-200 p-8 shadow-sm">
          <div className="border-b border-slate-200 pb-5 mb-8">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-primary">System Integrity</span>
            <h2 className="text-2xl font-bold text-slate-900 mt-1">Closed-Loop Verification Architecture</h2>
            <p className="text-sm text-slate-600 mt-1">
              Data flows deterministically from curriculum parsing to industry readiness, feeding observed outcomes back into curriculum improvement.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
            {PIPELINE_STAGES.map((s, idx) => {
              const Icon = s.icon;
              return (
                <div key={s.num} className="bg-slate-50 border border-slate-200 p-3 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
                      <span>STEP {s.num}</span>
                      {idx < 6 && <ArrowRight className="h-3 w-3 text-slate-400 hidden lg:block" />}
                    </div>
                    <Icon className="h-5 w-5 text-primary mb-2" />
                    <div className="text-xs font-bold text-slate-900 line-clamp-2">{s.title}</div>
                  </div>
                  <div className="text-[10px] font-mono text-slate-500 mt-3 border-t border-slate-200 pt-1">
                    M0{idx + 1} Pipeline
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Detailed Pipeline Stages */}
        <div className="mt-16 space-y-12">
          <div className="border-b border-slate-200 pb-4">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500">Deep Pipeline Execution</span>
            <h2 className="text-2xl font-bold text-slate-900 mt-1">Stage-by-Stage Architecture Breakdown</h2>
          </div>

          <div className="space-y-8">
            {PIPELINE_STAGES.map((stage) => {
              const Icon = stage.icon;
              return (
                <Card key={stage.num} className="border-slate-200 bg-white overflow-hidden shadow-sm">
                  <div className="border-b border-slate-100 bg-slate-50/70 px-6 py-4 flex flex-wrap items-center justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded border ${stage.accent}`}>
                        <Icon className="h-5 w-5" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-mono font-bold text-primary">STAGE {stage.num}</span>
                          <span className="text-xs text-slate-400">•</span>
                          <span className="text-xs font-mono text-slate-500">{stage.module}</span>
                        </div>
                        <h3 className="text-xl font-bold text-slate-900">{stage.title}</h3>
                      </div>
                    </div>

                    <Link to={stage.modulePath}>
                      <Button variant="outline" size="sm" className="font-semibold text-xs">
                        View Module Specifications
                        <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
                      </Button>
                    </Link>
                  </div>

                  <CardContent className="p-6">
                    <p className="text-sm text-slate-700 leading-relaxed mb-6">
                      {stage.description}
                    </p>

                    <div className="grid md:grid-cols-3 gap-6 pt-4 border-t border-slate-100">
                      <div>
                        <div className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500 mb-2">
                          Inputs Ingested
                        </div>
                        <ul className="space-y-1.5">
                          {stage.inputs.map((inItem, i) => (
                            <li key={i} className="text-xs text-slate-700 flex items-start gap-1.5">
                              <span className="text-primary mt-0.5">•</span>
                              <span>{inItem}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div>
                        <div className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500 mb-2">
                          Verified Artifacts Generated
                        </div>
                        <ul className="space-y-1.5">
                          {stage.outputs.map((outItem, i) => (
                            <li key={i} className="text-xs text-slate-700 flex items-start gap-1.5">
                              <CheckCircle2 className="h-3.5 w-3.5 text-success shrink-0 mt-0.5" />
                              <span>{outItem}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div>
                        <div className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500 mb-2">
                          Evidence & Governance
                        </div>
                        <div className="bg-slate-50 border border-slate-200 p-3 rounded text-xs text-slate-600 font-mono">
                          {stage.evidenceType}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>

        {/* System Differentiation Summary */}
        <div className="mt-16 bg-slate-900 text-white p-8 md:p-12 border border-slate-800">
          <div className="max-w-3xl">
            <span className="text-xs font-mono font-bold uppercase tracking-widest text-primary-300">
              Deterministic Academic Rigor
            </span>
            <h2 className="text-3xl font-black mt-2 tracking-tight">
              Why an Interconnected Pipeline Outperforms Point Solutions
            </h2>
            <p className="mt-4 text-slate-300 text-sm leading-relaxed">
              Standalone AI tutors or generic risk dashboards fail because they operate on unverified, isolated data.
              MASTERY links curriculum semantics directly to assessment questions, aggregates granular topic mastery,
              predicts academic risk with transparent SHAP explanations, and guides faculty interventions that provably
              close verified knowledge gaps.
            </p>
            <div className="mt-6 flex flex-wrap gap-4">
              <Link to="/architecture">
                <Button variant="primary" className="bg-white text-slate-900 hover:bg-slate-100 font-semibold">
                  Review 6-Layer Architecture
                </Button>
              </Link>
              <Link to="/differentiators">
                <Button variant="outline" className="border-slate-700 text-white hover:bg-slate-800 font-semibold">
                  View Technical Differentiators
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
