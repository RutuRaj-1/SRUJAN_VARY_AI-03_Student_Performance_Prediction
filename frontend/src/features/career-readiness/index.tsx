import React, { useState, useEffect } from 'react';
import {
  Briefcase,
  Target,
  Award,
  CheckCircle2,
  Clock,
  AlertTriangle,
  FileCode,
  ExternalLink,
  ShieldCheck,
  Layers,
  Sparkles,
  TrendingUp,
  FolderGit2,
  ArrowRight,
  RefreshCw,
} from 'lucide-react';
import {
  careerReadinessService,
  IndustryRoleProfile,
  CareerReadinessAnalysis,
  StudentCompetencyEvidence,
  StudentProjectEvidence,
  CareerDevelopmentRecommendation,
  CareerDashboardOverview,
  SubmitProjectPayload,
  RoleComparisonItem,
} from '@/services/career-readiness-service';

export const CareerReadinessPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'roles' | 'evidence' | 'gaps' | 'projects' | 'recommendations'>('roles');
  const [roles, setRoles] = useState<IndustryRoleProfile[]>([]);
  const [selectedRole, setSelectedRole] = useState<IndustryRoleProfile | null>(null);
  const [analysis, setAnalysis] = useState<CareerReadinessAnalysis | null>(null);
  const [evidenceList, setEvidenceList] = useState<StudentCompetencyEvidence[]>([]);
  const [projects, setProjects] = useState<StudentProjectEvidence[]>([]);
  const [recommendations, setRecommendations] = useState<CareerDevelopmentRecommendation[]>([]);
  const [overview, setOverview] = useState<CareerDashboardOverview | null>(null);
  const [comparisonRoles, setComparisonRoles] = useState<RoleComparisonItem[]>([]);
  const [evidenceFilter, setEvidenceFilter] = useState<string>('ALL');

  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [isSubmittingProject, setIsSubmittingProject] = useState<boolean>(false);
  const [showProjectModal, setShowProjectModal] = useState<boolean>(false);
  const [showCompareModal, setShowCompareModal] = useState<boolean>(false);

  // New Project Form State
  const [projectForm, setProjectForm] = useState<SubmitProjectPayload>({
    title: '',
    description: '',
    technology_stack: ['Python', 'FastAPI'],
    repository_url: '',
    portfolio_url: '',
    demonstrated_competencies: ['RESTful API Architecture'],
  });

  // Load initial data
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [rolesData, overviewData, evData, projData, recsData] = await Promise.all([
        careerReadinessService.getRoles(),
        careerReadinessService.getOverview().catch(() => null),
        careerReadinessService.getEvidence().catch(() => []),
        careerReadinessService.getProjects().catch(() => []),
        careerReadinessService.getRecommendations().catch(() => []),
      ]);

      setRoles(rolesData || []);
      setOverview(overviewData);
      setEvidenceList(evData || []);
      setProjects(projData || []);
      setRecommendations(recsData || []);

      if (rolesData && rolesData.length > 0) {
        setSelectedRole(rolesData[0]);
        // Trigger initial analysis for first role
        runAnalysis(rolesData[0].id);
      }
    } catch (err) {
      console.error('Failed to load career readiness data:', err);
    }
  };

  const runAnalysis = async (roleId: string, force = false) => {
    setIsAnalyzing(true);
    try {
      const result = await careerReadinessService.analyzeReadiness({
        role_id: roleId,
        force_recalculate: force,
      });
      setAnalysis(result);
    } catch (err) {
      console.error('Failed to analyze readiness:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSelectRole = (role: IndustryRoleProfile) => {
    setSelectedRole(role);
    runAnalysis(role.id);
  };

  const handleCompareAll = async () => {
    setShowCompareModal(true);
    try {
      const res = await careerReadinessService.compareRoles();
      setComparisonRoles(res.compared_roles || []);
    } catch (err) {
      console.error('Failed to compare roles:', err);
    }
  };

  const handleProjectSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmittingProject(true);
    try {
      await careerReadinessService.submitProject(projectForm);
      setShowProjectModal(false);
      // Refresh projects
      const updatedProjects = await careerReadinessService.getProjects();
      setProjects(updatedProjects);
      // Reset form
      setProjectForm({
        title: '',
        description: '',
        technology_stack: ['Python'],
        repository_url: '',
        portfolio_url: '',
        demonstrated_competencies: ['RESTful API Architecture'],
      });
    } catch (err) {
      console.error('Failed to submit project:', err);
    } finally {
      setIsSubmittingProject(false);
    }
  };

  const handleVerifyProject = async (projectId: string) => {
    try {
      await careerReadinessService.reviewProject(projectId, {
        verification_status: 'VERIFIED',
        verification_notes: 'Faculty verification: Verified repository commits and technical execution.',
      });
      // Refresh
      const [updatedProj, updatedEv] = await Promise.all([
        careerReadinessService.getProjects(),
        careerReadinessService.getEvidence(),
      ]);
      setProjects(updatedProj);
      setEvidenceList(updatedEv);
      if (selectedRole) runAnalysis(selectedRole.id, true);
    } catch (err) {
      console.error('Failed to verify project:', err);
    }
  };

  const getAlignmentBadge = (status?: string) => {
    switch (status) {
      case 'STRONG_EVIDENCE_ALIGNMENT':
        return <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200"><CheckCircle2 className="w-3.5 h-3.5" /> Strong Evidence Alignment</span>;
      case 'PARTIAL_EVIDENCE_ALIGNMENT':
        return <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200"><TrendingUp className="w-3.5 h-3.5" /> Partial Evidence Alignment</span>;
      case 'LIMITED_EVIDENCE_ALIGNMENT':
        return <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200"><Clock className="w-3.5 h-3.5" /> Limited Evidence Alignment</span>;
      default:
        return <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-slate-50 text-slate-700 border border-slate-200"><AlertTriangle className="w-3.5 h-3.5" /> Insufficient Evidence</span>;
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
      case 'HIGH':
        return <span className="px-2 py-0.5 rounded text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200">High Priority</span>;
      case 'MODERATE':
        return <span className="px-2 py-0.5 rounded text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200">Moderate</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-50 text-slate-600 border border-slate-200">Low / Informational</span>;
    }
  };

  const filteredEvidence = evidenceList.filter((e) => {
    if (evidenceFilter === 'ALL') return true;
    return e.evidence_state === evidenceFilter;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16">
      {/* 1. Header Banner */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-indigo-600 mb-1">
              <Sparkles className="w-4 h-4" />
              <span>Module 08: Career Readiness & Industry Competency Intelligence</span>
            </div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              Career Readiness & Skill Gap Intelligence
            </h1>
            <p className="text-sm text-slate-600 mt-1 max-w-3xl">
              Deterministic, role-specific alignment between verified academic learning outcomes, topic mastery, and verified practical project evidence.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleCompareAll}
              className="inline-flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-200 transition-colors"
            >
              <Layers className="w-4 h-4" />
              Compare Roles
            </button>
            <button
              onClick={() => setShowProjectModal(true)}
              className="inline-flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm transition-colors"
            >
              <FolderGit2 className="w-4 h-4" />
              Submit Practical Project
            </button>
          </div>
        </div>

        {/* Ethical Isolation & Firewall Notice */}
        <div className="mt-4 p-3 bg-slate-50 border border-slate-200 rounded-lg flex items-start gap-2.5 text-xs text-slate-700">
          <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold text-slate-900">Placement Officer Firewall & Non-Aggregation Policy: </span>
            Placement Officers may inspect authorized career competency evidence and verified projects for role-matching support.
            Under no circumstances are Phase 07 academic risk predictions, risk scores, or confidential intervention notes exposed.
            Career readiness is evaluated per role and is never collapsed into an arbitrary single employability percentage.
          </div>
        </div>
      </div>

      {/* 2. Key Metrics Bar */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="text-xs font-medium text-slate-500 uppercase tracking-wider">Permitted Roles</div>
          <div className="text-2xl font-bold text-slate-900 mt-1">{roles.length}</div>
          <div className="text-xs text-slate-500 mt-0.5">Curated Industry Benchmarks</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="text-xs font-medium text-slate-500 uppercase tracking-wider">Demonstrated Skills</div>
          <div className="text-2xl font-bold text-emerald-600 mt-1">{overview?.demonstrated_competencies_count ?? 0}</div>
          <div className="text-xs text-slate-500 mt-0.5">Verified Assessment / Project</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="text-xs font-medium text-slate-500 uppercase tracking-wider">Developing Skills</div>
          <div className="text-2xl font-bold text-blue-600 mt-1">{overview?.developing_competencies_count ?? 0}</div>
          <div className="text-xs text-slate-500 mt-0.5">In-Progress Mastery</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="text-xs font-medium text-slate-500 uppercase tracking-wider">Practical Projects</div>
          <div className="text-2xl font-bold text-indigo-600 mt-1">{overview?.verified_projects_count ?? 0}</div>
          <div className="text-xs text-slate-500 mt-0.5">{overview?.pending_projects_count ?? 0} Awaiting Faculty Review</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="text-xs font-medium text-slate-500 uppercase tracking-wider">Active Skill Gaps</div>
          <div className="text-2xl font-bold text-amber-600 mt-1">{overview?.active_gaps_count ?? (analysis?.gap_findings?.length ?? 0)}</div>
          <div className="text-xs text-slate-500 mt-0.5">Actionable Target Areas</div>
        </div>
      </div>

      {/* 3. Navigation Tabs */}
      <div className="flex border-b border-slate-200 space-x-6 text-sm font-medium">
        <button
          onClick={() => setActiveTab('roles')}
          className={`pb-3 border-b-2 flex items-center gap-2 transition-colors ${
            activeTab === 'roles'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Briefcase className="w-4 h-4" />
          Role Explorer & Analysis
        </button>
        <button
          onClick={() => setActiveTab('evidence')}
          className={`pb-3 border-b-2 flex items-center gap-2 transition-colors ${
            activeTab === 'evidence'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Award className="w-4 h-4" />
          Competency Evidence Matrix ({evidenceList.length})
        </button>
        <button
          onClick={() => setActiveTab('gaps')}
          className={`pb-3 border-b-2 flex items-center gap-2 transition-colors ${
            activeTab === 'gaps'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <AlertTriangle className="w-4 h-4" />
          Skill Gap Discoveries ({analysis?.gap_findings?.length || 0})
        </button>
        <button
          onClick={() => setActiveTab('projects')}
          className={`pb-3 border-b-2 flex items-center gap-2 transition-colors ${
            activeTab === 'projects'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <FolderGit2 className="w-4 h-4" />
          Practical Projects ({projects.length})
        </button>
        <button
          onClick={() => setActiveTab('recommendations')}
          className={`pb-3 border-b-2 flex items-center gap-2 transition-colors ${
            activeTab === 'recommendations'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Target className="w-4 h-4" />
          Development Recommendations ({recommendations.length})
        </button>
      </div>

      {/* 4. Tab 1: Role Explorer & Readiness Analysis */}
      {activeTab === 'roles' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Roles Selector Column */}
          <div className="space-y-3">
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Select Career Target</h3>
            {roles.map((role) => (
              <div
                key={role.id}
                onClick={() => handleSelectRole(role)}
                className={`p-4 rounded-xl border cursor-pointer transition-all ${
                  selectedRole?.id === role.id
                    ? 'border-indigo-600 bg-indigo-50/50 shadow-sm'
                    : 'border-slate-200 bg-white hover:border-slate-300'
                }`}
              >
                <div className="flex items-start justify-between">
                  <h4 className="font-semibold text-slate-900 text-sm">{role.role_title}</h4>
                  <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                    {role.experience_tier}
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-1 line-clamp-2">{role.description}</p>
                <div className="mt-3 flex items-center justify-between text-xs text-slate-400">
                  <span>{role.requirements?.length || 0} Benchmarked Competencies</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </div>
              </div>
            ))}
          </div>

          {/* Analysis View Column */}
          <div className="lg:col-span-2 space-y-6">
            {selectedRole && (
              <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-6">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-100 pb-4">
                  <div>
                    <h2 className="text-lg font-bold text-slate-900">{selectedRole.role_title}</h2>
                    <div className="flex items-center gap-2 text-xs text-slate-500 mt-0.5">
                      <span>{selectedRole.role_family}</span>
                      <span>•</span>
                      <span>Version {selectedRole.version}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getAlignmentBadge(analysis?.alignment_status)}
                    <button
                      onClick={() => selectedRole && runAnalysis(selectedRole.id, true)}
                      disabled={isAnalyzing}
                      className="p-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 transition-colors"
                      title="Recalculate analysis"
                    >
                      <RefreshCw className={`w-4 h-4 ${isAnalyzing ? 'animate-spin' : ''}`} />
                    </button>
                  </div>
                </div>

                {/* Readiness Coverage Gauges */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                    <div className="flex justify-between items-center text-xs font-semibold text-slate-700 mb-1">
                      <span>Core Competency Coverage</span>
                      <span className="text-indigo-600 font-bold">{analysis?.core_competency_coverage || 0}%</span>
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-2">
                      <div
                        className="bg-indigo-600 h-2 rounded-full transition-all"
                        style={{ width: `${analysis?.core_competency_coverage || 0}%` }}
                      />
                    </div>
                    <div className="text-[11px] text-slate-500 mt-2">
                      {analysis?.demonstrated_count || 0} demonstrated / {analysis?.developing_count || 0} developing out of {analysis?.total_requirements_count || 0} requirements.
                    </div>
                  </div>

                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                    <div className="flex justify-between items-center text-xs font-semibold text-slate-700 mb-1">
                      <span>Practical Project Coverage</span>
                      <span className="text-emerald-600 font-bold">{analysis?.practical_evidence_coverage || 0}%</span>
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-2">
                      <div
                        className="bg-emerald-600 h-2 rounded-full transition-all"
                        style={{ width: `${analysis?.practical_evidence_coverage || 0}%` }}
                      />
                    </div>
                    <div className="text-[11px] text-slate-500 mt-2">
                      Verified GitHub repositories, capstone projects, and coding benchmarks.
                    </div>
                  </div>
                </div>

                {/* Analysis Rationale */}
                <div className="p-4 rounded-lg bg-indigo-50/50 border border-indigo-100 text-xs text-indigo-900 leading-relaxed">
                  <div className="font-semibold text-indigo-950 mb-1 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5" />
                    Evidence-Backed Interpretation
                  </div>
                  {analysis?.summary_rationale || 'Analysis evaluates available evidence against benchmark requirements.'}
                </div>

                {/* Role Competency Requirements List */}
                <div className="space-y-3">
                  <h3 className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
                    Role Competency Requirements ({selectedRole.requirements?.length || 0})
                  </h3>
                  <div className="divide-y divide-slate-100 border border-slate-200 rounded-lg overflow-hidden">
                    {selectedRole.requirements?.map((req) => (
                      <div key={req.id} className="p-3.5 bg-white hover:bg-slate-50/50 flex items-center justify-between gap-4">
                        <div className="space-y-0.5">
                          <div className="text-xs font-semibold text-slate-900 flex items-center gap-2">
                            <span>{req.competency_name}</span>
                            <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded ${
                              req.importance === 'CORE' || req.importance === 'HIGH'
                                ? 'bg-rose-50 text-rose-700'
                                : 'bg-slate-100 text-slate-600'
                            }`}>
                              {req.importance}
                            </span>
                          </div>
                          <div className="text-[11px] text-slate-500">
                            Category: {req.category} • Required Depth: Level {req.required_depth}/5
                          </div>
                        </div>
                        <div>
                          {req.mapping_status === 'APPROVED' ? (
                            <span className="text-[10px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                              Verified Mapping
                            </span>
                          ) : (
                            <span className="text-[10px] font-semibold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                              Mapping Review Required
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 5. Tab 2: Competency Evidence Matrix */}
      {activeTab === 'evidence' && (
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">Student Competency Evidence Ledger</h3>
              <p className="text-xs text-slate-500 mt-0.5">Traceable evidence collected across topic mastery, verified exams, and practical projects.</p>
            </div>
            {/* Filter buttons */}
            <div className="flex flex-wrap gap-1.5 text-xs">
              {['ALL', 'DEMONSTRATED', 'DEVELOPING', 'REVIEW_REQUIRED', 'INSUFFICIENT_EVIDENCE'].map((f) => (
                <button
                  key={f}
                  onClick={() => setEvidenceFilter(f)}
                  className={`px-3 py-1 rounded-lg border font-medium transition-colors ${
                    evidenceFilter === f
                      ? 'bg-indigo-600 text-white border-indigo-600'
                      : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  {f.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>

          <div className="border border-slate-200 rounded-lg overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-700 uppercase tracking-wider text-[11px] font-semibold">
                <tr>
                  <th className="px-4 py-3">Competency</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3">Evidence State</th>
                  <th className="px-4 py-3">Source Type</th>
                  <th className="px-4 py-3">Score / Depth</th>
                  <th className="px-4 py-3">Summary & Provenance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredEvidence.map((ev) => (
                  <tr key={ev.id} className="hover:bg-slate-50/50">
                    <td className="px-4 py-3 font-semibold text-slate-900">{ev.competency_name}</td>
                    <td className="px-4 py-3 text-slate-500">{ev.category}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        ev.evidence_state === 'DEMONSTRATED'
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : ev.evidence_state === 'DEVELOPING'
                          ? 'bg-blue-50 text-blue-700 border border-blue-200'
                          : ev.evidence_state === 'REVIEW_REQUIRED'
                          ? 'bg-amber-50 text-amber-700 border border-amber-200'
                          : 'bg-slate-100 text-slate-600'
                      }`}>
                        {ev.evidence_state}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-500">{ev.evidence_type.replace('_', ' ')}</td>
                    <td className="px-4 py-3 font-semibold text-slate-800">
                      {ev.score_or_metric ? `${ev.score_or_metric.toFixed(1)}%` : 'Evaluated'}
                    </td>
                    <td className="px-4 py-3 text-slate-600 max-w-xs truncate">{ev.evidence_summary}</td>
                  </tr>
                ))}
                {filteredEvidence.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-slate-400">
                      No competency evidence matching selected filter.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 6. Tab 3: Skill Gap Discoveries */}
      {activeTab === 'gaps' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-900">
              Categorized Skill Gaps for {selectedRole?.role_title || 'Selected Role'}
            </h3>
            <span className="text-xs text-slate-500">
              {analysis?.gap_findings?.length || 0} Gaps Discovered
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {analysis?.gap_findings?.map((gap) => (
              <div key={gap.id} className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200 uppercase">
                      {gap.gap_type.replace('_', ' ')}
                    </span>
                    <h4 className="text-sm font-bold text-slate-900 mt-1">{gap.competency_name}</h4>
                  </div>
                  {getSeverityBadge(gap.gap_severity)}
                </div>

                <p className="text-xs text-slate-600 leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-100">
                  <span className="font-semibold text-slate-900">Rationale: </span>
                  {gap.rationale}
                </p>

                <div className="space-y-1 text-xs">
                  <div className="text-indigo-900 font-medium">
                    <span className="font-semibold">Suggested Next Action: </span>
                    {gap.suggested_action}
                  </div>
                  <div className="text-slate-500">
                    <span className="font-semibold text-slate-700">Evidence Needed: </span>
                    {gap.evidence_needed}
                  </div>
                </div>
              </div>
            ))}
            {(!analysis?.gap_findings || analysis.gap_findings.length === 0) && (
              <div className="col-span-2 p-12 text-center bg-white border border-slate-200 rounded-xl text-slate-500">
                <CheckCircle2 className="w-10 h-10 text-emerald-600 mx-auto mb-2" />
                <h4 className="font-bold text-slate-900">Zero Critical Skill Gaps Discovered!</h4>
                <p className="text-xs text-slate-500 mt-1">Demonstrated competency coverage sufficiently matches current role benchmark.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 7. Tab 4: Practical Projects */}
      {activeTab === 'projects' && (
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-slate-900">Student Practical Projects & Portfolios</h3>
              <p className="text-xs text-slate-500 mt-0.5">Verified engineering artifacts that establish authentic practical and coding competencies.</p>
            </div>
            <button
              onClick={() => setShowProjectModal(true)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 transition-colors"
            >
              <FolderGit2 className="w-3.5 h-3.5" />
              Add Project
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {projects.map((proj) => (
              <div key={proj.id} className="border border-slate-200 rounded-xl p-5 space-y-3 bg-white hover:border-slate-300 transition-all">
                <div className="flex items-start justify-between">
                  <h4 className="text-sm font-bold text-slate-900">{proj.title}</h4>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    proj.verification_status === 'VERIFIED'
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      : proj.verification_status === 'REJECTED'
                      ? 'bg-rose-50 text-rose-700 border border-rose-200'
                      : 'bg-amber-50 text-amber-700 border border-amber-200'
                  }`}>
                    {proj.verification_status.replace('_', ' ')}
                  </span>
                </div>

                <p className="text-xs text-slate-600 line-clamp-3">{proj.description}</p>

                {/* Tech stack */}
                <div className="flex flex-wrap gap-1">
                  {proj.technology_stack?.map((tech, idx) => (
                    <span key={idx} className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[10px] font-medium">
                      {tech}
                    </span>
                  ))}
                </div>

                {/* Links */}
                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
                  {proj.repository_url ? (
                    <a
                      href={proj.repository_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-indigo-600 hover:underline font-medium"
                    >
                      <FileCode className="w-3.5 h-3.5" /> Repository <ExternalLink className="w-3 h-3" />
                    </a>
                  ) : <span className="text-slate-400">No Repo Link</span>}

                  {proj.verification_status === 'PENDING_REVIEW' && (
                    <button
                      onClick={() => handleVerifyProject(proj.id)}
                      className="text-[11px] font-semibold text-emerald-700 hover:text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded border border-emerald-200"
                    >
                      Verify as Faculty
                    </button>
                  )}
                </div>

                {proj.verification_notes && (
                  <div className="text-[11px] text-slate-500 bg-slate-50 p-2 rounded border border-slate-100">
                    <span className="font-semibold text-slate-700">Review Notes: </span>
                    {proj.verification_notes}
                  </div>
                )}
              </div>
            ))}
            {projects.length === 0 && (
              <div className="col-span-2 p-8 text-center text-slate-400">
                No practical projects submitted yet. Submit a GitHub or portfolio project to earn practical competency credit!
              </div>
            )}
          </div>
        </div>
      )}

      {/* 8. Tab 5: Development Recommendations */}
      {activeTab === 'recommendations' && (
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-900">Personalized Career Development Roadmaps</h3>
            <span className="text-xs text-slate-500">{recommendations.length} Actionable Items</span>
          </div>

          <div className="space-y-3">
            {recommendations.map((rec) => (
              <div key={rec.id} className="p-4 rounded-xl border border-slate-200 hover:border-slate-300 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200 uppercase">
                      {rec.recommendation_type.replace('_', ' ')}
                    </span>
                    <h4 className="font-bold text-slate-900 text-sm">{rec.title}</h4>
                    {getSeverityBadge(rec.priority)}
                  </div>
                  <p className="text-xs text-slate-600">{rec.action_plan}</p>
                  <div className="text-[11px] text-slate-500 flex items-center gap-3 mt-1">
                    <span><span className="font-semibold text-slate-700">Target:</span> {rec.target_competency}</span>
                    <span>•</span>
                    <span><span className="font-semibold text-slate-700">Expected Evidence:</span> {rec.expected_evidence}</span>
                    <span>•</span>
                    <span><span className="font-semibold text-slate-700">Duration:</span> ~{rec.estimated_duration_days} days</span>
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <span className="text-xs font-semibold px-2.5 py-1 rounded bg-slate-100 text-slate-700">
                    {rec.status}
                  </span>
                </div>
              </div>
            ))}
            {recommendations.length === 0 && (
              <div className="p-8 text-center text-slate-400">
                No active development recommendations at this time.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Project Submission Modal */}
      {showProjectModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-lg w-full p-6 space-y-4 border border-slate-200">
            <h3 className="text-lg font-bold text-slate-900">Submit Practical Project Evidence</h3>
            <p className="text-xs text-slate-500">Provide verifiable repository and documentation links to claim practical competency credit.</p>

            <form onSubmit={handleProjectSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Project Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Distributed Key-Value Store"
                  value={projectForm.title}
                  onChange={(e) => setProjectForm({ ...projectForm, title: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-1 focus:ring-indigo-600 outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Description</label>
                <textarea
                  required
                  rows={3}
                  placeholder="Describe architecture, engineering challenges solved, and testing performed..."
                  value={projectForm.description}
                  onChange={(e) => setProjectForm({ ...projectForm, description: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-1 focus:ring-indigo-600 outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">GitHub / Code Repository URL</label>
                <input
                  type="url"
                  placeholder="https://github.com/username/project-repo"
                  value={projectForm.repository_url || ''}
                  onChange={(e) => setProjectForm({ ...projectForm, repository_url: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-1 focus:ring-indigo-600 outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Demonstrated Competency</label>
                <input
                  type="text"
                  placeholder="e.g. RESTful API Architecture, Database Design"
                  value={projectForm.demonstrated_competencies.join(', ')}
                  onChange={(e) => setProjectForm({
                    ...projectForm,
                    demonstrated_competencies: e.target.value.split(',').map((s) => s.trim()).filter(Boolean),
                  })}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-1 focus:ring-indigo-600 outline-none"
                />
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t">
                <button
                  type="button"
                  onClick={() => setShowProjectModal(false)}
                  className="px-3.5 py-2 text-slate-600 hover:bg-slate-100 rounded-lg font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmittingProject}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition-colors"
                >
                  {isSubmittingProject ? 'Submitting...' : 'Submit for Verification'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Role Comparison Modal */}
      {showCompareModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-4xl w-full p-6 space-y-4 border border-slate-200">
            <div className="flex justify-between items-center border-b pb-3">
              <div>
                <h3 className="text-lg font-bold text-slate-900">Career Role Benchmark Comparison</h3>
                <p className="text-xs text-slate-500">Compare your demonstrated evidence standing across multiple professional roles.</p>
              </div>
              <button
                onClick={() => setShowCompareModal(false)}
                className="text-slate-400 hover:text-slate-600 font-bold text-base"
              >
                ✕
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-600">
                <thead className="bg-slate-50 border-b text-[11px] font-semibold text-slate-700 uppercase">
                  <tr>
                    <th className="px-4 py-3">Role Title</th>
                    <th className="px-4 py-3">Alignment Status</th>
                    <th className="px-4 py-3">Core Coverage</th>
                    <th className="px-4 py-3">Practical Coverage</th>
                    <th className="px-4 py-3">Demonstrated</th>
                    <th className="px-4 py-3">Active Gaps</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {comparisonRoles.map((cr) => (
                    <tr key={cr.role_id} className="hover:bg-slate-50/50">
                      <td className="px-4 py-3 font-semibold text-slate-900">{cr.role_title}</td>
                      <td className="px-4 py-3">{getAlignmentBadge(cr.alignment_status)}</td>
                      <td className="px-4 py-3 font-bold text-indigo-600">{cr.core_coverage_pct.toFixed(1)}%</td>
                      <td className="px-4 py-3 font-bold text-emerald-600">{cr.practical_coverage_pct.toFixed(1)}%</td>
                      <td className="px-4 py-3 text-slate-800">{cr.demonstrated_count} / {cr.total_requirements}</td>
                      <td className="px-4 py-3 font-semibold text-amber-600">{cr.gap_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg text-slate-500 text-[11px]">
              Note: Career comparison metrics reflect observed alignment and do not force or restrict students to any singular track.
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
