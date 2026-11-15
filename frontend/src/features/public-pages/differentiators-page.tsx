import { Link } from 'react-router-dom';
import {
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  Eye,
  Lock,
  UserCheck,
  Cpu,
  BarChart2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';

const DIFFERENTIATORS = [
  {
    title: 'Fine-Grained Topic Mastery vs Cumulative Percentages',
    icon: BarChart2,
    accent: 'bg-primary/10 text-primary',
    conventional:
      'Reports a single blunt score (e.g. 74% in Data Structures). Conceals that the student scored 0% on Pointers and Dynamic Memory Allocation, guaranteeing failure in Advanced Operating Systems.',
    mastery:
      'Deconstructs every course into a Directed Acyclic Graph (DAG) of micro-topics and evaluates mastery per node (0–100%). Flags specific prerequisite debt before downstream courses begin.',
  },
  {
    title: 'Explainable SHAP Factor Attribution vs Black-Box Risk Prediction',
    icon: Eye,
    accent: 'bg-warning/10 text-warning',
    conventional:
      'Outputs an opaque risk percentage or red warning badge with no justification. Faculty cannot tell whether the risk is driven by attendance, prerequisite gaps, or test scores.',
    mastery:
      'Calculates SHAP (SHapley Additive exPlanations) values for every prediction. Faculty advisors see the exact top contributory factors (e.g., Attendance drop -18%, Topic Deficit +24%, Missing Labs +12%).',
  },
  {
    title: 'Ethical Privacy Firewall & Anti-Bias Architecture',
    icon: Lock,
    accent: 'bg-rose-50 text-rose-700',
    conventional:
      'Consolidates all student data into flat tables where campus recruiters or unvetted staff can view behavioral flags, mental health notes, or academic risk warnings.',
    mastery:
      'Enforces an architectural privacy firewall. Placement Officers are cryptographically locked out from risk indicators and personal struggles. Recruiter views are strictly limited to verified competency mastery.',
  },
  {
    title: 'Mandatory Human-in-the-Loop Faculty Governance',
    icon: UserCheck,
    accent: 'bg-emerald-50 text-emerald-700',
    conventional:
      'Fully autonomous AI agents dispatching unverified, hallucinated remedial assignments directly to students without educator awareness or validation.',
    mastery:
      'AI drafts scaffolded remedial plans, but no intervention is dispatched without formal faculty advisor review and cryptographic approval sign-off.',
  },
  {
    title: 'Deterministic Bloom’s Taxonomy & OBE Attainment',
    icon: Cpu,
    accent: 'bg-blue-50 text-blue-700',
    conventional:
      'Course Learning Outcome (CLO) attainment is manually calculated on spreadsheets at semester end using fabricated averages to pass NBA/NAAC accreditation audits.',
    mastery:
      'Programmatically computes real-time CLO attainment from question-level Bloom’s taxonomy metadata (L1 to L6) and continuous formative assessment evidence.',
  },
  {
    title: 'Zero Demographics Ingestion & Algorithmic Fairness',
    icon: ShieldCheck,
    accent: 'bg-purple-50 text-purple-700',
    conventional:
      'ML models ingest gender, ethnicity, zip codes, and parental income, unintentionally learning historical societal biases and penalizing disadvantaged cohorts.',
    mastery:
      'Zero demographic, financial, or protected class features are ingested. All predictions rely strictly on time-series academic evidence and demonstrated mastery.',
  },
];

const COMPARISON_ROWS = [
  {
    feature: 'Academic Granularity',
    conventional: 'Course-level percentage or letter grade (A, B, C)',
    mastery: 'Sub-topic node mastery (0–100%) mapped to Bloom’s Taxonomy',
  },
  {
    feature: 'Risk Detection Timing',
    conventional: 'Post-mortem after semester exam failure',
    mastery: 'Weeks 3–6 of semester based on velocity & prerequisite deficits',
  },
  {
    feature: 'AI Explainability',
    conventional: 'Opaque black-box score or absent altogether',
    mastery: '100% factor attribution via SHAP feature importance vectors',
  },
  {
    feature: 'Intervention Approval',
    conventional: 'None or unreviewed automated chatbots',
    mastery: 'Mandatory Human-in-the-Loop faculty advisor sign-off',
  },
  {
    feature: 'Placement Privacy Firewall',
    conventional: 'Shared database without fine-grained role walls',
    mastery: 'Cryptographically enforced role firewall (403 on risk endpoints)',
  },
  {
    feature: 'Curriculum Representation',
    conventional: 'Static text PDF syllabi',
    mastery: 'Dynamic Directed Acyclic Graph (DAG) with dependency checking',
  },
  {
    feature: 'Industry Competency Alignment',
    conventional: 'Outdated static course descriptions',
    mastery: 'Live alignment to O*NET/ESCO standardized role frameworks',
  },
];

export function DifferentiatorsPage() {
  return (
    <div className="py-16">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="max-w-3xl">
          <Badge variant="outline" className="text-primary font-mono text-xs uppercase tracking-wider mb-4">
            Trust, Ethics & Innovation
          </Badge>
          <h1 className="text-4xl md:text-5xl font-black text-slate-900 tracking-tight">
            Technical Differentiators & Ethical AI Governance
          </h1>
          <p className="mt-5 text-lg text-slate-600 leading-relaxed">
            MASTERY is not another chatbot wrapped around an LLM. It is an ethically governed,
            evidence-backed academic intelligence platform engineered to eliminate structural failures
            in higher education without compromising student dignity, privacy, or faculty agency.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to="/app">
              <Button size="lg" className="font-semibold shadow-sm">
                Enter Workspace
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link to="/roles">
              <Button variant="outline" size="lg" className="font-semibold">
                Explore Role Ecosystem
              </Button>
            </Link>
          </div>
        </div>

        {/* 6 Key Differentiators Cards */}
        <div className="mt-16 space-y-6">
          <div className="border-b border-slate-200 pb-4">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500">Core Distinctions</span>
            <h2 className="text-2xl font-bold text-slate-900 mt-1">Six Core Technical Differentiators</h2>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {DIFFERENTIATORS.map((diff, i) => {
              const Icon = diff.icon;
              return (
                <Card key={i} className="border-slate-200 bg-white shadow-sm flex flex-col justify-between">
                  <CardContent className="p-6 md:p-8">
                    <div className="flex items-center gap-3 mb-4">
                      <div className={`p-2 rounded ${diff.accent}`}>
                        <Icon className="h-5 w-5" />
                      </div>
                      <h3 className="text-lg font-bold text-slate-900">{diff.title}</h3>
                    </div>

                    <div className="space-y-4 text-xs">
                      <div className="bg-red-50/70 border border-red-200 p-3.5 rounded text-slate-700">
                        <div className="flex items-center gap-1.5 font-bold text-red-800 uppercase tracking-wider font-mono mb-1">
                          <XCircle className="h-3.5 w-3.5" />
                          <span>Conventional University Practice:</span>
                        </div>
                        <p className="leading-relaxed">{diff.conventional}</p>
                      </div>

                      <div className="bg-emerald-50/70 border border-emerald-200 p-3.5 rounded text-slate-700">
                        <div className="flex items-center gap-1.5 font-bold text-emerald-800 uppercase tracking-wider font-mono mb-1">
                          <CheckCircle2 className="h-3.5 w-3.5" />
                          <span>The MASTERY Architectural Standard:</span>
                        </div>
                        <p className="leading-relaxed">{diff.mastery}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>

        {/* Head-to-Head Comparison Table */}
        <div className="mt-16 bg-white border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-6 md:p-8 border-b border-slate-200 bg-slate-50/70">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-primary">Head-to-Head</span>
            <h2 className="text-2xl font-bold text-slate-900 mt-1">
              Conventional Higher-Ed Systems vs. MASTERY
            </h2>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-100/70 text-slate-600 font-mono uppercase tracking-wider">
                  <th className="py-3.5 px-6 font-semibold w-1/4">Evaluation Dimension</th>
                  <th className="py-3.5 px-6 font-semibold w-3/8 text-red-900">Conventional Systems</th>
                  <th className="py-3.5 px-6 font-semibold w-3/8 text-primary">MASTERY Intelligence Platform</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {COMPARISON_ROWS.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/50 transition-colors">
                    <td className="py-4 px-6 font-bold text-slate-900 font-mono text-[11px]">
                      {row.feature}
                    </td>
                    <td className="py-4 px-6 text-slate-600 leading-relaxed">
                      {row.conventional}
                    </td>
                    <td className="py-4 px-6 text-slate-900 font-medium bg-primary/5 leading-relaxed">
                      {row.mastery}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Ethical Commitment Box */}
        <div className="mt-16 bg-slate-900 text-white p-8 md:p-12 border border-slate-800">
          <div className="max-w-3xl">
            <Badge variant="outline" className="text-primary-300 border-primary-500/40 font-mono text-xs mb-3">
              Institutional AI Charter
            </Badge>
            <h2 className="text-3xl font-black tracking-tight">Our Digital Trust Commitment</h2>
            <p className="mt-4 text-sm text-slate-300 leading-relaxed">
              In academic AI, trust is non-negotiable. Predictions must be auditable, interventions must be human-reviewed,
              and student privacy must be architecturally guaranteed. MASTERY proves that predictive intelligence
              can empower students without reducing them to algorithmic labels.
            </p>
            <div className="mt-6 flex flex-wrap gap-4">
              <Link to="/app">
                <Button className="bg-white text-slate-900 hover:bg-slate-100 font-semibold">
                  Test the Live Workspace
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link to="/problem">
                <Button variant="outline" className="border-slate-700 text-white hover:bg-slate-800 font-semibold">
                  Review The 4 Structural Problems
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
