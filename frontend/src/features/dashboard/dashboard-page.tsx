import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Server,
  Database,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  FileText,
  Compass,
  Briefcase,
  AlertTriangle,
  Award,
} from 'lucide-react';
import { healthService } from '@/services/health-service';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { StatusIndicator } from '@/components/ui/status-indicator';
import { Link } from 'react-router-dom';

export const DashboardPage: React.FC = () => {
  const { data: health, isLoading: isAppLoading, error: appError } = useQuery({
    queryKey: ['backend-health'],
    queryFn: healthService.checkAppHealth,
    refetchInterval: 30000,
  });

  const { data: dbHealth, isLoading: isDbLoading } = useQuery({
    queryKey: ['database-health'],
    queryFn: healthService.checkDatabaseHealth,
    refetchInterval: 30000,
  });

  const intelligenceOutputs = [
    {
      title: 'Academic Risk Engine',
      description: 'Identifies students requiring academic intervention without stigmatization.',
      focus: 'Early warning, attendance trends, assessment drops, explainable risk factors.',
      icon: AlertTriangle,
      color: 'border-l-amber-500',
      badge: 'Output 1 / 3',
    },
    {
      title: 'Learning Mastery Engine',
      description: 'Measures demonstrated topic-level understanding from independent assessments.',
      focus: 'Unit-wise mastery heatmaps, conceptual gaps, syllabus outcome alignment.',
      icon: Award,
      color: 'border-l-blue-500',
      badge: 'Output 2 / 3',
    },
    {
      title: 'Career Readiness Engine',
      description: 'Evaluates practical competencies against verified industry role frameworks.',
      focus: 'Coding/SQL demonstrations, GitHub verification, role skill-gap analysis.',
      icon: Briefcase,
      color: 'border-l-emerald-500',
      badge: 'Output 3 / 3',
    },
  ];

  const modules = [
    {
      id: '01',
      title: 'Academic Data Intelligence Hub',
      desc: 'Institutional records, attendance, internal marks, CSV/Excel imports, validation & evidence timeline.',
      phase: 'Phase 02',
      path: '/academic-data',
      icon: Database,
    },
    {
      id: '02',
      title: 'AI Syllabus & Competency Intelligence',
      desc: 'Syllabus PDF extraction, unit/topic breakdown, learning outcomes, dependency mapping & faculty approvals.',
      phase: 'Phase 03',
      path: '/syllabus',
      icon: FileText,
    },
    {
      id: '03',
      title: 'Continuous Learning & Assessment Engine',
      desc: 'AI question generation, faculty verification, MCQs, descriptive answers, coding & SQL assessments.',
      phase: 'Phase 04',
      path: '/assessments',
      icon: CheckCircle2,
    },
    {
      id: '04',
      title: 'Evidence Calibration & Student Mastery',
      desc: 'Topic-level mastery scoring, provenance tracking, evidence mismatch detection & mastery heatmaps.',
      phase: 'Phase 05',
      path: '/mastery',
      icon: Award,
    },
    {
      id: '05',
      title: 'Explainable Academic Risk Prediction',
      desc: 'Multi-factor risk screening, historical performance models, explainable alerts & faculty reviews.',
      phase: 'Phase 06',
      path: '/academic-risk',
      icon: AlertTriangle,
    },
    {
      id: '06',
      title: 'Personalized Intervention & Student Growth',
      desc: 'Targeted support plans, AI recommendation engine, mentor assignments & progress tracking.',
      phase: 'Phase 07',
      path: '/interventions',
      icon: Compass,
    },
    {
      id: '07',
      title: 'Industry & Placement Readiness Intelligence',
      desc: 'Role competency frameworks, practical benchmarks, skill gap analysis & placement readiness radar.',
      phase: 'Phase 08',
      path: '/career-readiness',
      icon: Briefcase,
    },
  ];

  return (
    <div className="space-y-8">
      {/* Platform Title Banner */}
      <div className="border-b border-slate-200 pb-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              MASTERY Architecture & Overview
            </h1>
            <p className="text-sm text-slate-600 mt-1">
              AI-powered Student Performance Analytics, Academic Risk Prediction and Career Readiness Platform.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="font-mono text-xs">
              Phase 01 / 11 Complete
            </Badge>
            <Badge variant="info" className="text-xs">
              Modular Monolith
            </Badge>
          </div>
        </div>
      </div>

      {/* Triad Intelligence Philosophy Notice */}
      <div className="bg-slate-900 text-white rounded-lg p-6 shadow-sm border border-slate-800">
        <div className="max-w-3xl space-y-2">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-blue-400">
            <ShieldCheck className="h-4 w-4" />
            <span>Foundational Design Principle</span>
          </div>
          <h2 className="text-lg font-bold">Beyond Marks. Towards Mastery.</h2>
          <p className="text-sm text-slate-300 leading-relaxed">
            MASTERY maintains three distinct intelligence outputs. Marks, mastery and career readiness measure fundamentally different dimensions and are{' '}
            <strong className="text-white underline decoration-blue-500 decoration-2">
              never combined into an arbitrary aggregate student score
            </strong>
            .
          </p>
        </div>

        {/* 3 Output Pillars Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          {intelligenceOutputs.map((out) => (
            <div
              key={out.title}
              className={`bg-slate-800/80 rounded-md p-4 border-l-4 ${out.color} border-slate-700`}
            >
              <div className="flex items-center justify-between mb-2">
                <out.icon className="h-4 w-4 text-slate-300" />
                <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">
                  {out.badge}
                </span>
              </div>
              <h3 className="font-semibold text-sm text-white">{out.title}</h3>
              <p className="text-xs text-slate-300 mt-1.5 leading-snug">{out.description}</p>
              <p className="text-[11px] text-slate-400 mt-2 font-mono">
                Focus: {out.focus}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Backend & Subsystem Live Connectivity Diagnostic Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Server className="h-4 w-4 text-blue-600" />
            <CardTitle>System & Subsystem Connectivity</CardTitle>
          </div>
          <Badge variant="outline" className="font-mono text-[11px]">
            Live Diagnostics
          </Badge>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Core API */}
            <div className="p-4 rounded-md border border-slate-200 bg-slate-50">
              <div className="text-xs text-slate-500 font-medium">Core API Service</div>
              <div className="mt-2 flex items-center justify-between">
                <span className="text-sm font-semibold text-slate-800">FastAPI REST</span>
                <StatusIndicator
                  status={isAppLoading ? 'loading' : health ? 'healthy' : 'error'}
                  label={health ? 'Operational' : 'Unavailable'}
                />
              </div>
              <div className="mt-2 text-[11px] text-slate-500 font-mono">
                Port: 8000 | v0.1.0
              </div>
            </div>

            {/* Database */}
            <div className="p-4 rounded-md border border-slate-200 bg-slate-50">
              <div className="text-xs text-slate-500 font-medium">PostgreSQL / Supabase</div>
              <div className="mt-2 flex items-center justify-between">
                <span className="text-sm font-semibold text-slate-800">Database Engine</span>
                <StatusIndicator
                  status={
                    isDbLoading
                      ? 'loading'
                      : dbHealth?.status === 'connected'
                      ? 'connected'
                      : 'unconfigured'
                  }
                  label={
                    dbHealth?.status === 'connected'
                      ? 'Connected'
                      : 'Unconfigured'
                  }
                />
              </div>
              <div className="mt-2 text-[11px] text-slate-500 truncate" title={dbHealth?.message || 'Database not yet wired'}>
                {dbHealth?.message || 'Ready for DATABASE_URL'}
              </div>
            </div>

            {/* AI Service Layer */}
            <div className="p-4 rounded-md border border-slate-200 bg-slate-50">
              <div className="text-xs text-slate-500 font-medium">AI Service Layer</div>
              <div className="mt-2 flex items-center justify-between">
                <span className="text-sm font-semibold text-slate-800">OpenAI Gateway</span>
                <StatusIndicator
                  status={health?.services?.ai_engine === 'configured' ? 'connected' : 'unconfigured'}
                  label={health?.services?.ai_engine === 'configured' ? 'Configured' : 'Standby'}
                />
              </div>
              <div className="mt-2 text-[11px] text-slate-500 font-mono">
                Model: gpt-4o-mini
              </div>
            </div>

            {/* Security / RBAC */}
            <div className="p-4 rounded-md border border-slate-200 bg-slate-50">
              <div className="text-xs text-slate-500 font-medium">Auth & RBAC</div>
              <div className="mt-2 flex items-center justify-between">
                <span className="text-sm font-semibold text-slate-800">Supabase Auth</span>
                <StatusIndicator
                  status={health?.services?.supabase_auth === 'configured' ? 'connected' : 'unconfigured'}
                  label={health?.services?.supabase_auth === 'configured' ? 'Configured' : 'Standby'}
                />
              </div>
              <div className="mt-2 text-[11px] text-slate-500 font-mono">
                Roles: Student, Faculty, Admin
              </div>
            </div>
          </div>

          {appError && (
            <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-md text-xs text-amber-800 flex items-start gap-2">
              <AlertCircle className="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <strong>Backend is currently offline or unreachable at http://localhost:8000/api/v1.</strong>
                <p className="mt-0.5">Start the FastAPI backend with: <code className="bg-amber-100 px-1 py-0.5 rounded font-mono">cd backend; .venv\Scripts\uvicorn app.main:app --reload</code></p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* The Seven Product Modules Roadmap Grid */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-slate-900">Seven Product Domains</h2>
            <p className="text-xs text-slate-500">
              Architectural boundaries established in Phase 01. Implementation scheduled across Phases 02–08.
            </p>
          </div>
          <Badge variant="outline" className="font-mono text-xs">
            Contract-driven
          </Badge>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {modules.map((m) => (
            <Card key={m.id} hover className="flex flex-col justify-between">
              <CardContent className="p-5">
                <div className="flex items-center justify-between mb-3">
                  <div className="h-8 w-8 rounded bg-slate-100 text-slate-700 flex items-center justify-center font-bold text-xs">
                    {m.id}
                  </div>
                  <Badge variant="default" className="text-[10px] font-mono">
                    {m.phase}
                  </Badge>
                </div>
                <h3 className="text-sm font-semibold text-slate-900 leading-snug">{m.title}</h3>
                <p className="text-xs text-slate-500 mt-2 leading-relaxed">{m.desc}</p>
              </CardContent>
              <div className="px-5 py-3 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
                <span className="text-[11px] font-medium text-slate-400">Domain View</span>
                <Link
                  to={m.path}
                  className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-700 transition-colors"
                >
                  <span>Inspect Spec</span>
                  <ArrowRight className="h-3 w-3" />
                </Link>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};
