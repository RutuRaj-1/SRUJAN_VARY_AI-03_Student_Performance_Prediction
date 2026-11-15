import { Link } from 'react-router-dom';
import { ArrowRight, CheckCircle2, ShieldCheck, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { MODULES_DATA } from './modules-data';

export function ModulesOverviewPage() {
  return (
    <div className="py-16">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="max-w-3xl">
          <Badge variant="outline" className="text-primary font-mono text-xs uppercase tracking-wider mb-4">
            MASTERY Module Suite
          </Badge>
          <h1 className="text-4xl md:text-5xl font-black text-slate-900 tracking-tight">
            The Seven Specialized Business Modules
          </h1>
          <p className="mt-5 text-lg text-slate-600 leading-relaxed">
            MASTERY is engineered as a modular monolith of seven specialized intelligence engines.
            Each module addresses an explicit point of failure in higher education, functioning
            both as an autonomous service and as part of an interconnected intelligence loop.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to="/app">
              <Button size="lg" className="font-semibold shadow-sm">
                Open All Modules in Workspace
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link to="/solution">
              <Button variant="outline" size="lg" className="font-semibold">
                View 7-Stage Pipeline
              </Button>
            </Link>
          </div>
        </div>

        {/* Modules Grid */}
        <div className="mt-16 space-y-12">
          {MODULES_DATA.map((module) => {
            const Icon = module.icon;
            return (
              <Card key={module.code} className="border-slate-200 bg-white shadow-sm overflow-hidden">
                <div className="border-b border-slate-100 bg-slate-50/70 p-6 flex flex-wrap items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div className={`p-2.5 rounded border ${module.accent}`}>
                      <Icon className="h-6 w-6" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono font-bold text-primary">MODULE {module.num}</span>
                        <span className="text-xs text-slate-400">•</span>
                        <span className="text-xs font-mono text-slate-500">{module.code}</span>
                      </div>
                      <h2 className="text-2xl font-bold text-slate-900 mt-0.5">{module.title}</h2>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Link to={`/modules/${module.slug}`}>
                      <Button variant="outline" size="sm" className="font-semibold text-xs">
                        Deep Dive Specification
                        <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
                      </Button>
                    </Link>
                    <Link to={module.appRoute}>
                      <Button size="sm" className="font-semibold text-xs bg-slate-900 text-white hover:bg-slate-800">
                        Launch in App
                        <ExternalLink className="ml-1.5 h-3.5 w-3.5" />
                      </Button>
                    </Link>
                  </div>
                </div>

                <CardContent className="p-6 md:p-8">
                  <p className="text-base text-slate-700 leading-relaxed font-medium mb-4">
                    {module.tagline}
                  </p>

                  <div className="bg-amber-50/70 border border-amber-200/80 p-4 rounded mb-6 text-xs text-amber-900">
                    <span className="font-bold uppercase tracking-wider font-mono mr-2">Structural Problem Solved:</span>
                    {module.problemSolved}
                  </div>

                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 pt-2">
                    <div>
                      <div className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500 mb-3">
                        Core Capabilities
                      </div>
                      <ul className="space-y-2">
                        {module.coreCapabilities.slice(0, 4).map((cap, i) => (
                          <li key={i} className="text-xs text-slate-700 flex items-start gap-2">
                            <CheckCircle2 className="h-3.5 w-3.5 text-primary shrink-0 mt-0.5" />
                            <span>{cap}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div>
                      <div className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500 mb-3">
                        Inputs & Artifacts
                      </div>
                      <div className="space-y-3">
                        <div>
                          <div className="text-[11px] font-mono text-slate-400 uppercase">Ingests:</div>
                          <p className="text-xs text-slate-600 mt-0.5">{module.inputs.join(', ')}</p>
                        </div>
                        <div>
                          <div className="text-[11px] font-mono text-slate-400 uppercase">Generates:</div>
                          <p className="text-xs text-slate-600 mt-0.5">{module.outputs.join(', ')}</p>
                        </div>
                      </div>
                    </div>

                    <div>
                      <div className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500 mb-3">
                        Governance & Assurance
                      </div>
                      <div className="bg-slate-50 border border-slate-200 p-3 rounded text-xs text-slate-600 leading-relaxed flex items-start gap-2">
                        <ShieldCheck className="h-4 w-4 text-success shrink-0 mt-0.5" />
                        <div>
                          <span className="font-semibold text-slate-800">Tamper-Evident Evidence: </span>
                          {module.evidenceGovernance}
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Bottom CTA */}
        <div className="mt-16 bg-slate-900 text-white p-8 md:p-12 text-center border border-slate-800">
          <h2 className="text-3xl font-black tracking-tight">Experience All Seven Modules in the Workspace</h2>
          <p className="mt-3 text-sm text-slate-300 max-w-2xl mx-auto">
            Interact with live student records, curriculum graphs, risk predictions, and intervention plans across all personas.
          </p>
          <div className="mt-6 flex justify-center gap-3">
            <Link to="/app">
              <Button size="lg" className="bg-white text-slate-900 hover:bg-slate-100 font-semibold">
                Launch Academic Workspace
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
