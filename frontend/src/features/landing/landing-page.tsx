import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Compass,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Play,
  Database,
  FileText,
  Award,
  BookOpen,
  Briefcase,
  Menu,
  X,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export const LandingPage: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const modules = [
    {
      num: '01',
      title: 'Academic Data Intelligence Hub',
      route: '/app/academic-data',
      icon: Database,
      tagline: 'Reliable academic intelligence begins with reliable academic evidence.',
      problem: 'Student attendance, exam scores, and internal marks are trapped in disconnected files without tamper-evident validation.',
      capabilities: [
        'Automated CSV/XLSX two-phase ingestion & validation',
        'Data-quality scanner detecting grade anomalies & missing marks',
        'Separation of verified, unverified, excused, and absent records',
        'Cryptographic audit ledger tracking faculty edits',
      ],
      inputs: 'Raw mark sheets, attendance registries, institutional ERP CSVs',
      outputs: 'Verified student academic profiles and canonical ledger',
      next: 'Feeds clean performance records into Assessment & Mastery engines',
    },
    {
      num: '02',
      title: 'AI Syllabus & Competency Intelligence',
      route: '/app/syllabus',
      icon: FileText,
      tagline: 'Understand what is taught before evaluating what is learned.',
      problem: 'Course curriculum PDFs sit dormant in archives without machine-readable linkages to examination questions.',
      capabilities: [
        'Automated PDF syllabus extraction into Course Learning Outcomes (CLOs)',
        'Hierarchical unit, topic, and subtopic structural parsing',
        'Bloom\'s Taxonomy depth classification (L1–L6)',
        'Industry competency crosswalk & curriculum gap discovery',
      ],
      inputs: 'Institutional PDF syllabi and course curriculum documents',
      outputs: 'Structured competency graph and mapped Course Learning Outcomes',
      next: 'Supplies topic blueprints to the Intelligent Assessment Engine',
    },
    {
      num: '03',
      title: 'Intelligent Assessment & Attentiveness Engine',
      route: '/app/assessments',
      icon: CheckCircle2,
      tagline: 'Move from raw marks to structured assessment evidence.',
      problem: 'Assessments evaluate total scores rather than topic-level mastery, and lack observable learning engagement feedback.',
      capabilities: [
        'Question bank tagged with Bloom\'s cognitive levels and topic codes',
        'Multi-type assessment authoring (Objective, Subjective, Coding)',
        'Student attempt environment with granular feedback',
        'Ethical, observable interaction telemetry (Zero webcam/facial surveillance)',
      ],
      inputs: 'Question blueprints, student responses, interaction events',
      outputs: 'Itemized, topic-attributed evidence items with cognitive levels',
      next: 'Supplies granular assessment evidence to Mastery Analytics',
    },
    {
      num: '04',
      title: 'Learning Mastery & Performance Analytics',
      route: '/app/mastery',
      icon: Award,
      tagline: 'Understand where learning progresses and where more evidence is needed.',
      problem: 'A composite grade of 65% conceals whether a student mastered core recursion or failed concurrency.',
      capabilities: [
        'Evidence-backed topic mastery: MASTERED, PROGRESSING, NEEDS_ATTENTION',
        'Course Learning Outcome attainment percentage gauges',
        'Evidence sufficiency checks: Excused absences are NEVER scored as zero',
        'Cognitive Bloom level distribution and learning gap discovery',
      ],
      inputs: 'Verified assessment items and topic-mapped response evidence',
      outputs: 'Explainable mastery profiles, CLO attainments, and identified gaps',
      next: 'Provides time-bounded features for Academic Risk Prediction',
    },
    {
      num: '05',
      title: 'Academic Risk Prediction Engine',
      route: '/app/risk',
      icon: AlertTriangle,
      tagline: 'Identify academic difficulty early enough to respond responsibly.',
      problem: 'Academic difficulty is discovered only after semester results, when remediation is impossible.',
      capabilities: [
        'Time-bounded feature engineering preventing temporal data leakage',
        'Dataset readiness gating preventing premature machine learning inference',
        'Deterministic expert-rule baseline + Logistic Regression fallback',
        'Explainable adverse vs protective factor impact breakdowns',
      ],
      inputs: 'Historical trajectory, attendance consistency, topic mastery trends',
      outputs: 'Early risk probabilities, risk classifications, and factor explanations',
      next: 'Triggers personalized intervention recommendations for at-risk students',
    },
    {
      num: '06',
      title: 'Personalized Academic Intervention',
      route: '/app/interventions',
      icon: BookOpen,
      tagline: 'Turn academic insights into structured, human-supervised support.',
      problem: 'Remediation is informal, undocumented, and rarely monitored for actual learning recovery.',
      capabilities: [
        'Automated intervention recommendations based on verified mastery deficits',
        'Faculty review & approval lifecycle (DRAFT → APPROVED → ACTIVE → COMPLETED)',
        'Student action items with verifiable evidence submissions',
        'Observational progress tracking without unsubstantiated causal claims',
      ],
      inputs: 'Identified learning gaps, risk factors, and faculty advising directives',
      outputs: 'Supervised student academic support plans and progress audit trail',
      next: 'Validates competency recovery for Career Readiness',
    },
    {
      num: '07',
      title: 'Career Readiness & Industry Skill Gap',
      route: '/app/career-readiness',
      icon: Briefcase,
      tagline: 'Connect what students learn with what professional roles require.',
      problem: 'High academic GPA does not guarantee alignment with modern technical industry roles.',
      capabilities: [
        'Industry role profiles (Full-Stack, AI/ML, Data Systems, Cloud/DevOps)',
        'Separation of Core Academic Coverage vs Practical Project Evidence',
        'Faculty verification of external GitHub & laboratory capstones',
        '5-Tier Skill Gap discovery and targeted career roadmap recommendations',
      ],
      inputs: 'Mastered syllabus competencies and verified practical project ledgers',
      outputs: 'Role alignment status, core coverage %, and targeted skill roadmaps',
      next: 'Empowers graduating students with verified career competency portfolios',
    },
  ];

  return (
    <div className="min-h-screen bg-[#F7FAF9] text-[#172825] font-sans">
      {/* 1. TOP NAVIGATION */}
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-sm border-b border-[#DCE6E2]">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-[4px] bg-[#123E40] text-white flex items-center justify-center font-bold text-lg tracking-wider shadow-sm">
              M
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg text-[#172825] tracking-tight">MASTERY</span>
                <span className="text-[10px] font-mono bg-[#EEF8F7] text-[#123E40] px-1.5 py-0.5 rounded border border-[#BDCEC8]">
                  SRUJAN 2026
                </span>
              </div>
              <p className="text-[11px] text-[#687A75] font-medium leading-none hidden sm:block">
                Beyond Marks. Towards Mastery.
              </p>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden lg:flex items-center gap-6 text-xs font-semibold text-[#40524E]">
            <a href="#problem" className="hover:text-[#237277] transition-colors">The Problem</a>
            <a href="#solution" className="hover:text-[#237277] transition-colors">Solution Workflow</a>
            <a href="#modules" className="hover:text-[#237277] transition-colors">Seven Modules</a>
            <a href="#architecture" className="hover:text-[#237277] transition-colors">Architecture</a>
            <a href="#differentiators" className="hover:text-[#237277] transition-colors">Differentiators</a>
            <a href="#ecosystem" className="hover:text-[#237277] transition-colors">Role Ecosystem</a>
            <Link to="/demo-guide" className="text-[#237277] hover:text-[#123E40] flex items-center gap-1 font-bold">
              <Compass className="h-3.5 w-3.5" />
              <span>Demo Walkthrough</span>
            </Link>
          </nav>

          {/* Top Actions */}
          <div className="flex items-center gap-3">
            <Link to="/demo-guide" className="hidden sm:inline-block">
              <Button variant="outline" size="sm" className="text-xs border-[#BDCEC8]">
                Walkthrough Guide
              </Button>
            </Link>
            <Link to="/app/dashboard">
              <Button variant="primary" size="sm" className="gap-1.5 text-xs">
                <span>Explore Platform</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </Button>
            </Link>

            {/* Mobile Hamburger */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 text-[#40524E] hover:text-[#172825]"
            >
              {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu Dropdown */}
        {mobileMenuOpen && (
          <div className="lg:hidden border-t border-[#DCE6E2] bg-white px-6 py-4 space-y-3 text-sm">
            <a href="#problem" onClick={() => setMobileMenuOpen(false)} className="block py-1 text-[#40524E]">The Problem</a>
            <a href="#solution" onClick={() => setMobileMenuOpen(false)} className="block py-1 text-[#40524E]">Solution Workflow</a>
            <a href="#modules" onClick={() => setMobileMenuOpen(false)} className="block py-1 text-[#40524E]">Seven Modules</a>
            <a href="#architecture" onClick={() => setMobileMenuOpen(false)} className="block py-1 text-[#40524E]">System Architecture</a>
            <a href="#differentiators" onClick={() => setMobileMenuOpen(false)} className="block py-1 text-[#40524E]">Core Differentiators</a>
            <Link to="/demo-guide" onClick={() => setMobileMenuOpen(false)} className="block py-1 font-bold text-[#237277]">
              Demo Walkthrough Guide
            </Link>
            <Link to="/app/dashboard" onClick={() => setMobileMenuOpen(false)} className="block pt-2">
              <Button variant="primary" size="sm" className="w-full">
                Enter Platform Workspace
              </Button>
            </Link>
          </div>
        )}
      </header>

      {/* 2. HERO SECTION */}
      <section className="relative overflow-hidden pt-16 pb-20 md:pt-24 md:pb-28 border-b border-[#DCE6E2] bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-[4px] bg-[#EEF8F7] border border-[#BDCEC8] text-[#123E40] text-xs font-semibold mb-6">
              <ShieldCheck className="h-4 w-4 text-[#237277]" />
              <span>SRUJAN 2026 · Problem Statement AI-03 · Student Performance Prediction</span>
            </div>

            <h1 className="text-4xl md:text-6xl font-bold tracking-tight text-[#172825] leading-tight font-sans">
              Beyond Marks. <br />
              <span className="text-[#237277]">Towards Mastery.</span>
            </h1>

            <p className="mt-6 text-lg md:text-xl text-[#40524E] leading-relaxed">
              An evidence-driven academic intelligence platform that connects curriculum understanding, assessment performance, learning mastery, early risk prediction, personalized academic support, and career readiness — all within one unified ecosystem.
            </p>

            <div className="mt-8 flex flex-wrap items-center gap-4">
              <Link to="/app/dashboard">
                <Button variant="primary" size="lg" className="gap-2 text-sm font-semibold">
                  <Play className="h-4 w-4" />
                  <span>Explore the Platform</span>
                </Button>
              </Link>
              <a href="#architecture">
                <Button variant="outline" size="lg" className="text-sm border-[#BDCEC8]">
                  <span>View System Architecture</span>
                </Button>
              </a>
              <Link to="/demo-guide">
                <Button variant="secondary" size="lg" className="gap-1.5 text-sm">
                  <Compass className="h-4 w-4 text-[#237277]" />
                  <span>Interactive Walkthrough</span>
                </Button>
              </Link>
            </div>
          </div>

          {/* Connected Intelligence Pipeline Illustration */}
          <div className="mt-16 p-6 md:p-8 rounded-[6px] bg-[#EEF8F7] border border-[#BDCEC8] shadow-subtle">
            <div className="text-xs font-mono font-bold text-[#123E40] uppercase tracking-wider mb-4 flex items-center justify-between">
              <span>The MASTERY Evidence Pipeline</span>
              <span className="hidden md:inline text-[#687A75]">Continuous Closed-Loop Learning Recovery</span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 text-center">
              {[
                { step: '1', title: 'Curriculum', desc: 'AI Syllabus Parsing', color: 'bg-white border-[#DCE6E2]' },
                { step: '2', title: 'Academic Data', desc: 'Verified Evidence Ledger', color: 'bg-white border-[#DCE6E2]' },
                { step: '3', title: 'Assessments', desc: 'Bloom Taxonomy Items', color: 'bg-white border-[#DCE6E2]' },
                { step: '4', title: 'Mastery', desc: 'Topic-Level Analytics', color: 'bg-[#D9F0EE] border-[#2D8E92]' },
                { step: '5', title: 'Risk Engine', desc: 'Early Time-Bounded AI', color: 'bg-white border-[#DCE6E2]' },
                { step: '6', title: 'Interventions', desc: 'Faculty-Supervised Plan', color: 'bg-white border-[#DCE6E2]' },
                { step: '7', title: 'Career Alignment', desc: 'Industry Skill Gap', color: 'bg-white border-[#DCE6E2]' },
              ].map((p) => (
                <div key={p.step} className={`p-3.5 rounded-[4px] border ${p.color} flex flex-col justify-between text-left`}>
                  <div className="font-mono text-[10px] text-[#687A75] font-bold">STAGE {p.step}</div>
                  <div className="font-bold text-xs text-[#172825] mt-1">{p.title}</div>
                  <div className="text-[11px] text-[#40524E] mt-0.5">{p.desc}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* 3. PROBLEM SECTION */}
      <section id="problem" className="py-20 border-b border-[#DCE6E2] bg-[#F7FAF9]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="max-w-3xl mb-12">
            <div className="inline-flex items-center gap-1.5 text-xs font-mono font-bold text-[#237277] uppercase tracking-wider">
              <span>Current Educational Bottleneck</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-[#172825] mt-2 font-sans">
              Traditional academic metrics tell only part of the story.
            </h2>
            <p className="mt-3 text-sm md:text-base text-[#40524E] leading-relaxed">
              Modern academic reporting relies heavily on isolated percentages, attendance registries, and end-semester examinations. These signals are useful historical records, but they fail to support early student learning intervention.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                num: '01',
                title: 'Academic Data is Fragmented',
                desc: 'Attendance registries, internal test sheets, and laboratory marks reside in disparate spreadsheets, making longitudinal evidence tracking impossible.',
              },
              {
                num: '02',
                title: 'Curriculum is Disconnected from Evidence',
                desc: 'Institutional syllabi outline Course Learning Outcomes, but semester exams generate only total numerical marks without topic attribution.',
              },
              {
                num: '03',
                title: 'Marks Conceal Topic-Level Deficits',
                desc: 'A passing score of 65% conceals whether a student mastered core algorithms or failed critical database concurrency transactions.',
              },
              {
                num: '04',
                title: 'Academic Risk is Identified Too Late',
                desc: 'Traditional alert systems trigger only after a student has already failed an end-semester exam, when proactive remediation is no longer viable.',
              },
              {
                num: '05',
                title: 'Student Support is Not Tracked',
                desc: 'Remediation is informal and verbal. Institutions lack auditable evidence proving whether faculty advising led to learning recovery.',
              },
              {
                num: '06',
                title: 'Academic Scores Disconnect from Industry',
                desc: 'Graduating GPAs do not reflect whether students hold the verifiable practical competencies demanded by modern technical roles.',
              },
            ].map((prob) => (
              <div key={prob.num} className="p-6 rounded-[6px] bg-white border border-[#DCE6E2] shadow-subtle hover:border-[#BDCEC8] transition-colors">
                <span className="font-mono text-xs font-bold text-[#237277]">{prob.num}</span>
                <h3 className="text-base font-bold text-[#172825] mt-2">{prob.title}</h3>
                <p className="text-xs text-[#40524E] mt-2 leading-relaxed">{prob.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 4. SOLUTION WORKFLOW SECTION */}
      <section id="solution" className="py-20 border-b border-[#DCE6E2] bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="max-w-3xl mb-12">
            <div className="inline-flex items-center gap-1.5 text-xs font-mono font-bold text-[#237277] uppercase tracking-wider">
              <span>The MASTERY Paradigm</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-[#172825] mt-2 font-sans">
              From Raw Marks to Actionable Academic Intelligence
            </h2>
            <p className="mt-3 text-sm md:text-base text-[#40524E] leading-relaxed">
              MASTERY creates a traceable intelligence ecosystem connecting curriculum design, student evaluation, early warning, and career readiness without arbitrary composite scores.
            </p>
          </div>

          <div className="p-8 rounded-[6px] bg-[#F7FAF9] border border-[#DCE6E2] font-mono text-xs text-[#172825] space-y-4 overflow-x-auto">
            <div className="text-[#237277] font-bold">/* End-to-End Evidence Attribution Architecture */</div>
            <div className="space-y-1.5 text-[#40524E]">
              <div>Institutional Curriculum (Syllabi PDFs)</div>
              <div className="text-[#237277]">└── [Module 02] Extract Units, Topics, CLOs, and Bloom Taxonomy Depths</div>
              <div className="pl-4">├── [Module 01] Ingest Verified Academic Records & Attendance</div>
              <div className="pl-8">├── [Module 03] Deliver Assessments Mapped to Specific Topics</div>
              <div className="pl-12">├── [Module 04] Calculate Evidence-Backed Topic Mastery & CLO Attainment</div>
              <div className="pl-16">├── [Module 05] Predict Time-Bounded Risk Before Midterm Cutoffs</div>
              <div className="pl-20">├── [Module 06] Prescribe Faculty-Supervised Academic Intervention</div>
              <div className="pl-24">└── [Module 07] Map Demonstrated Competencies to Industry Role Profiles</div>
            </div>
          </div>
        </div>
      </section>

      {/* 5. SEVEN MODULES SHOWCASE */}
      <section id="modules" className="py-20 border-b border-[#DCE6E2] bg-[#F7FAF9]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="max-w-3xl mb-12">
            <div className="inline-flex items-center gap-1.5 text-xs font-mono font-bold text-[#237277] uppercase tracking-wider">
              <span>Complete Functional Suite</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-[#172825] mt-2 font-sans">
              The Seven Integrated Business Modules
            </h2>
            <p className="mt-3 text-sm md:text-base text-[#40524E] leading-relaxed">
              Each module addresses a dedicated academic domain while operating as part of a continuous intelligence pipeline.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {modules.map((m) => {
              const Icon = m.icon;
              return (
                <div
                  key={m.num}
                  className="p-6 rounded-[6px] bg-white border border-[#DCE6E2] shadow-subtle flex flex-col justify-between hover:border-[#2D8E92] transition-all"
                >
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <span className="font-mono text-xs font-bold px-2 py-0.5 rounded-[3px] bg-[#EEF8F7] text-[#123E40] border border-[#BDCEC8]">
                        MODULE {m.num}
                      </span>
                      <Icon className="h-5 w-5 text-[#237277]" />
                    </div>

                    <h3 className="text-base font-bold text-[#172825]">{m.title}</h3>
                    <p className="text-xs italic text-[#237277] mt-1">{m.tagline}</p>

                    <div className="mt-4 pt-3 border-t border-[#DCE6E2] space-y-2 text-xs">
                      <div className="text-[#40524E]">
                        <strong className="text-[#172825]">Problem:</strong> {m.problem}
                      </div>

                      <div className="space-y-1 pt-1">
                        <strong className="text-[#172825] block text-[11px] uppercase tracking-wider font-mono">
                          Key Capabilities:
                        </strong>
                        <ul className="list-disc list-inside text-[#40524E] space-y-0.5 text-[11px]">
                          {m.capabilities.slice(0, 3).map((c, idx) => (
                            <li key={idx} className="line-clamp-1">{c}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>

                  <div className="mt-6 pt-4 border-t border-[#DCE6E2] flex items-center justify-between">
                    <span className="text-[11px] text-[#687A75] font-mono">Evidence-Based</span>
                    <Link to={m.route}>
                      <Button variant="outline" size="sm" className="gap-1.5 text-xs border-[#BDCEC8]">
                        <span>Explore Module</span>
                        <ArrowRight className="h-3 w-3" />
                      </Button>
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* 6. TECHNICAL ARCHITECTURE SECTION */}
      <section id="architecture" className="py-20 border-b border-[#DCE6E2] bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="max-w-3xl mb-12">
            <div className="inline-flex items-center gap-1.5 text-xs font-mono font-bold text-[#237277] uppercase tracking-wider">
              <span>Engineering Specifications</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-[#172825] mt-2 font-sans">
              Clean Decoupled Architecture
            </h2>
            <p className="mt-3 text-sm md:text-base text-[#40524E] leading-relaxed">
              MASTERY is architected as a modular monolith backend powered by FastAPI and PostgreSQL with Row-Level Security, consumed by a reactive, decoupled React + Vite frontend.
            </p>
          </div>

          <div className="p-8 rounded-[6px] bg-[#F7FAF9] border border-[#DCE6E2] space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              {[
                {
                  layer: '1. Presentation Layer',
                  tech: 'React 18, Vite, Tailwind, Lucide',
                  details: 'Public Landing Page, Role-Aware Workspace Shell, Interactive Demo Guide, Brutalist Containers.',
                },
                {
                  layer: '2. Application Layer',
                  tech: 'FastAPI Decoupled Monolith',
                  details: 'Seven isolated business module routers, Unified Dashboard aggregator, JWT & RBAC dependency injection.',
                },
                {
                  layer: '3. Intelligence Layer',
                  tech: 'scikit-learn & Rule Engines',
                  details: 'Temporal feature engineering, sufficiency gates, topic mastery attribution, risk explanations, gap detection.',
                },
                {
                  layer: '4. Data & Storage Layer',
                  tech: 'PostgreSQL & Supabase RLS',
                  details: '28 normalized relational entities, Row-Level Security policies, immutable cryptographic audit tables.',
                },
                {
                  layer: '5. Ethical AI Boundary',
                  tech: 'Charter § 4.2 Privacy Firewall',
                  details: 'Placement Officer risk isolation, zero webcam surveillance, separate academic vs practical evidence.',
                },
              ].map((item, i) => (
                <div key={i} className="p-4 rounded-[4px] bg-white border border-[#DCE6E2] flex flex-col justify-between">
                  <div>
                    <span className="font-mono text-[10px] font-bold text-[#237277] uppercase">{item.layer}</span>
                    <div className="font-bold text-xs text-[#172825] mt-1">{item.tech}</div>
                    <p className="text-[11px] text-[#40524E] mt-2 leading-relaxed">{item.details}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* 7. CORE DIFFERENTIATORS */}
      <section id="differentiators" className="py-20 border-b border-[#DCE6E2] bg-[#F7FAF9]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="max-w-3xl mb-12">
            <div className="inline-flex items-center gap-1.5 text-xs font-mono font-bold text-[#237277] uppercase tracking-wider">
              <span>Why MASTERY is Different</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-[#172825] mt-2 font-sans">
              Built on Evidence, Explainability & Digital Trust
            </h2>
            <p className="mt-3 text-sm md:text-base text-[#40524E] leading-relaxed">
              We reject arbitrary composite scoring, facial surveillance, and premature machine learning predictions.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                title: 'Temporal Leakage Prevention',
                desc: 'Prediction models only evaluate features created before the strict prediction cutoff date. Final exam grades are never leaked into continuous predictors.',
              },
              {
                title: 'Evidence Sufficiency Checks',
                desc: 'Students with missing medical records are flagged as INSUFFICIENT_EVIDENCE. The platform NEVER assigns an arbitrary zero score.',
              },
              {
                title: 'Placement Privacy Firewall',
                desc: 'Recruiters can view verified practical project competencies, but are strictly barred from viewing student academic risk scores.',
              },
              {
                title: 'Faculty Human-in-the-Loop',
                desc: 'AI generates recommendations, but only professors can approve academic interventions and verify practical project submissions.',
              },
            ].map((diff, i) => (
              <div key={i} className="p-5 rounded-[6px] bg-white border border-[#DCE6E2] shadow-subtle">
                <CheckCircle2 className="h-5 w-5 text-[#237277] mb-2" />
                <h3 className="font-bold text-sm text-[#172825]">{diff.title}</h3>
                <p className="text-xs text-[#40524E] mt-2 leading-relaxed">{diff.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 8. ROLE-BASED ECOSYSTEM */}
      <section id="ecosystem" className="py-20 border-b border-[#DCE6E2] bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="max-w-3xl mb-12">
            <div className="inline-flex items-center gap-1.5 text-xs font-mono font-bold text-[#237277] uppercase tracking-wider">
              <span>Stakeholder Personas</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-[#172825] mt-2 font-sans">
              Tailored Intelligence for Every Institutional Role
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            {[
              { role: 'Students', desc: 'Inspect topic mastery, submit project evidence, review approved support plans, explore career roadmaps.' },
              { role: 'Faculty', desc: 'Verify assessment ledgers, review risk signals, approve intervention plans, verify practical portfolios.' },
              { role: 'Institution Admins', desc: 'Monitor cohort health, track syllabus coverage, evaluate intervention recovery across departments.' },
              { role: 'Placement Officers', desc: 'Inspect verified project portfolios and role skill gaps under ethical privacy isolation.' },
              { role: 'Platform Admins', desc: 'Manage institutional tenants, monitor system telemetry, audit cryptographic ledgers.' },
            ].map((eco, i) => (
              <div key={i} className="p-4 rounded-[4px] bg-[#F7FAF9] border border-[#DCE6E2] flex flex-col justify-between">
                <div>
                  <span className="font-bold text-xs text-[#123E40]">{eco.role}</span>
                  <p className="text-[11px] text-[#40524E] mt-2 leading-relaxed">{eco.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 9. FINAL CTA SECTION */}
      <section className="py-20 bg-[#123E40] text-white">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <Badge variant="brand" className="mb-4 bg-[#EEF8F7] text-[#123E40]">
            READY FOR TECHNICAL EVALUATION
          </Badge>
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight font-sans">
            Make academic progress visible. <br />
            Make support actionable.
          </h2>
          <p className="mt-4 text-sm md:text-base text-slate-300 max-w-xl mx-auto">
            Experience the complete MASTERY platform across all seven modules using our preloaded, four-scenario synthetic demo environment.
          </p>

          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <Link to="/app/dashboard">
              <Button variant="primary" size="lg" className="bg-[#237277] hover:bg-[#18575A] text-white gap-2">
                <Play className="h-4 w-4" />
                <span>Launch Interactive Demo Workspace</span>
              </Button>
            </Link>
            <Link to="/demo-guide">
              <Button variant="outline" size="lg" className="border-slate-500 text-white hover:bg-[#18575A]">
                <span>Open Walkthrough Guide</span>
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* 10. INSTITUTIONAL FOOTER */}
      <footer className="py-8 bg-[#0C2D2F] text-slate-400 border-t border-[#18575A] text-xs">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-bold text-white">MASTERY</span>
            <span>· Beyond Marks. Towards Mastery.</span>
          </div>
          <div className="text-center md:text-right font-mono text-[11px] text-slate-400">
            SRUJAN 2026 · Problem Statement AI-03 · Team VARY
            <br />
            Track: AI, CyberSecurity and Digital Trust
          </div>
        </div>
      </footer>
    </div>
  );
};
