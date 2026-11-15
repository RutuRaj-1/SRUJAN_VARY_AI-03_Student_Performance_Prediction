import { useParams, Link, Navigate } from 'react-router-dom';
import {
  ArrowLeft,
  ArrowRight,
  ExternalLink,
  CheckCircle2,
  ShieldCheck,
  Cpu,
  GraduationCap,
  Sparkles,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { MODULES_DATA } from './modules-data';

export function ModuleDetailPage() {
  const { moduleSlug } = useParams<{ moduleSlug: string }>();

  const moduleIndex = MODULES_DATA.findIndex((m) => m.slug === moduleSlug);

  if (moduleIndex === -1) {
    return <Navigate to="/modules" replace />;
  }

  const module = MODULES_DATA[moduleIndex];
  const prevModule = moduleIndex > 0 ? MODULES_DATA[moduleIndex - 1] : null;
  const nextModule = moduleIndex < MODULES_DATA.length - 1 ? MODULES_DATA[moduleIndex + 1] : null;

  const Icon = module.icon;

  return (
    <div className="py-16">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Navigation Breadcrumb */}
        <div className="mb-8 flex items-center justify-between">
          <Link
            to="/modules"
            className="inline-flex items-center text-xs font-mono text-slate-500 hover:text-slate-900 transition-colors"
          >
            <ArrowLeft className="mr-1.5 h-3.5 w-3.5" />
            Back to All Modules Overview
          </Link>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-slate-400">
              Module {module.num} of 07
            </span>
          </div>
        </div>

        {/* Hero Section */}
        <div className="bg-white border border-slate-200 p-8 md:p-12 shadow-sm">
          <div className="flex flex-wrap items-center gap-3 mb-4">
            <Badge variant="outline" className="font-mono text-xs uppercase tracking-wider text-primary border-primary/30">
              MODULE {module.num}
            </Badge>
            <Badge variant="brand" className="font-mono text-xs uppercase">
              {module.code} Specification
            </Badge>
          </div>

          <div className="flex items-start gap-4">
            <div className={`p-3 rounded border hidden sm:block ${module.accent}`}>
              <Icon className="h-8 w-8" />
            </div>
            <div>
              <h1 className="text-3xl md:text-5xl font-black text-slate-900 tracking-tight">
                {module.title}
              </h1>
              <p className="mt-4 text-xl text-slate-600 font-medium leading-relaxed">
                {module.tagline}
              </p>
            </div>
          </div>

          <div className="mt-8 flex flex-wrap gap-4 pt-6 border-t border-slate-100">
            <Link to={module.appRoute}>
              <Button size="lg" className="font-semibold shadow-sm">
                Launch {module.code} in Workspace
                <ExternalLink className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link to="/solution">
              <Button variant="outline" size="lg" className="font-semibold">
                View in Pipeline Flow
              </Button>
            </Link>
          </div>
        </div>

        {/* Problem & Solution Comparison */}
        <div className="mt-12 grid md:grid-cols-2 gap-8">
          <Card className="border-red-200 bg-red-50/40 shadow-sm">
            <CardContent className="p-6 md:p-8">
              <div className="flex items-center gap-2 text-red-900 font-mono text-xs font-bold uppercase tracking-wider mb-3">
                <span className="h-2 w-2 rounded-full bg-red-600" />
                The Structural Flaw in Conventional EdTech
              </div>
              <h2 className="text-xl font-bold text-slate-900 mb-3">
                Why Legacy Higher-Ed Workflows Fail
              </h2>
              <p className="text-sm text-slate-700 leading-relaxed">
                {module.problemSolved}
              </p>
            </CardContent>
          </Card>

          <Card className="border-emerald-200 bg-emerald-50/40 shadow-sm">
            <CardContent className="p-6 md:p-8">
              <div className="flex items-center gap-2 text-emerald-900 font-mono text-xs font-bold uppercase tracking-wider mb-3">
                <span className="h-2 w-2 rounded-full bg-emerald-600" />
                The MASTERY Architectural Remedy
              </div>
              <h2 className="text-xl font-bold text-slate-900 mb-3">
                Deterministic, Evidence-Backed Automation
              </h2>
              <p className="text-sm text-slate-700 leading-relaxed">
                {module.description}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Core Capabilities */}
        <div className="mt-12 bg-white border border-slate-200 p-8 shadow-sm">
          <div className="flex items-center gap-2 text-xs font-mono font-bold uppercase tracking-wider text-slate-500 mb-2">
            <Sparkles className="h-4 w-4 text-primary" />
            Verified System Features
          </div>
          <h2 className="text-2xl font-bold text-slate-900 mb-6">
            Core Technical Capabilities
          </h2>

          <div className="grid md:grid-cols-2 gap-4">
            {module.coreCapabilities.map((cap, i) => (
              <div
                key={i}
                className="flex items-start gap-3 p-4 rounded bg-slate-50 border border-slate-100 hover:border-slate-200 transition-colors"
              >
                <div className="mt-0.5 p-1 rounded bg-primary/10 text-primary">
                  <CheckCircle2 className="h-4 w-4" />
                </div>
                <div>
                  <span className="text-sm font-semibold text-slate-900 block mb-1">
                    {cap}
                  </span>
                  <span className="text-xs text-slate-500">
                    Production-tested algorithm integrated into the MASTERY unified runtime.
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Technical Architecture & Inputs/Outputs */}
        <div className="mt-12 grid md:grid-cols-3 gap-8">
          <Card className="border-slate-200 bg-white shadow-sm md:col-span-2">
            <CardContent className="p-6 md:p-8">
              <div className="flex items-center gap-2 text-xs font-mono font-bold uppercase tracking-wider text-slate-500 mb-2">
                <Cpu className="h-4 w-4 text-primary" />
                Under the Hood
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-3">Technical Architecture</h3>
              <p className="text-sm text-slate-700 leading-relaxed mb-6 font-mono bg-slate-50 border border-slate-200 p-4 rounded">
                {module.technicalArchitecture}
              </p>

              <div className="grid sm:grid-cols-2 gap-6 pt-4 border-t border-slate-100">
                <div>
                  <div className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500 mb-2">
                    Ingestion Inputs
                  </div>
                  <ul className="space-y-1.5">
                    {module.inputs.map((inItem, idx) => (
                      <li key={idx} className="text-xs text-slate-700 flex items-start gap-1.5">
                        <span className="text-primary font-bold">•</span>
                        <span>{inItem}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <div className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500 mb-2">
                    Verified Outputs
                  </div>
                  <ul className="space-y-1.5">
                    {module.outputs.map((outItem, idx) => (
                      <li key={idx} className="text-xs text-slate-700 flex items-start gap-1.5">
                        <CheckCircle2 className="h-3.5 w-3.5 text-success shrink-0 mt-0.5" />
                        <span>{outItem}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-200 bg-white shadow-sm flex flex-col justify-between">
            <CardContent className="p-6 md:p-8">
              <div className="flex items-center gap-2 text-xs font-mono font-bold uppercase tracking-wider text-slate-500 mb-2">
                <ShieldCheck className="h-4 w-4 text-success" />
                Integrity & Governance
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-3">Evidence Provenance</h3>
              <p className="text-xs text-slate-600 leading-relaxed mb-6">
                {module.evidenceGovernance}
              </p>

              <div className="pt-4 border-t border-slate-100">
                <div className="flex items-center gap-2 text-xs font-mono font-bold uppercase tracking-wider text-slate-500 mb-2">
                  <GraduationCap className="h-4 w-4 text-primary" />
                  Academic Impact
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">
                  {module.academicImpact}
                </p>
              </div>
            </CardContent>

            <div className="p-6 bg-slate-50 border-t border-slate-100">
              <Link to={module.appRoute} className="w-full block">
                <Button className="w-full text-xs font-semibold">
                  Open {module.code} Interactive View
                  <ExternalLink className="ml-1.5 h-3.5 w-3.5" />
                </Button>
              </Link>
            </div>
          </Card>
        </div>

        {/* Previous / Next Module Navigation */}
        <div className="mt-16 pt-8 border-t border-slate-200 flex flex-wrap items-center justify-between gap-4">
          {prevModule ? (
            <Link
              to={`/modules/${prevModule.slug}`}
              className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 hover:text-slate-900 transition-colors"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>
                Previous: <span className="font-mono text-xs">{prevModule.code}</span> — {prevModule.title}
              </span>
            </Link>
          ) : (
            <div />
          )}

          {nextModule ? (
            <Link
              to={`/modules/${nextModule.slug}`}
              className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 hover:text-slate-900 transition-colors"
            >
              <span>
                Next: <span className="font-mono text-xs">{nextModule.code}</span> — {nextModule.title}
              </span>
              <ArrowRight className="h-4 w-4" />
            </Link>
          ) : (
            <div />
          )}
        </div>
      </div>
    </div>
  );
}
