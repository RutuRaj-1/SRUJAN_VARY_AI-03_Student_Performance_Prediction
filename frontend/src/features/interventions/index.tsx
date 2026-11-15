import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Sparkles,
  CheckCircle,
  FileText,
  Plus,
  RotateCcw,
  Lock,
  ShieldAlert,
  Info,
  ExternalLink,
} from 'lucide-react';
import {
  interventionService,
  AcademicInterventionPlan,
  InterventionRecommendation,
  InterventionPlanStatus,
} from '@/services/intervention-service';
import { syllabusService, AcademicSubject } from '@/services/syllabus-service';
import { academicDataService, StudentAcademicProfile } from '@/services/academic-data-service';
import { useAuth } from '@/context/auth-context';

export const InterventionPage: React.FC = () => {
  const { profile } = useAuth();
  const queryClient = useQueryClient();

  const isStudent = profile?.role === 'STUDENT';
  const isPlacementOfficer = profile?.role === 'PLACEMENT_OFFICER';
  const isFacultyOrAdmin =
    profile?.role === 'FACULTY' ||
    profile?.role === 'INSTITUTION_ADMIN' ||
    profile?.role === 'SUPER_ADMIN';

  // Navigation tab state
  const [activeTab, setActiveTab] = useState<'dashboard' | 'recommendations' | 'plans' | 'student_workspace'>(
    isStudent ? 'student_workspace' : 'dashboard'
  );

  // Filters
  const [selectedSubjectId, setSelectedSubjectId] = useState<string>('');
  const [selectedStudentId, setSelectedStudentId] = useState<string>('');
  const [selectedPlanId, setSelectedPlanId] = useState<string>('');

  // Modals state
  const [isCreatePlanOpen, setIsCreatePlanOpen] = useState(false);
  const [newPlanTitle, setNewPlanTitle] = useState('');
  const [newPlanObjective, setNewPlanObjective] = useState('');
  const [selectedRecForPlan, setSelectedRecForPlan] = useState<InterventionRecommendation | null>(null);

  const [isReviewModalOpen, setIsReviewModalOpen] = useState(false);
  const [reviewDecision, setReviewDecision] = useState<'APPROVE' | 'REJECT'>('APPROVE');
  const [reviewNotes, setReviewNotes] = useState('');

  const [isSubmitActionOpen, setIsSubmitActionOpen] = useState(false);
  const [submittingActionId, setSubmittingActionId] = useState<string>('');
  const [studentSubmissionNotes, setStudentSubmissionNotes] = useState('');
  const [studentSubmissionUrl, setStudentSubmissionUrl] = useState('');

  // ---------------------------------------------------------------------------
  // Queries
  // ---------------------------------------------------------------------------
  const { data: subjects = [] } = useQuery<AcademicSubject[]>({
    queryKey: ['syllabus-subjects'],
    queryFn: () => syllabusService.getSubjects(),
  });

  const { data: students = [] } = useQuery<StudentAcademicProfile[]>({
    queryKey: ['academic-students'],
    queryFn: () => academicDataService.getStudents(),
    enabled: isFacultyOrAdmin,
  });

  useEffect(() => {
    if (subjects.length > 0 && !selectedSubjectId) {
      setSelectedSubjectId(subjects[0].id);
    }
  }, [subjects, selectedSubjectId]);

  useEffect(() => {
    if (isFacultyOrAdmin && students.length > 0 && !selectedStudentId) {
      setSelectedStudentId(students[0].id);
    }
  }, [students, isFacultyOrAdmin, selectedStudentId]);

  // Faculty Dashboard Query
  const { data: facultyDashboard } = useQuery({
    queryKey: ['interventions-faculty-dashboard', selectedSubjectId],
    queryFn: () => interventionService.getFacultyDashboard(selectedSubjectId || undefined),
    enabled: isFacultyOrAdmin,
  });

  // Recommendations Query
  const { data: recommendations = [], isLoading: isLoadingRecs } = useQuery<InterventionRecommendation[]>({
    queryKey: ['interventions-recommendations', selectedSubjectId, selectedStudentId],
    queryFn: () => interventionService.getRecommendations(selectedStudentId || undefined, selectedSubjectId || undefined),
    enabled: isFacultyOrAdmin,
  });

  // Plans Query
  const { data: plans = [], isLoading: isLoadingPlans } = useQuery<AcademicInterventionPlan[]>({
    queryKey: ['interventions-plans', selectedSubjectId, selectedStudentId],
    queryFn: () => interventionService.getPlans(selectedStudentId || undefined, selectedSubjectId || undefined),
    enabled: isFacultyOrAdmin,
  });

  // Student Workspace Query
  const { data: studentWorkspace, isLoading: isLoadingStudent } = useQuery({
    queryKey: ['interventions-student-workspace'],
    queryFn: () => interventionService.getStudentWorkspace(),
    enabled: isStudent,
  });

  // Selected Plan Query
  const { data: activePlanDetail } = useQuery<AcademicInterventionPlan>({
    queryKey: ['intervention-plan-detail', selectedPlanId],
    queryFn: () => interventionService.getPlan(selectedPlanId),
    enabled: !!selectedPlanId,
  });

  // ---------------------------------------------------------------------------
  // Mutations
  // ---------------------------------------------------------------------------
  const generateRecsMutation = useMutation({
    mutationFn: () =>
      interventionService.generateRecommendations(selectedStudentId, selectedSubjectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['interventions-recommendations'] });
      queryClient.invalidateQueries({ queryKey: ['interventions-faculty-dashboard'] });
    },
  });

  const createPlanMutation = useMutation({
    mutationFn: (payload: any) => interventionService.createPlan(payload),
    onSuccess: () => {
      setIsCreatePlanOpen(false);
      setSelectedRecForPlan(null);
      setNewPlanTitle('');
      setNewPlanObjective('');
      queryClient.invalidateQueries({ queryKey: ['interventions-plans'] });
      queryClient.invalidateQueries({ queryKey: ['interventions-faculty-dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['interventions-recommendations'] });
      setActiveTab('plans');
    },
  });

  const reviewPlanMutation = useMutation({
    mutationFn: () =>
      interventionService.reviewPlan(selectedPlanId, {
        decision: reviewDecision,
        review_notes: reviewNotes,
      }),
    onSuccess: () => {
      setIsReviewModalOpen(false);
      setReviewNotes('');
      queryClient.invalidateQueries({ queryKey: ['interventions-plans'] });
      queryClient.invalidateQueries({ queryKey: ['intervention-plan-detail'] });
      queryClient.invalidateQueries({ queryKey: ['interventions-faculty-dashboard'] });
    },
  });

  const assignPlanMutation = useMutation({
    mutationFn: (planId: string) => interventionService.assignPlan(planId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['interventions-plans'] });
      queryClient.invalidateQueries({ queryKey: ['intervention-plan-detail'] });
      queryClient.invalidateQueries({ queryKey: ['interventions-faculty-dashboard'] });
    },
  });

  const updateActionStatusMutation = useMutation({
    mutationFn: ({ actionId, payload }: { actionId: string; payload: any }) =>
      interventionService.updateActionStatus(actionId, payload),
    onSuccess: () => {
      setIsSubmitActionOpen(false);
      setStudentSubmissionNotes('');
      setStudentSubmissionUrl('');
      queryClient.invalidateQueries({ queryKey: ['interventions-plans'] });
      queryClient.invalidateQueries({ queryKey: ['intervention-plan-detail'] });
      queryClient.invalidateQueries({ queryKey: ['interventions-student-workspace'] });
    },
  });

  // ---------------------------------------------------------------------------
  // Placement Officer Boundary View
  // ---------------------------------------------------------------------------
  if (isPlacementOfficer) {
    return (
      <div className="p-8 max-w-4xl mx-auto">
        <div className="rounded-xl border border-red-500/20 bg-red-950/20 p-8 text-center backdrop-blur-sm">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-red-500/10 text-red-400 mb-4">
            <Lock className="h-7 w-7" />
          </div>
          <h2 className="text-xl font-semibold text-red-200">Ethical Governance Barrier: Placement Officer Quarantined</h2>
          <p className="mt-3 text-sm text-red-300/80 leading-relaxed max-w-xl mx-auto">
            Academic intervention records are reserved strictly for supportive faculty advising and student-centered recovery.
            To eliminate employment stigmatization, Placement Officers have no clearance to view remedial support plans.
          </p>
          <div className="mt-6 inline-flex items-center gap-2 text-xs text-red-400 bg-red-950/50 px-4 py-2 rounded-lg border border-red-900/50">
            <ShieldAlert className="h-4 w-4" />
            MASTERY Ethical AI Charter § 4.2
          </div>
        </div>
      </div>
    );
  }

  // ---------------------------------------------------------------------------
  // Status Badge Helper
  // ---------------------------------------------------------------------------
  const getStatusBadge = (statusVal: InterventionPlanStatus | string) => {
    switch (statusVal) {
      case 'APPROVED':
      case 'VERIFIED':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'ACTIVE':
      case 'IN_PROGRESS':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
      case 'PENDING_REVIEW':
      case 'SUBMITTED':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'COMPLETED':
        return 'bg-purple-500/10 text-purple-400 border-purple-500/30';
      case 'REJECTED':
      case 'DECLINED':
        return 'bg-red-500/10 text-red-400 border-red-500/30';
      case 'DRAFT':
      default:
        return 'bg-secondary text-muted-foreground border-border/40';
    }
  };

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      {/* --------------------------------------------------------------------- */}
      {/* Page Header */}
      {/* --------------------------------------------------------------------- */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border/40 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-primary/10 border border-primary/20 text-primary">
              <Sparkles className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2 font-sans">
                Personalized Academic Intervention
                <span className="text-xs font-medium px-2 py-0.5 rounded-[3px] bg-[#EEF8F7] text-[#123E40] border border-[#BDCEC8] font-mono">
                  Module 06
                </span>
              </h1>
              <p className="text-sm text-muted-foreground mt-0.5">
                Faculty-reviewed, evidence-grounded academic recovery plans and student growth tracking.
              </p>
            </div>
          </div>
        </div>

        {/* Global Controls */}
        {isFacultyOrAdmin && (
          <div className="flex flex-wrap items-center gap-3">
            <select
              value={selectedSubjectId}
              onChange={(e) => setSelectedSubjectId(e.target.value)}
              className="h-9 px-3 rounded-md bg-secondary/50 border border-border text-sm focus:outline-none"
            >
              {subjects.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.code} - {s.name}
                </option>
              ))}
            </select>

            <select
              value={selectedStudentId}
              onChange={(e) => setSelectedStudentId(e.target.value)}
              className="h-9 px-3 rounded-md bg-secondary/50 border border-border text-sm focus:outline-none"
            >
              {students.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.first_name} {s.last_name} ({s.enrollment_number})
                </option>
              ))}
            </select>

            <button
              onClick={() => generateRecsMutation.mutate()}
              disabled={generateRecsMutation.isPending || !selectedStudentId}
              className="inline-flex items-center gap-2 h-9 px-4 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
            >
              <Sparkles className="h-4 w-4" />
              {generateRecsMutation.isPending ? 'Generating...' : 'Analyze & Recommend'}
            </button>
          </div>
        )}
      </div>

      {/* --------------------------------------------------------------------- */}
      {/* Mandatory Scientific Disclaimer Banner */}
      {/* --------------------------------------------------------------------- */}
      <div className="rounded-lg border border-primary/20 bg-primary/5 p-4 flex items-start gap-3">
        <Info className="h-5 w-5 text-primary mt-0.5 shrink-0" />
        <div className="text-xs text-foreground/80 leading-relaxed">
          <span className="font-semibold text-primary">Human-in-the-Loop Governance Notice: </span>
          Interventions are supportive pedagogical recommendations designed to accelerate student conceptual understanding.
          They do <strong>NOT</strong> constitute disciplinary actions or cognitive diagnoses. All support plans require authorized
          faculty review prior to student assignment.
        </div>
      </div>

      {/* --------------------------------------------------------------------- */}
      {/* Faculty Metric Strip */}
      {/* --------------------------------------------------------------------- */}
      {isFacultyOrAdmin && facultyDashboard && (
        <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
          <div className="p-4 rounded-lg bg-card/50 border border-border/40">
            <span className="text-xs text-muted-foreground">Total Plans</span>
            <div className="text-2xl font-bold mt-1 text-foreground">{facultyDashboard.total_plans}</div>
          </div>
          <div className="p-4 rounded-lg bg-amber-500/5 border border-amber-500/20">
            <span className="text-xs text-amber-400 font-medium">Pending Review</span>
            <div className="text-2xl font-bold mt-1 text-amber-400">{facultyDashboard.draft_review_count}</div>
          </div>
          <div className="p-4 rounded-lg bg-blue-500/5 border border-blue-500/20">
            <span className="text-xs text-blue-400 font-medium">Active Plans</span>
            <div className="text-2xl font-bold mt-1 text-blue-400">{facultyDashboard.active_plans_count}</div>
          </div>
          <div className="p-4 rounded-lg bg-purple-500/5 border border-purple-500/20">
            <span className="text-xs text-purple-400 font-medium">Completed</span>
            <div className="text-2xl font-bold mt-1 text-purple-400">{facultyDashboard.completed_plans_count}</div>
          </div>
          <div className="p-4 rounded-lg bg-red-500/5 border border-red-500/20">
            <span className="text-xs text-red-400 font-medium">Overdue Actions</span>
            <div className="text-2xl font-bold mt-1 text-red-400">{facultyDashboard.overdue_actions_count}</div>
          </div>
          <div className="p-4 rounded-lg bg-slate-500/5 border border-slate-500/20">
            <span className="text-xs text-slate-400 font-medium">Evidence Gaps</span>
            <div className="text-2xl font-bold mt-1 text-slate-400">
              {facultyDashboard.insufficient_evidence_recommendations_count}
            </div>
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* Navigation Tabs */}
      {/* --------------------------------------------------------------------- */}
      <div className="flex items-center gap-2 border-b border-border/40 pb-2">
        {isFacultyOrAdmin && (
          <>
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'dashboard'
                  ? 'bg-secondary text-foreground'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Faculty Overview
            </button>
            <button
              onClick={() => setActiveTab('recommendations')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'recommendations'
                  ? 'bg-secondary text-foreground'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Recommendations Queue ({recommendations.length})
            </button>
            <button
              onClick={() => setActiveTab('plans')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'plans'
                  ? 'bg-secondary text-foreground'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Intervention Plans ({plans.length})
            </button>
          </>
        )}
        {isStudent && (
          <button
            onClick={() => setActiveTab('student_workspace')}
            className="px-4 py-2 rounded-md text-sm font-medium bg-secondary text-foreground"
          >
            My Academic Support Plans
          </button>
        )}
      </div>

      {/* --------------------------------------------------------------------- */}
      {/* TAB 1: FACULTY OVERVIEW */}
      {/* --------------------------------------------------------------------- */}
      {isFacultyOrAdmin && activeTab === 'dashboard' && facultyDashboard && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Recent Plans */}
            <div className="rounded-xl border border-border/50 bg-card/40 p-6 space-y-4">
              <h3 className="text-base font-semibold text-foreground flex items-center gap-2">
                <FileText className="h-4 w-4 text-primary" />
                Recent Intervention Plans
              </h3>
              {facultyDashboard.recent_plans.length === 0 ? (
                <p className="text-xs text-muted-foreground py-6 text-center">No plans created yet.</p>
              ) : (
                <div className="space-y-3">
                  {facultyDashboard.recent_plans.slice(0, 5).map((plan) => (
                    <div
                      key={plan.id}
                      onClick={() => {
                        setSelectedPlanId(plan.id);
                        setActiveTab('plans');
                      }}
                      className="p-3 rounded-lg bg-secondary/30 hover:bg-secondary/60 transition-colors border border-border/30 cursor-pointer flex items-center justify-between"
                    >
                      <div>
                        <span className="text-xs font-semibold text-foreground block">{plan.plan_title}</span>
                        <span className="text-[11px] text-muted-foreground">
                          {plan.student_name} ({plan.subject_code})
                        </span>
                      </div>
                      <span className={`text-xs px-2 py-0.5 rounded border ${getStatusBadge(plan.plan_status)}`}>
                        {plan.plan_status}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Active Priority Recommendations */}
            <div className="rounded-xl border border-border/50 bg-card/40 p-6 space-y-4">
              <h3 className="text-base font-semibold text-foreground flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-primary" />
                Priority Recommendations Awaiting Action
              </h3>
              {facultyDashboard.active_recommendations.length === 0 ? (
                <p className="text-xs text-muted-foreground py-6 text-center">
                  No active recommendations awaiting review.
                </p>
              ) : (
                <div className="space-y-3">
                  {facultyDashboard.active_recommendations.slice(0, 5).map((rec) => (
                    <div
                      key={rec.id}
                      className="p-3 rounded-lg bg-secondary/30 border border-border/30 flex items-center justify-between"
                    >
                      <div>
                        <span className="text-xs font-semibold text-foreground block">
                          {rec.proposed_action_title}
                        </span>
                        <span className="text-[11px] text-muted-foreground">
                          {rec.student_name} | Priority: {rec.priority}
                        </span>
                      </div>
                      <button
                        onClick={() => {
                          setSelectedRecForPlan(rec);
                          setNewPlanTitle(rec.proposed_action_title);
                          setNewPlanObjective(rec.proposed_action_description);
                          setIsCreatePlanOpen(true);
                        }}
                        className="text-xs px-2.5 py-1 rounded bg-primary text-primary-foreground font-medium hover:bg-primary/90"
                      >
                        Adopt Plan
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* TAB 2: RECOMMENDATIONS QUEUE */}
      {/* --------------------------------------------------------------------- */}
      {isFacultyOrAdmin && activeTab === 'recommendations' && (
        <div className="space-y-4">
          {isLoadingRecs ? (
            <div className="p-12 text-center text-muted-foreground">
              <RotateCcw className="h-6 w-6 animate-spin mx-auto mb-2 text-primary" />
              Loading recommendations queue...
            </div>
          ) : recommendations.length === 0 ? (
            <div className="p-12 text-center border border-dashed border-border/50 rounded-xl bg-card/20">
              <CheckCircle className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
              <p className="text-sm font-medium text-foreground">No pending recommendations for this student.</p>
              <p className="text-xs text-muted-foreground mt-1">
                Click &quot;Analyze &amp; Recommend&quot; to synthesize evidence from Phase 06 gaps and Phase 07 risk profiles.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {recommendations.map((rec) => (
                <div
                  key={rec.id}
                  className="rounded-xl border border-border/50 bg-card/40 p-5 space-y-3 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span
                        className={`text-xs px-2.5 py-0.5 rounded-full font-mono font-medium ${
                          rec.priority === 'CRITICAL'
                            ? 'bg-red-500/10 text-red-400 border border-red-500/30'
                            : rec.priority === 'HIGH'
                            ? 'bg-orange-500/10 text-orange-400 border border-orange-500/30'
                            : 'bg-secondary text-muted-foreground'
                        }`}
                      >
                        {rec.priority} Priority
                      </span>
                      <span className="text-xs font-mono text-muted-foreground">
                        Effort: ~{rec.suggested_duration_days} days
                      </span>
                    </div>

                    <h4 className="text-sm font-bold text-foreground">{rec.proposed_action_title}</h4>
                    <p className="text-xs text-muted-foreground mt-1 leading-relaxed">{rec.rationale}</p>

                    <div className="mt-3 p-2.5 rounded bg-secondary/30 border border-border/30 text-xs">
                      <span className="text-[11px] font-semibold text-muted-foreground uppercase block mb-1">
                        Proposed Pedagogical Action:
                      </span>
                      <p className="text-xs text-foreground/90">{rec.proposed_action_description}</p>
                    </div>
                  </div>

                  <div className="pt-3 border-t border-border/30 flex items-center justify-between">
                    <span className="text-[11px] text-muted-foreground font-mono">
                      Sufficiency: {rec.evidence_sufficiency}
                    </span>
                    <button
                      onClick={() => {
                        setSelectedRecForPlan(rec);
                        setNewPlanTitle(rec.proposed_action_title);
                        setNewPlanObjective(rec.proposed_action_description);
                        setIsCreatePlanOpen(true);
                      }}
                      className="inline-flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-md bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
                    >
                      <Plus className="h-3.5 w-3.5" />
                      Create Plan from Recommendation
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* TAB 3: INTERVENTION PLANS (Faculty View) */}
      {/* --------------------------------------------------------------------- */}
      {isFacultyOrAdmin && activeTab === 'plans' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Plans Roster */}
          <div className="space-y-3 md:col-span-1">
            <div className="flex items-center justify-between pb-2">
              <span className="text-xs font-semibold text-muted-foreground uppercase">Intervention Plans</span>
              <button
                onClick={() => {
                  setSelectedRecForPlan(null);
                  setNewPlanTitle('');
                  setNewPlanObjective('');
                  setIsCreatePlanOpen(true);
                }}
                className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded bg-secondary text-foreground hover:bg-secondary/80"
              >
                <Plus className="h-3.5 w-3.5" /> Custom Plan
              </button>
            </div>

            {isLoadingPlans ? (
              <div className="p-8 text-center text-xs text-muted-foreground">Loading plans...</div>
            ) : plans.length === 0 ? (
              <div className="p-8 text-center text-xs text-muted-foreground border border-dashed border-border/40 rounded-lg">
                No plans created yet.
              </div>
            ) : (
              plans.map((p) => (
                <div
                  key={p.id}
                  onClick={() => setSelectedPlanId(p.id)}
                  className={`p-3.5 rounded-lg border transition-all cursor-pointer ${
                    selectedPlanId === p.id
                      ? 'bg-secondary/70 border-primary/50'
                      : 'bg-card/40 border-border/40 hover:bg-secondary/30'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className={`text-[10px] px-2 py-0.5 rounded border ${getStatusBadge(p.plan_status)}`}>
                      {p.plan_status}
                    </span>
                    <span className="text-[11px] font-mono text-muted-foreground">
                      {p.actions.length} actions
                    </span>
                  </div>
                  <h4 className="text-xs font-bold text-foreground truncate">{p.plan_title}</h4>
                  <p className="text-[11px] text-muted-foreground mt-0.5 truncate">
                    Student: {p.student_name}
                  </p>
                </div>
              ))
            )}
          </div>

          {/* Active Plan Inspector */}
          <div className="md:col-span-2">
            {!activePlanDetail ? (
              <div className="p-12 text-center border border-dashed border-border/40 rounded-xl bg-card/20 text-muted-foreground text-xs">
                Select an intervention plan from the left panel to inspect actions, review status, and progress timeline.
              </div>
            ) : (
              <div className="rounded-xl border border-border/50 bg-card/60 p-6 space-y-6">
                {/* Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border/40 pb-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs px-2.5 py-0.5 rounded border ${getStatusBadge(activePlanDetail.plan_status)}`}>
                        {activePlanDetail.plan_status}
                      </span>
                      <span className="text-xs text-muted-foreground font-mono">
                        Course: {activePlanDetail.subject_code}
                      </span>
                    </div>
                    <h2 className="text-lg font-bold text-foreground mt-1">{activePlanDetail.plan_title}</h2>
                    <p className="text-xs text-muted-foreground">
                      Student: <strong>{activePlanDetail.student_name}</strong> ({activePlanDetail.enrollment_number})
                    </p>
                  </div>

                  {/* Faculty Actions */}
                  <div className="flex items-center gap-2">
                    {activePlanDetail.plan_status === 'PENDING_REVIEW' && (
                      <button
                        onClick={() => setIsReviewModalOpen(true)}
                        className="text-xs px-3 py-1.5 rounded-md bg-amber-500 text-amber-950 font-semibold hover:bg-amber-400"
                      >
                        Faculty Review Checkpoint
                      </button>
                    )}
                    {activePlanDetail.plan_status === 'APPROVED' && (
                      <button
                        onClick={() => assignPlanMutation.mutate(activePlanDetail.id)}
                        disabled={assignPlanMutation.isPending}
                        className="text-xs px-3 py-1.5 rounded-md bg-primary text-primary-foreground font-semibold hover:bg-primary/90"
                      >
                        Assign to Student
                      </button>
                    )}
                  </div>
                </div>

                {/* Objective */}
                <div>
                  <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">
                    Pedagogical Learning Objective
                  </h4>
                  <p className="text-xs text-foreground/90 bg-secondary/30 p-3 rounded-lg border border-border/30 leading-relaxed">
                    {activePlanDetail.learning_objective}
                  </p>
                </div>

                {/* Actions Checklist */}
                <div className="space-y-3">
                  <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    Assigned Action Items ({activePlanDetail.actions.length})
                  </h4>
                  {activePlanDetail.actions.map((act) => (
                    <div
                      key={act.id}
                      className="p-4 rounded-lg bg-secondary/20 border border-border/30 space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-foreground flex items-center gap-2">
                          <span className="h-5 w-5 rounded-full bg-secondary flex items-center justify-center text-[10px]">
                            {act.action_order}
                          </span>
                          {act.action_title}
                        </span>
                        <span className={`text-[10px] px-2 py-0.5 rounded border ${getStatusBadge(act.action_status)}`}>
                          {act.action_status}
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground pl-7">{act.instructions}</p>

                      {act.student_completion_notes && (
                        <div className="ml-7 mt-2 p-2.5 rounded bg-card/60 border border-border/30 text-xs">
                          <span className="text-[11px] font-semibold text-muted-foreground block">
                            Student Submission:
                          </span>
                          <p className="text-xs text-foreground/90 mt-0.5">{act.student_completion_notes}</p>
                          {act.student_submission_url && (
                            <a
                              href={act.student_submission_url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-primary hover:underline text-xs inline-flex items-center gap-1 mt-1 font-mono"
                            >
                              View Submission Artifact <ExternalLink className="h-3 w-3" />
                            </a>
                          )}
                        </div>
                      )}

                      {/* Faculty Verification Button */}
                      {act.action_status === 'SUBMITTED' && isFacultyOrAdmin && (
                        <div className="ml-7 pt-2 flex justify-end">
                          <button
                            onClick={() =>
                              updateActionStatusMutation.mutate({
                                actionId: act.id,
                                payload: {
                                  new_status: 'VERIFIED',
                                  faculty_feedback: 'Verified by course faculty.',
                                },
                              })
                            }
                            className="text-xs px-3 py-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-medium hover:bg-emerald-500/20"
                          >
                            Verify &amp; Accept Completion
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                {/* Progress History Timeline */}
                <div className="space-y-3 pt-4 border-t border-border/40">
                  <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    Audited Progress Timeline ({activePlanDetail.progress_events.length})
                  </h4>
                  <div className="space-y-2 text-xs">
                    {activePlanDetail.progress_events.map((ev) => (
                      <div key={ev.id} className="p-2.5 rounded bg-secondary/15 border border-border/20 flex items-start justify-between">
                        <div>
                          <span className="font-semibold text-foreground text-xs">{ev.event_type.replace(/_/g, ' ')}</span>
                          <p className="text-[11px] text-muted-foreground mt-0.5">{ev.event_notes}</p>
                        </div>
                        <span className="text-[10px] text-muted-foreground font-mono">
                          {new Date(ev.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* TAB 4: STUDENT WORKSPACE (Student View) */}
      {/* --------------------------------------------------------------------- */}
      {isStudent && (
        <div className="space-y-6">
          {isLoadingStudent ? (
            <div className="p-12 text-center text-muted-foreground">
              <RotateCcw className="h-6 w-6 animate-spin mx-auto mb-2 text-primary" />
              Loading your academic support plans...
            </div>
          ) : !studentWorkspace || studentWorkspace.active_plans.length === 0 ? (
            <div className="p-12 text-center border border-dashed border-border/50 rounded-xl bg-card/20">
              <CheckCircle className="h-8 w-8 text-emerald-400 mx-auto mb-2" />
              <p className="text-sm font-medium text-foreground">All coursework is currently up to date.</p>
              <p className="text-xs text-muted-foreground mt-1">
                No active intervention plans have been assigned to you.
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {studentWorkspace.active_plans.map((plan) => (
                <div key={plan.id} className="rounded-xl border border-border/50 bg-card/60 p-6 space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border/40 pb-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className={`text-xs px-2.5 py-0.5 rounded border ${getStatusBadge(plan.plan_status)}`}>
                          {plan.plan_status}
                        </span>
                        <span className="text-xs text-muted-foreground font-mono">
                          Course: {plan.subject_code} - {plan.subject_name}
                        </span>
                      </div>
                      <h3 className="text-lg font-bold text-foreground mt-1">{plan.plan_title}</h3>
                    </div>

                    <span className="text-xs text-muted-foreground">
                      Advisor: {plan.assigned_faculty_name || 'Course Instructor'}
                    </span>
                  </div>

                  <div>
                    <span className="text-[11px] font-semibold text-muted-foreground uppercase">
                      Objective &amp; Learning Purpose
                    </span>
                    <p className="text-xs text-foreground/90 mt-1 leading-relaxed bg-secondary/30 p-3 rounded-lg border border-border/30">
                      {plan.learning_objective}
                    </p>
                  </div>

                  <div className="space-y-3">
                    <span className="text-[11px] font-semibold text-muted-foreground uppercase">
                      Your Action Tasks ({plan.actions.length})
                    </span>
                    {plan.actions.map((act) => (
                      <div
                        key={act.id}
                        className="p-4 rounded-lg bg-secondary/20 border border-border/30 space-y-3"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-foreground flex items-center gap-2">
                            <span className="h-5 w-5 rounded-full bg-secondary flex items-center justify-center text-[10px]">
                              {act.action_order}
                            </span>
                            {act.action_title}
                          </span>
                          <span className={`text-[10px] px-2 py-0.5 rounded border ${getStatusBadge(act.action_status)}`}>
                            {act.action_status}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground pl-7">{act.instructions}</p>

                        {/* Student action buttons */}
                        <div className="pl-7 pt-1 flex items-center gap-2">
                          {act.action_status === 'ASSIGNED' && (
                            <button
                              onClick={() =>
                                updateActionStatusMutation.mutate({
                                  actionId: act.id,
                                  payload: { new_status: 'IN_PROGRESS' },
                                })
                              }
                              className="text-xs px-3 py-1.5 rounded bg-primary text-primary-foreground font-medium hover:bg-primary/90"
                            >
                              Start Working on Task
                            </button>
                          )}

                          {(act.action_status === 'IN_PROGRESS' || act.action_status === 'ASSIGNED') && (
                            <button
                              onClick={() => {
                                setSubmittingActionId(act.id);
                                setIsSubmitActionOpen(true);
                              }}
                              className="text-xs px-3 py-1.5 rounded bg-secondary text-foreground hover:bg-secondary/80 font-medium border border-border/40"
                            >
                              Submit Completion Evidence
                            </button>
                          )}

                          {act.action_status === 'SUBMITTED' && (
                            <span className="text-xs text-amber-400 font-medium">
                              Evidence submitted. Awaiting faculty verification.
                            </span>
                          )}

                          {act.action_status === 'VERIFIED' && (
                            <span className="text-xs text-emerald-400 font-medium flex items-center gap-1">
                              <CheckCircle className="h-3.5 w-3.5" /> Verified by faculty!
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* Create Plan Modal */}
      {/* --------------------------------------------------------------------- */}
      {isCreatePlanOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg rounded-xl border border-border bg-card p-6 shadow-xl space-y-4">
            <h3 className="text-lg font-bold text-foreground">Create Academic Support Plan</h3>
            <p className="text-xs text-muted-foreground">
              Define the learning objectives and actions for this student intervention.
            </p>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-muted-foreground mb-1 font-medium">Plan Title</label>
                <input
                  type="text"
                  value={newPlanTitle}
                  onChange={(e) => setNewPlanTitle(e.target.value)}
                  placeholder="e.g. Paxos Consensus Mastery Acceleration"
                  className="w-full h-9 px-3 rounded-md bg-secondary border border-border text-sm"
                />
              </div>

              <div>
                <label className="block text-muted-foreground mb-1 font-medium">Learning Objective</label>
                <textarea
                  value={newPlanObjective}
                  onChange={(e) => setNewPlanObjective(e.target.value)}
                  rows={3}
                  placeholder="Describe the target understanding and mastery criteria..."
                  className="w-full p-3 rounded-md bg-secondary border border-border text-sm resize-none"
                />
              </div>
            </div>

            <div className="pt-2 flex justify-end gap-2">
              <button
                onClick={() => setIsCreatePlanOpen(false)}
                className="px-4 py-2 rounded-md text-xs font-medium text-muted-foreground hover:bg-secondary"
              >
                Cancel
              </button>
              <button
                onClick={() =>
                  createPlanMutation.mutate({
                    student_id: selectedStudentId,
                    subject_id: selectedSubjectId,
                    topic_id: selectedRecForPlan?.topic_id,
                    recommendation_id: selectedRecForPlan?.id,
                    plan_title: newPlanTitle,
                    learning_objective: newPlanObjective,
                  })
                }
                disabled={createPlanMutation.isPending || !newPlanTitle || !newPlanObjective}
                className="px-4 py-2 rounded-md text-xs font-medium bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
              >
                {createPlanMutation.isPending ? 'Creating...' : 'Save & Queue for Review'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* Faculty Review Modal */}
      {/* --------------------------------------------------------------------- */}
      {isReviewModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-xl border border-border bg-card p-6 shadow-xl space-y-4">
            <h3 className="text-lg font-bold text-foreground">Faculty Review Checkpoint</h3>
            <p className="text-xs text-muted-foreground">
              Review and approve or reject this student support plan.
            </p>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-muted-foreground mb-1 font-medium">Review Decision</label>
                <div className="flex items-center gap-3">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      checked={reviewDecision === 'APPROVE'}
                      onChange={() => setReviewDecision('APPROVE')}
                    />
                    <span className="text-emerald-400 font-semibold">Approve Plan</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      checked={reviewDecision === 'REJECT'}
                      onChange={() => setReviewDecision('REJECT')}
                    />
                    <span className="text-red-400 font-semibold">Reject Plan</span>
                  </label>
                </div>
              </div>

              <div>
                <label className="block text-muted-foreground mb-1 font-medium">Review Notes</label>
                <textarea
                  value={reviewNotes}
                  onChange={(e) => setReviewNotes(e.target.value)}
                  rows={3}
                  placeholder="Add advisory notes, reasons, or recommendations..."
                  className="w-full p-3 rounded-md bg-secondary border border-border text-sm resize-none"
                />
              </div>
            </div>

            <div className="pt-2 flex justify-end gap-2">
              <button
                onClick={() => setIsReviewModalOpen(false)}
                className="px-4 py-2 rounded-md text-xs font-medium text-muted-foreground hover:bg-secondary"
              >
                Cancel
              </button>
              <button
                onClick={() => reviewPlanMutation.mutate()}
                disabled={reviewPlanMutation.isPending}
                className="px-4 py-2 rounded-md text-xs font-medium bg-primary text-primary-foreground hover:bg-primary/90"
              >
                {reviewPlanMutation.isPending ? 'Submitting...' : 'Submit Review'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* Submit Action Modal */}
      {/* --------------------------------------------------------------------- */}
      {isSubmitActionOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-xl border border-border bg-card p-6 shadow-xl space-y-4">
            <h3 className="text-lg font-bold text-foreground">Submit Task Evidence</h3>
            <p className="text-xs text-muted-foreground">
              Provide summary notes and any artifact link demonstrating completion of this action.
            </p>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-muted-foreground mb-1 font-medium">Completion Summary</label>
                <textarea
                  value={studentSubmissionNotes}
                  onChange={(e) => setStudentSubmissionNotes(e.target.value)}
                  rows={3}
                  placeholder="Explain what concepts you revised, problems solved, or questions answered..."
                  className="w-full p-3 rounded-md bg-secondary border border-border text-sm resize-none"
                />
              </div>

              <div>
                <label className="block text-muted-foreground mb-1 font-medium">Artifact / Solution URL (Optional)</label>
                <input
                  type="text"
                  value={studentSubmissionUrl}
                  onChange={(e) => setStudentSubmissionUrl(e.target.value)}
                  placeholder="e.g. GitHub link, Colab notebook, or cloud doc"
                  className="w-full h-9 px-3 rounded-md bg-secondary border border-border text-sm font-mono"
                />
              </div>
            </div>

            <div className="pt-2 flex justify-end gap-2">
              <button
                onClick={() => setIsSubmitActionOpen(false)}
                className="px-4 py-2 rounded-md text-xs font-medium text-muted-foreground hover:bg-secondary"
              >
                Cancel
              </button>
              <button
                onClick={() =>
                  updateActionStatusMutation.mutate({
                    actionId: submittingActionId,
                    payload: {
                      new_status: 'SUBMITTED',
                      student_completion_notes: studentSubmissionNotes,
                      student_submission_url: studentSubmissionUrl,
                    },
                  })
                }
                disabled={updateActionStatusMutation.isPending || !studentSubmissionNotes}
                className="px-4 py-2 rounded-md text-xs font-medium bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
              >
                {updateActionStatusMutation.isPending ? 'Submitting...' : 'Submit Evidence'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
