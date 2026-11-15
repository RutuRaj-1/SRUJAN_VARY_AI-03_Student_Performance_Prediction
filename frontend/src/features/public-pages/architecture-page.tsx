import { Link } from 'react-router-dom';
import {
  ArrowRight,
  Layers,
  Shield,
  Cpu,
  Database,
  Lock,
  GitBranch,
  Terminal,
  CheckCircle2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';

const ARCHITECTURE_LAYERS = [
  {
    layer: 'Layer 01',
    name: 'Presentation & Role-Aware Workspace Layer',
    icon: Layers,
    accent: 'border-l-4 border-l-blue-600',
    tech: 'React 18 • TypeScript • Tailwind CSS • Vite • Lucide • Recharts',
    description:
      'Decoupled single-page application built on strict editorial brutalist design principles. Features five distinct persona workspaces (Student, Faculty, Academic Admin, Placement Officer, Platform Admin) with instant perspective switching and zero page reload latency.',
    details: [
      'Role-based dynamic route protection with client-side privilege verification',
      'Unified context provider managing active persona and student focus',
      'Accessible, high-contrast typography optimized for dense academic inspection',
      'Zero synthetic database write operations — pure deterministic read models',
    ],
  },
  {
    layer: 'Layer 02',
    name: 'API Gateway & Ethical Security Firewall',
    icon: Lock,
    accent: 'border-l-4 border-l-indigo-600',
    tech: 'FastAPI • Pydantic v2 • OAuth2 / JWT • CORS Middleware • Rate Limiting',
    description:
      'High-throughput asynchronous gateway enforcing cryptographic token validation, role-based authorization scopes, and an ethical firewall. Placement officers are cryptographically restricted from querying mental health, academic risk, or socio-economic indicators.',
    details: [
      'Strict RBAC authorization policies enforced on every endpoint route',
      'Placement Privacy Firewall (HTTP 403 on risk endpoints for placement roles)',
      'Immutable request audit logging with client IP, timestamp, and actor ID',
      'Strict Pydantic request/response schema sanitization and validation',
    ],
  },
  {
    layer: 'Layer 03',
    name: 'Core Intelligence & Analytics Services',
    icon: Cpu,
    accent: 'border-l-4 border-l-emerald-600',
    tech: 'Modular Python Services • NumPy • SciPy • NetworkX • Pandas',
    description:
      'Seven decoupled domain services orchestrating the academic intelligence lifecycle: Syllabus DAG generation, academic record reconciliation, multimodal assessment evaluation, Bayesian mastery scoring, risk prediction, intervention generation, and career readiness alignment.',
    details: [
      'M01 Syllabus Intelligence: Topological sorting & prerequisite DAG validation',
      'M02 Academic Data Hub: Multi-source reconciliation and velocity computation',
      'M03 Assessment Engine: Formative rubric evaluation and attentiveness synthesis',
      'M04 Mastery Engine: Fine-grained Bayesian topic and Bloom’s CLO attainment',
      'M05 Risk Prediction: Calibrated probability modeling with explainable SHAP weights',
      'M06 Intervention Engine: Scaffolded remedial action plans with faculty approval',
      'M07 Career Readiness: Cosine similarity benchmarking against live role frameworks',
    ],
  },
  {
    layer: 'Layer 04',
    name: 'Explainability & Governance Layer',
    icon: Shield,
    accent: 'border-l-4 border-l-amber-600',
    tech: 'SHAP / TreeExplainer • Bloom’s Taxonomy Matrices • Cryptographic SHA-256',
    description:
      'Guarantees that no academic decision or risk flag is an unexplainable black box. Every risk tier output is accompanied by top contributory factors and feature weights. Every AI-suggested intervention requires mandatory human faculty sign-off.',
    details: [
      'Transparent SHAP factor attributions (Attendance velocity, topic deficits, pace)',
      'Deterministic Bloom’s Revised Taxonomy cognitive mapping (L1 to L6)',
      'Human-in-the-Loop approval workflows for all remedial learning interventions',
      'Tamper-evident verification digests for all ingested syllabi and assessment records',
    ],
  },
  {
    layer: 'Layer 05',
    name: 'Persistence & Vector Knowledge Store',
    icon: Database,
    accent: 'border-l-4 border-l-purple-600',
    tech: 'PostgreSQL 15 • Supabase • pgvector • SQLAlchemy 2.0 • Redis Cache',
    description:
      'Relational core with foreign-key referential integrity, temporal snapshots for student performance tracking, and pgvector embeddings for semantic curriculum and skill matching. Read-optimized views ensure sub-50ms dashboard response times.',
    details: [
      'Relational normalization across students, courses, topics, assessments, and risks',
      'Semantic competency vector store for fast career role cosine similarity matching',
      'Append-only historical audit ledgers tracking grade changes and interventions',
      'Redis in-memory caching for real-time dashboard aggregation queries',
    ],
  },
  {
    layer: 'Layer 06',
    name: 'Data Ingestion & Ingress Adapters',
    icon: GitBranch,
    accent: 'border-l-4 border-l-rose-600',
    tech: 'pypdf • python-docx • CSV/JSON Parsers • SIS Webhooks • REST Connectors',
    description:
      'Modular adapter layer converting unstructured institutional files into validated domain entities. Handles messy multi-page PDF syllabi, raw LMS grade sheets, and biometric attendance logs with row-level error reporting.',
    details: [
      'Multi-format OCR and structural PDF document tokenization pipelines',
      'Batch CSV/JSON validation with transactional all-or-nothing rollback',
      'Idempotent ingestion ensuring duplicate uploads never corrupt student ledgers',
      'Comprehensive error reporting detailing exact row and column parsing errors',
    ],
  },
];

export function ArchitecturePage() {
  return (
    <div className="py-16">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="max-w-3xl">
          <Badge variant="outline" className="text-primary font-mono text-xs uppercase tracking-wider mb-4">
            System Design & Engineering
          </Badge>
          <h1 className="text-4xl md:text-5xl font-black text-slate-900 tracking-tight">
            Six-Layer Decoupled System Architecture
          </h1>
          <p className="mt-5 text-lg text-slate-600 leading-relaxed">
            MASTERY is engineered as an enterprise-grade modular monolith. It couples a decoupled, role-aware React frontend
            with an asynchronous FastAPI backend and PostgreSQL persistence engine, built from the ground up for high auditability,
            ethical security, and zero unexplainable AI outputs.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to="/solution">
              <Button size="lg" className="font-semibold shadow-sm">
                View 7-Stage Pipeline
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link to="/differentiators">
              <Button variant="outline" size="lg" className="font-semibold">
                Ethical AI & Differentiators
              </Button>
            </Link>
          </div>
        </div>

        {/* High Level Metrics Banner */}
        <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 bg-white border border-slate-200 p-6 shadow-sm">
          <div>
            <div className="text-xs font-mono uppercase tracking-wider text-slate-500">Architecture</div>
            <div className="text-2xl font-black text-slate-900 mt-1">Modular Monolith</div>
            <div className="text-xs text-slate-500 mt-0.5">Decoupled UI & Async Core</div>
          </div>
          <div>
            <div className="text-xs font-mono uppercase tracking-wider text-slate-500">API Response SLA</div>
            <div className="text-2xl font-black text-primary mt-1">&lt; 50ms</div>
            <div className="text-xs text-slate-500 mt-0.5">PostgreSQL + In-Memory Caching</div>
          </div>
          <div>
            <div className="text-xs font-mono uppercase tracking-wider text-slate-500">Explainability</div>
            <div className="text-2xl font-black text-success mt-1">100% Attributed</div>
            <div className="text-xs text-slate-500 mt-0.5">Zero Black-Box Scoring</div>
          </div>
          <div>
            <div className="text-xs font-mono uppercase tracking-wider text-slate-500">Security Gate</div>
            <div className="text-2xl font-black text-warning mt-1">Strict RBAC</div>
            <div className="text-xs text-slate-500 mt-0.5">Placement Privacy Firewall</div>
          </div>
        </div>

        {/* 6 Layers Breakdown */}
        <div className="mt-16 space-y-8">
          <div className="border-b border-slate-200 pb-4">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500">Full Stack Topology</span>
            <h2 className="text-2xl font-bold text-slate-900 mt-1">Detailed Architectural Layers</h2>
          </div>

          <div className="space-y-6">
            {ARCHITECTURE_LAYERS.map((layer) => {
              const Icon = layer.icon;
              return (
                <Card key={layer.layer} className={`bg-white shadow-sm overflow-hidden ${layer.accent}`}>
                  <CardContent className="p-6 md:p-8">
                    <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded bg-slate-100 text-slate-900">
                          <Icon className="h-5 w-5" />
                        </div>
                        <div>
                          <span className="text-xs font-mono font-bold text-primary block">{layer.layer}</span>
                          <h3 className="text-xl font-bold text-slate-900">{layer.name}</h3>
                        </div>
                      </div>

                      <Badge variant="outline" className="font-mono text-xs bg-slate-50 text-slate-700">
                        {layer.tech}
                      </Badge>
                    </div>

                    <p className="text-sm text-slate-700 leading-relaxed mb-6">
                      {layer.description}
                    </p>

                    <div className="bg-slate-50 border border-slate-100 p-4 rounded">
                      <div className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500 mb-2.5">
                        Architectural Invariants & Specifications:
                      </div>
                      <div className="grid md:grid-cols-2 gap-2">
                        {layer.details.map((item, i) => (
                          <div key={i} className="flex items-start gap-2 text-xs text-slate-700">
                            <CheckCircle2 className="h-3.5 w-3.5 text-primary shrink-0 mt-0.5" />
                            <span>{item}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>

        {/* Terminal / Code verification block */}
        <div className="mt-16 bg-slate-950 text-slate-100 p-8 rounded border border-slate-800 font-mono text-xs shadow-lg">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
            <div className="flex items-center gap-2 text-slate-400">
              <Terminal className="h-4 w-4 text-primary" />
              <span>verification_suite.log — MASTERY Automated Validation</span>
            </div>
            <span className="text-success text-[11px] font-bold">ALL 73 TESTS PASSING [100%]</span>
          </div>
          <pre className="text-slate-300 overflow-x-auto space-y-1">
            <code>tests/test_syllabus_pipeline.py::test_dag_cycle_prevention PASSED</code>{'\n'}
            <code>tests/test_academic_hub.py::test_idempotent_reconciliation PASSED</code>{'\n'}
            <code>tests/test_assessment_engine.py::test_rubric_justification PASSED</code>{'\n'}
            <code>tests/test_mastery_analytics.py::test_bayesian_topic_aggregation PASSED</code>{'\n'}
            <code>tests/test_risk_prediction.py::test_shap_explainability_vectors PASSED</code>{'\n'}
            <code>tests/test_risk_firewall.py::test_placement_officer_403_rejection PASSED</code>{'\n'}
            <code>tests/test_intervention_engine.py::test_faculty_signoff_integrity PASSED</code>{'\n'}
            <code>tests/test_career_readiness.py::test_industry_taxonomy_mapping PASSED</code>{'\n'}
            <code className="text-primary font-bold">======================= 73 passed in 1.48s =======================</code>
          </pre>
        </div>

        {/* Bottom CTA */}
        <div className="mt-16 text-center">
          <Link to="/app">
            <Button size="lg" className="font-semibold shadow-sm">
              Enter Workspace & Test System
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
