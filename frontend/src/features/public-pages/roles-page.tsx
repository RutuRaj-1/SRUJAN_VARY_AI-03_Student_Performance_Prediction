import { Link } from 'react-router-dom';
import {
  ArrowRight,
  GraduationCap,
  BookOpen,
  Building2,
  Briefcase,
  Sliders,
  CheckCircle2,
  Lock,
  ExternalLink,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';

const ROLES = [
  {
    roleId: 'student',
    title: 'Student',
    subtitle: 'Self-Directed Mastery & Transparent Academic Growth',
    icon: GraduationCap,
    accent: 'bg-primary/10 text-primary border-primary/20',
    description:
      'Students gain a transparent, actionable view of their learning progress beyond blunt test percentages. They understand exactly which sub-topics require review, track Course Learning Outcome attainment, and receive faculty-approved remedial guidance.',
    keyCapabilities: [
      'Interactive Topic Mastery Trees with Bloom’s Taxonomy breakdown',
      'Clear visibility into prerequisite bottlenecks and foundational gaps',
      'Faculty-reviewed personalized remedial learning itineraries',
      'Objective career readiness scores mapped to industry target roles',
      'Zero punitive labeling — focus on growth and competency attainment',
    ],
    workspaceRoute: '/app/mastery',
    privacyNotes: 'Full visibility over own academic evidence, submissions, and interventions.',
  },
  {
    roleId: 'faculty',
    title: 'Faculty / Course Instructor',
    subtitle: 'Evidence-Based Instruction & Mentorship Governance',
    icon: BookOpen,
    accent: 'bg-secondary/10 text-secondary border-secondary/20',
    description:
      'Faculty leverage real-time diagnostic insights into student learning bottlenecks rather than waiting for end-of-semester exam post-mortems. They maintain full human authority over student interventions.',
    keyCapabilities: [
      'Cohort-level and student-level topic mastery diagnostic heatmaps',
      'Rubric-assisted assessment grading with automated justification drafts',
      'Automated Course Learning Outcome (CLO) attainment calculations for OBE',
      'Human-in-the-Loop review, modification, and approval of remedial plans',
      'Early academic risk detection with transparent SHAP factor explanations',
    ],
    workspaceRoute: '/app/assessments',
    privacyNotes: 'Access to enrolled student academic records and intervention review controls.',
  },
  {
    roleId: 'admin',
    title: 'Academic Administrator / HoD',
    subtitle: 'Institutional Governance, Accreditation & Retention Radar',
    icon: Building2,
    accent: 'bg-accent/10 text-accent border-accent/20',
    description:
      'Deans and Department Heads monitor program-level health, attrition risks, and curriculum prerequisite friction. Generates one-click compliance and attainment reports for NBA, NAAC, and ABET accreditation.',
    keyCapabilities: [
      'Department-wide academic risk radar and early attrition warnings',
      'Program-level Course Learning Outcome (CLO) and PO attainment audit reports',
      'Curriculum bottleneck analytics across multi-semester prerequisite DAGs',
      'Intervention efficacy tracking to verify remedial program ROI',
      'Faculty grading distribution and assessment consistency analytics',
    ],
    workspaceRoute: '/app/risk',
    privacyNotes: 'Department-wide read access with institutional oversight and reporting authority.',
  },
  {
    roleId: 'placement',
    title: 'Placement Officer',
    subtitle: 'Verified Competency Profiling & Industry Matching',
    icon: Briefcase,
    accent: 'bg-success/10 text-success border-success/20',
    description:
      'Placement teams connect graduating cohorts with employers based on verified, evidence-backed competencies rather than self-reported resumes or inflated GPAs.',
    keyCapabilities: [
      'Verified competency profiles benchmarked against O*NET & ESCO role standards',
      'Granular skill gap identification for targeted placement training bootcamps',
      'Student portfolio evidence verification (capstones, lab code artifacts)',
      'Cohort industry readiness distribution and hiring pipeline readiness',
      'Automated role matching based on empirical topic mastery evidence',
    ],
    workspaceRoute: '/app/career',
    privacyNotes: 'RESTRICTED: Privacy Firewall permanently prevents access to student risk flags, remedial interventions, or mental health data.',
  },
  {
    roleId: 'platform_admin',
    title: 'Platform Administrator',
    subtitle: 'System Health, Ingestion Pipelines & Security Auditing',
    icon: Sliders,
    accent: 'bg-slate-100 text-slate-800 border-slate-300',
    description:
      'Manages system-wide data pipelines, ERP/LMS webhook connectors, role access policies, and tamper-evident audit logs across the entire institution.',
    keyCapabilities: [
      'Real-time ingestion pipeline health and batch job monitoring',
      'Role-based access control (RBAC) and security firewall enforcement',
      'Immutable cryptographic audit event stream inspection',
      'Database performance, query latency, and cache hit metrics',
      'Institutional syllabus versioning and catalog administration',
    ],
    workspaceRoute: '/app/academic-data',
    privacyNotes: 'System-level infrastructure governance and security administration.',
  },
];

export function RolesPage() {
  return (
    <div className="py-16">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="max-w-3xl">
          <Badge variant="outline" className="text-primary font-mono text-xs uppercase tracking-wider mb-4">
            Stakeholder Ecosystem
          </Badge>
          <h1 className="text-4xl md:text-5xl font-black text-slate-900 tracking-tight">
            Tailored Experiences Across Five Academic Personas
          </h1>
          <p className="mt-5 text-lg text-slate-600 leading-relaxed">
            MASTERY unites students, educators, academic leadership, placement teams, and platform administrators
            in a single coherent workspace. Each role sees the exact intelligence required for their mission,
            governed by strict cryptographic privacy controls.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to="/app">
              <Button size="lg" className="font-semibold shadow-sm">
                Enter Workspace & Switch Personas
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

        {/* Roles Grid */}
        <div className="mt-16 space-y-8">
          {ROLES.map((role) => {
            const Icon = role.icon;
            const isPlacement = role.roleId === 'placement';

            return (
              <Card key={role.roleId} className="border-slate-200 bg-white shadow-sm overflow-hidden">
                <div className="border-b border-slate-100 bg-slate-50/70 p-6 flex flex-wrap items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div className={`p-2.5 rounded border ${role.accent}`}>
                      <Icon className="h-6 w-6" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono font-bold text-primary uppercase">ROLE PROFILE</span>
                        {isPlacement && (
                          <span className="inline-flex items-center gap-1 text-[10px] font-mono font-bold bg-amber-100 text-amber-800 px-2 py-0.5 rounded">
                            <Lock className="h-3 w-3" />
                            PRIVACY FIREWALLED
                          </span>
                        )}
                      </div>
                      <h2 className="text-2xl font-bold text-slate-900 mt-0.5">{role.title}</h2>
                    </div>
                  </div>

                  <Link to={role.workspaceRoute}>
                    <Button size="sm" className="font-semibold text-xs">
                      View {role.title} Workspace
                      <ExternalLink className="ml-1.5 h-3.5 w-3.5" />
                    </Button>
                  </Link>
                </div>

                <CardContent className="p-6 md:p-8">
                  <p className="text-sm font-semibold text-slate-800 mb-2">
                    {role.subtitle}
                  </p>
                  <p className="text-sm text-slate-600 leading-relaxed mb-6">
                    {role.description}
                  </p>

                  <div className="grid md:grid-cols-3 gap-6 pt-4 border-t border-slate-100">
                    <div className="md:col-span-2">
                      <div className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500 mb-3">
                        Key Responsibilities & Capabilities
                      </div>
                      <div className="grid sm:grid-cols-2 gap-2.5">
                        {role.keyCapabilities.map((cap, i) => (
                          <div key={i} className="flex items-start gap-2 text-xs text-slate-700">
                            <CheckCircle2 className="h-3.5 w-3.5 text-primary shrink-0 mt-0.5" />
                            <span>{cap}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <div className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500 mb-3">
                        Security & Data Boundary
                      </div>
                      <div
                        className={`p-3 rounded text-xs leading-relaxed ${
                          isPlacement
                            ? 'bg-amber-50 border border-amber-200 text-amber-900 font-medium'
                            : 'bg-slate-50 border border-slate-200 text-slate-600'
                        }`}
                      >
                        {role.privacyNotes}
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
          <h2 className="text-3xl font-black tracking-tight">Evaluate MASTERY from Any Perspective</h2>
          <p className="mt-3 text-sm text-slate-300 max-w-2xl mx-auto">
            Switch instantly between Student, Faculty, Admin, Placement, and Platform Admin personas in the live workspace.
          </p>
          <div className="mt-6 flex justify-center gap-3">
            <Link to="/app">
              <Button size="lg" className="bg-white text-slate-900 hover:bg-slate-100 font-semibold">
                Launch Workspace
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
