import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Layers, ArrowLeft, CheckCircle2 } from 'lucide-react';
import { Link } from 'react-router-dom';

export interface ModuleSpecProps {
  id: string;
  name: string;
  phase: string;
  tagline: string;
  description: string;
  responsibilities: string[];
  dataInputs: string[];
  dataOutputs: string[];
  intelligenceType: string;
  backendRoute: string;
}

export const ModuleSpecView: React.FC<ModuleSpecProps> = ({
  id,
  name,
  phase,
  tagline,
  description,
  responsibilities,
  dataInputs,
  dataOutputs,
  intelligenceType,
  backendRoute,
}) => {
  return (
    <div className="space-y-6">
      {/* Navigation Breadcrumb */}
      <div>
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-800 transition-colors"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          <span>Back to Architecture Overview</span>
        </Link>
      </div>

      {/* Header Banner */}
      <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="h-12 w-12 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center font-bold text-lg border border-blue-100">
              {id}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold text-slate-900">{name}</h1>
                <Badge variant="outline" className="font-mono text-xs">
                  {phase}
                </Badge>
              </div>
              <p className="text-xs text-blue-600 font-medium mt-0.5">{tagline}</p>
              <p className="text-xs text-slate-500 mt-2 max-w-2xl">{description}</p>
            </div>
          </div>
          <div>
            <Badge variant="default" className="text-xs font-mono py-1">
              Status: Architectural Contract Ready
            </Badge>
          </div>
        </div>
      </div>

      {/* Details Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Domain Responsibilities */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
              <CardTitle>Core Responsibilities</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2.5 text-xs text-slate-700">
              {responsibilities.map((r, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-blue-500 mt-1.5 shrink-0" />
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        {/* Integration Contract */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Layers className="h-4 w-4 text-blue-600" />
              <CardTitle>Architectural Integration Contract</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4 text-xs">
            <div>
              <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Data Inputs
              </div>
              <div className="flex flex-wrap gap-1.5">
                {dataInputs.map((inp, idx) => (
                  <Badge key={idx} variant="default" className="font-mono text-[11px]">
                    {inp}
                  </Badge>
                ))}
              </div>
            </div>

            <div>
              <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Intelligence Outputs
              </div>
              <div className="flex flex-wrap gap-1.5">
                {dataOutputs.map((out, idx) => (
                  <Badge key={idx} variant="info" className="font-mono text-[11px]">
                    {out}
                  </Badge>
                ))}
              </div>
            </div>

            <div className="pt-2 border-t border-slate-100 grid grid-cols-2 gap-2 text-slate-600">
              <div>
                <span className="font-semibold block text-slate-800">Intelligence Classification:</span>
                <span className="text-[11px] font-mono">{intelligenceType}</span>
              </div>
              <div>
                <span className="font-semibold block text-slate-800">Backend API Route:</span>
                <span className="text-[11px] font-mono">{backendRoute}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
