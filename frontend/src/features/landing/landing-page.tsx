import React from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  Database,
  Layers,
  FileCheck2,
  LineChart,
  ShieldAlert,
  Brain,
  Compass,
  CheckCircle2,
  XCircle,
  ExternalLink,
  Lock,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { MODULES_DATA } from '@/features/public-pages/modules-data';

export const LandingPage: React.FC = () => {
  return (
    <div className="space-y-0">
      {/* 1. HERO SECTION */}
      <section className="relative overflow-hidden bg-white border-b border-slate-200 py-20 lg:py-28">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl">
            <div className="flex flex-wrap items-center gap-2 mb-6">
              <Badge variant="outline" className="border-primary/30 text-primary font-mono text-xs uppercase tracking-wider">
                Problem Statement AI-03
              </Badge>
              <Badge variant="brand" className="font-mono text-xs uppercase">
                Track: AI, CyberSecurity and Digital Trust
              </Badge>
              <span className="text-xs font-mono text-slate-400">Team VARY • SRUJAN 2026</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-slate-900 tracking-tight leading-[1.08]">
              Beyond Marks. <br />
              <span className="text-primary">Towards Mastery.</span>
            </h1>

            <p className="mt-6 text-lg sm:text-xl text-slate-600 leading-relaxed font-normal">
              An evidence-based academic intelligence platform that replaces blunt exam percentages
              with granular topic mastery, early explainable risk prediction, and faculty-supervised
              remedial interventions.
            </p>

            <div className="mt-8 flex flex-wrap items-center gap-3">
              <Link to="/app">
                <Button size="lg" className="font-semibold shadow-sm">
                  <span>Enter Academic Workspace</span>
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link to="/modules">
                <Button variant="outline" size="lg" className="font-semibold">
                  <span>Explore Seven Modules</span>
                </Button>
              </Link>
              <Link to="/problem">
                <Button variant="ghost" size="lg" className="text-slate-600 font-semibold">
                  <span>The Problem</span>
                </Button>
              </Link>
            </div>
          </div>

          {/* Quick Metrics Bar */}
          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 bg-slate-50 border border-slate-200 p-6 rounded">
            <div>
              <div className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500">Business Modules</div>
              <div className="text-3xl font-black text-slate-900 mt-1">7 Engines</div>
              <div className="text-xs text-slate-500 mt-0.5">Syllabus to Career Placement</div>
            </div>
            <div>
              <div className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500">Risk Explainability</div>
              <div className="text-3xl font-black text-primary mt-1">100% SHAP</div>
              <div className="text-xs text-slate-500 mt-0.5">Factor Attribution Vectors</div>
            </div>
            <div>
              <div className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500">Governance Gate</div>
              <div className="text-3xl font-black text-success mt-1">Human-in-Loop</div>
              <div className="text-xs text-slate-500 mt-0.5">Faculty Remedial Sign-Off</div>
            </div>
            <div>
              <div className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500">Student Privacy</div>
              <div className="text-3xl font-black text-warning mt-1">Role Firewall</div>
              <div className="text-xs text-slate-500 mt-0.5">Placement Risk Lockout</div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. THE FOUR STRUCTURAL FAILURES */}
      <section className="py-20 bg-slate-50 border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-wrap items-end justify-between gap-4 mb-12">
            <div className="max-w-2xl">
              <span className="text-xs font-mono font-bold text-primary uppercase tracking-wider">
                The Higher Education Crisis
              </span>
              <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-slate-900 mt-1">
                Four Structural Failures of Conventional Systems
              </h2>
              <p className="mt-3 text-sm sm:text-base text-slate-600">
                Traditional academic workflows rely on blunt aggregates and fragmented tools that fail students before educators even notice.
              </p>
            </div>
            <Link to="/problem">
              <Button variant="outline" size="sm" className="font-semibold text-xs">
                Full Problem Analysis
                <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
              </Button>
            </Link>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                title: 'Trapped & Fragmented Data',
                problem: 'Syllabus PDFs, LMS logs, and exam marks sit in disconnected silos without validation or provenance.',
                solution: 'Unified, validated academic timeline with cryptographic content verification.',
              },
              {
                title: 'Overall Marks Conceal Gaps',
                problem: 'A 72% composite mark hides 0% comprehension in foundational topics, causing downstream failure.',
                solution: 'Granular sub-topic mastery (0–100%) mapped to Bloom’s Taxonomy cognitive levels.',
              },
              {
                title: 'Post-Mortem Risk Detection',
                problem: 'Academic difficulty is discovered only after semester results, when remediation is impossible.',
                solution: 'Early risk detection in Weeks 3–6 with transparent SHAP factor explanations.',
              },
              {
                title: 'Academic-Industry Disconnect',
                problem: 'High GPAs frequently fail to translate into industry readiness because practical skills are unverified.',
                solution: 'Objective readiness benchmarking against live industry frameworks (O*NET & ESCO).',
              },
            ].map((item, idx) => (
              <Card key={idx} className="bg-white border-slate-200 shadow-sm flex flex-col justify-between">
                <CardContent className="p-6">
                  <div className="text-xs font-mono font-bold text-primary mb-2">0{idx + 1}</div>
                  <h3 className="font-bold text-base text-slate-900 mb-3">{item.title}</h3>
                  <div className="space-y-3 text-xs">
                    <div className="text-slate-600 bg-red-50/60 border border-red-100 p-2.5 rounded">
                      <div className="flex items-center gap-1 font-bold text-red-900 mb-1">
                        <XCircle className="h-3 w-3 text-red-600" />
                        <span>The Failure</span>
                      </div>
                      {item.problem}
                    </div>
                    <div className="text-slate-600 bg-emerald-50/60 border border-emerald-100 p-2.5 rounded">
                      <div className="flex items-center gap-1 font-bold text-emerald-900 mb-1">
                        <CheckCircle2 className="h-3 w-3 text-emerald-600" />
                        <span>The Fix</span>
                      </div>
                      {item.solution}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* 3. CLOSED-LOOP SOLUTION WORKFLOW */}
      <section className="py-20 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-wrap items-end justify-between gap-4 mb-12">
            <div className="max-w-2xl">
              <span className="text-xs font-mono font-bold text-primary uppercase tracking-wider">
                Systemic Solution
              </span>
              <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-slate-900 mt-1">
                The 7-Stage Interconnected Intelligence Pipeline
              </h2>
              <p className="mt-3 text-sm sm:text-base text-slate-600">
                Evidence flows deterministically across seven stages, from syllabus parsing to industry career readiness.
              </p>
            </div>
            <Link to="/solution">
              <Button variant="outline" size="sm" className="font-semibold text-xs">
                Inspect Complete Pipeline
                <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
              </Button>
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-7 gap-3">
            {[
              { num: '01', name: 'Curriculum Parsing', path: '/modules/syllabus', icon: Database },
              { num: '02', name: 'Data Hub Ingestion', path: '/modules/academic-data', icon: Layers },
              { num: '03', name: 'Assessment Engine', path: '/modules/assessments', icon: FileCheck2 },
              { num: '04', name: 'Mastery Analytics', path: '/modules/mastery', icon: LineChart },
              { num: '05', name: 'Academic Risk', path: '/modules/risk', icon: ShieldAlert },
              { num: '06', name: 'Interventions', path: '/modules/interventions', icon: Brain },
              { num: '07', name: 'Career Readiness', path: '/modules/career', icon: Compass },
            ].map((step, i) => {
              const StepIcon = step.icon;
              return (
                <Link
                  key={step.num}
                  to={step.path}
                  className="p-4 rounded bg-slate-50 border border-slate-200 hover:border-primary hover:bg-primary/5 transition-all group flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
                      <span>STEP {step.num}</span>
                      {i < 6 && <ArrowRight className="h-3 w-3 text-slate-300 hidden lg:block" />}
                    </div>
                    <StepIcon className="h-5 w-5 text-primary group-hover:scale-110 transition-transform mb-2" />
                    <div className="text-xs font-bold text-slate-900">{step.name}</div>
                  </div>
                  <div className="text-[10px] font-mono text-slate-500 mt-4 pt-2 border-t border-slate-200">
                    M0{i + 1} Module →
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* 4. SEVEN MODULES SUITE OVERVIEW */}
      <section className="py-20 bg-slate-50 border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-wrap items-end justify-between gap-4 mb-12">
            <div className="max-w-2xl">
              <span className="text-xs font-mono font-bold text-primary uppercase tracking-wider">
                Modular Monolith Architecture
              </span>
              <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-slate-900 mt-1">
                Seven Specialized Business Modules
              </h2>
              <p className="mt-3 text-sm sm:text-base text-slate-600">
                Explore each autonomous intelligence engine or launch directly into the live workspace.
              </p>
            </div>
            <Link to="/modules">
              <Button variant="outline" size="sm" className="font-semibold text-xs">
                View All Module Specifications
                <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
              </Button>
            </Link>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {MODULES_DATA.map((module) => {
              const Icon = module.icon;
              return (
                <Card key={module.code} className="bg-white border-slate-200 shadow-sm flex flex-col justify-between hover:border-slate-300 transition-colors">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono font-bold text-primary">MODULE {module.num}</span>
                        <span className="text-xs font-mono text-slate-400">• {module.code}</span>
                      </div>
                      <div className={`p-1.5 rounded ${module.accent}`}>
                        <Icon className="h-4 w-4" />
                      </div>
                    </div>

                    <h3 className="text-lg font-bold text-slate-900 mb-2">{module.title}</h3>
                    <p className="text-xs text-slate-600 leading-relaxed mb-4">{module.tagline}</p>

                    <div className="space-y-1 pt-3 border-t border-slate-100">
                      {module.coreCapabilities.slice(0, 2).map((cap, i) => (
                        <div key={i} className="flex items-start gap-1.5 text-xs text-slate-700">
                          <CheckCircle2 className="h-3.5 w-3.5 text-primary shrink-0 mt-0.5" />
                          <span className="line-clamp-1">{cap}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>

                  <div className="p-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-xs">
                    <Link to={`/modules/${module.slug}`} className="font-semibold text-primary hover:underline">
                      Specifications →
                    </Link>
                    <Link to={module.appRoute} className="font-mono text-slate-600 hover:text-slate-900 flex items-center gap-1">
                      <span>Launch</span>
                      <ExternalLink className="h-3 w-3" />
                    </Link>
                  </div>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* 5. ARCHITECTURE & SECURITY */}
      <section className="py-20 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <span className="text-xs font-mono font-bold text-primary uppercase tracking-wider">
                Under the Hood
              </span>
              <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-slate-900 mt-1">
                Six-Layer Decoupled System Architecture
              </h2>
              <p className="mt-4 text-slate-600 text-sm leading-relaxed">
                MASTERY is built as an enterprise-grade modular monolith. It couples a decoupled React 18 single-page
                application with an asynchronous FastAPI backend and PostgreSQL persistence engine.
              </p>

              <div className="mt-6 space-y-3">
                {[
                  { title: 'Presentation Layer', desc: 'Decoupled React 18, TypeScript, Tailwind CSS with five persona views.' },
                  { title: 'API Gateway & Firewall', desc: 'FastAPI gateway enforcing RBAC and Placement privacy firewalls.' },
                  { title: 'Core Intelligence Services', desc: 'Seven domain engines: DAG topological sorting, Bayesian mastery, SHAP risk.' },
                  { title: 'Explainability & Governance', desc: 'Transparent factor attribution and Human-in-the-Loop approval workflows.' },
                  { title: 'Persistence & Vector Store', desc: 'PostgreSQL relational schemas, pgvector competency embeddings, and audit trails.' },
                  { title: 'Data Ingress Adapters', desc: 'Multi-format PDF/DOCX OCR and batch CSV/JSON validation pipelines.' },
                ].map((l, i) => (
                  <div key={i} className="flex items-start gap-3 p-2.5 rounded bg-slate-50 border border-slate-100">
                    <span className="font-mono text-xs font-bold text-primary mt-0.5">L0{i + 1}</span>
                    <div>
                      <span className="text-xs font-bold text-slate-900 block">{l.title}</span>
                      <span className="text-xs text-slate-500">{l.desc}</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-8">
                <Link to="/architecture">
                  <Button variant="outline" size="sm" className="font-semibold text-xs">
                    View Complete Technical Architecture
                    <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
                  </Button>
                </Link>
              </div>
            </div>

            <div className="bg-slate-900 text-slate-100 p-8 rounded border border-slate-800 shadow-md">
              <div className="flex items-center gap-2 text-primary font-mono text-xs font-bold uppercase tracking-wider mb-4">
                <Lock className="h-4 w-4" />
                Ethical Security & Governance Invariants
              </div>
              <h3 className="text-xl font-bold text-white mb-4">
                Non-Negotiable Architectural Guarantees
              </h3>
              <div className="space-y-4 text-xs text-slate-300">
                <div className="p-3 rounded bg-slate-800/80 border border-slate-700">
                  <span className="font-bold text-white block mb-1">Placement Privacy Firewall</span>
                  Placement Officers are cryptographically locked out from viewing student academic risk scores,
                  mental health markers, or remedial intervention history.
                </div>
                <div className="p-3 rounded bg-slate-800/80 border border-slate-700">
                  <span className="font-bold text-white block mb-1">Temporal Leakage Elimination</span>
                  Risk models only evaluate features timestamped before the prediction cutoff date. Final exam grades
                  never leak into continuous predictors.
                </div>
                <div className="p-3 rounded bg-slate-800/80 border border-slate-700">
                  <span className="font-bold text-white block mb-1">Zero Synthetic Database Writes</span>
                  Live databases are never mutated by demo simulations. Read models are pure and auditable.
                </div>
                <div className="p-3 rounded bg-slate-800/80 border border-slate-700">
                  <span className="font-bold text-white block mb-1">Human-in-the-Loop Faculty Approval</span>
                  No AI-generated intervention is sent to students without formal faculty advisor review and sign-off.
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-800 flex justify-between items-center text-xs">
                <span className="font-mono text-slate-400">Digital Trust Verified</span>
                <Link to="/differentiators" className="text-primary hover:underline font-semibold">
                  Read Differentiators →
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 6. FIVE STAKEHOLDER PERSONAS */}
      <section className="py-20 bg-slate-50 border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-wrap items-end justify-between gap-4 mb-12">
            <div className="max-w-2xl">
              <span className="text-xs font-mono font-bold text-primary uppercase tracking-wider">
                Tailored Stakeholder Workspaces
              </span>
              <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-slate-900 mt-1">
                Five Specialized Institutional Personas
              </h2>
              <p className="mt-3 text-sm sm:text-base text-slate-600">
                Experience the platform through role-aware workspaces tailored to each stakeholder’s core objective.
              </p>
            </div>
            <Link to="/roles">
              <Button variant="outline" size="sm" className="font-semibold text-xs">
                View Role Specifications
                <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
              </Button>
            </Link>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-4">
            {[
              { role: 'Student', focus: 'Topic Mastery & Remediation', desc: 'Inspect topic mastery, review faculty-approved learning plans, explore career roadmaps.' },
              { role: 'Faculty', focus: 'Evaluation & Human Sign-Off', desc: 'Rubric-assisted grading, diagnostic heatmaps, review and approve student interventions.' },
              { role: 'Admin / HoD', focus: 'Accreditation & Risk Radar', desc: 'Monitor cohort health, CLO/PO attainment audit reports, curriculum prerequisite bottleneck audits.' },
              { role: 'Placement', focus: 'Verified Competency Matching', desc: 'Inspect verified skill matrices and role readiness under strict privacy isolation from risk flags.' },
              { role: 'Platform Admin', focus: 'Pipelines & Infrastructure', desc: 'Manage institutional tenants, data ingestion pipelines, cryptographic audit logs.' },
            ].map((p, idx) => (
              <div key={idx} className="bg-white border border-slate-200 p-4 rounded shadow-sm flex flex-col justify-between">
                <div>
                  <span className="text-xs font-mono font-bold text-primary uppercase">0{idx + 1} • {p.role}</span>
                  <div className="font-bold text-sm text-slate-900 mt-1">{p.focus}</div>
                  <p className="text-xs text-slate-600 mt-2 leading-relaxed">{p.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 7. FINAL CALL TO ACTION */}
      <section className="py-20 bg-slate-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <Badge variant="outline" className="text-primary-300 border-primary-500/40 font-mono text-xs uppercase mb-4">
            Ready for Evaluation
          </Badge>
          <h2 className="text-3xl sm:text-5xl font-black tracking-tight max-w-3xl mx-auto">
            Make academic progress visible. <br />
            Make support actionable.
          </h2>
          <p className="mt-4 text-sm sm:text-base text-slate-300 max-w-xl mx-auto">
            Access the complete MASTERY academic workspace across all seven modules with real-time analytics and role-aware navigation.
          </p>

          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <Link to="/app">
              <Button size="lg" className="bg-white text-slate-900 hover:bg-slate-100 font-semibold gap-2">
                <span>Enter Academic Workspace</span>
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link to="/modules">
              <Button variant="outline" size="lg" className="border-slate-700 text-white hover:bg-slate-800 font-semibold">
                <span>Explore Modules Suite</span>
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};
