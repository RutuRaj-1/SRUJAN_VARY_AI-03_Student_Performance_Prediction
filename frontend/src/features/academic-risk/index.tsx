import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  AlertTriangle,
  ShieldAlert,
  ShieldCheck,
  CheckCircle,
  HelpCircle,
  Play,
  RotateCcw,
  Sliders,
  Database,
  Layers,
  Info,
  ChevronRight,
  Cpu,
  Lock,
} from 'lucide-react';
import {
  riskService,
  RiskClassification,
  RiskModelType,
  AcademicRiskTarget,
  CohortRiskSummary,
  StudentRiskProfile,
  RiskModelVersion,
} from '@/services/risk-service';
import { syllabusService, AcademicSubject } from '@/services/syllabus-service';
import { academicDataService, StudentAcademicProfile } from '@/services/academic-data-service';
import { useAuth } from '@/context/auth-context';

export const AcademicRiskPage: React.FC = () => {
  const { profile } = useAuth();
  const queryClient = useQueryClient();

  const isStudent = profile?.role === 'STUDENT';
  const isPlacementOfficer = profile?.role === 'PLACEMENT_OFFICER';
  const isFacultyOrAdmin =
    profile?.role === 'FACULTY' ||
    profile?.role === 'INSTITUTION_ADMIN' ||
    profile?.role === 'SUPER_ADMIN';

  // Navigation tab state
  const [activeTab, setActiveTab] = useState<'cohort' | 'student' | 'governance'>(
    isStudent ? 'student' : 'cohort'
  );

  // Global selection state
  const [selectedSubjectId, setSelectedSubjectId] = useState<string>('');
  const [selectedTargetId, setSelectedTargetId] = useState<string>('');
  const [selectedStudentId, setSelectedStudentId] = useState<string>('');
  const [riskFilter, setRiskFilter] = useState<string>('ALL');

  // Governance Drawer & Train Modal state
  const [isTrainModalOpen, setIsTrainModalOpen] = useState(false);
  const [trainModelType, setTrainModelType] = useState<RiskModelType>('LOGISTIC_REGRESSION');
  const [trainVersionTag, setTrainVersionTag] = useState('');

  // ---------------------------------------------------------------------------
  // Data Queries
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

  // Default subject
  useEffect(() => {
    if (subjects.length > 0 && !selectedSubjectId) {
      setSelectedSubjectId(subjects[0].id);
    }
  }, [subjects, selectedSubjectId]);

  // Default student for faculty/admin vs student self-resolution
  useEffect(() => {
    if (isFacultyOrAdmin) {
      if (students.length > 0 && !selectedStudentId) {
        setSelectedStudentId(students[0].id);
      }
    } else if (isStudent && profile?.user_id) {
      // Student self-resolution: fetch their student profile
      academicDataService.getStudents().then((studList) => {
        const selfStud = studList.find((s) => s.profile_id === profile.user_id);
        if (selfStud) {
          setSelectedStudentId(selfStud.id);
        }
      });
    }
  }, [students, profile, isFacultyOrAdmin, isStudent, selectedStudentId]);

  // Targets query
  const { data: targets = [] } = useQuery<AcademicRiskTarget[]>({
    queryKey: ['risk-targets', selectedSubjectId],
    queryFn: () => riskService.getTargets(selectedSubjectId),
    enabled: !!selectedSubjectId,
  });

  useEffect(() => {
    if (targets.length > 0 && !selectedTargetId) {
      setSelectedTargetId(targets[0].id);
    }
  }, [targets, selectedTargetId]);

  // Cohort Risk Summary query
  const {
    data: cohortSummary,
    isLoading: isLoadingCohort,
  } = useQuery<CohortRiskSummary>({
    queryKey: ['cohort-risk-summary', selectedSubjectId, selectedTargetId],
    queryFn: () => riskService.getCohortSummary(selectedSubjectId, selectedTargetId || undefined),
    enabled: !!selectedSubjectId && isFacultyOrAdmin,
  });

  // Student Risk Profile query
  const {
    data: studentRiskProfile,
    isLoading: isLoadingProfile,
  } = useQuery<StudentRiskProfile>({
    queryKey: ['student-risk-profile', selectedStudentId, selectedSubjectId, selectedTargetId],
    queryFn: () =>
      riskService.getStudentRiskProfile(
        selectedStudentId,
        selectedSubjectId,
        selectedTargetId || undefined
      ),
    enabled: !!selectedStudentId && !!selectedSubjectId,
  });

  // Dataset Readiness query
  const { data: readinessData, isLoading: isLoadingReadiness } = useQuery({
    queryKey: ['risk-readiness', selectedSubjectId, selectedTargetId],
    queryFn: () => riskService.getReadiness(selectedSubjectId, selectedTargetId || undefined),
    enabled: !!selectedSubjectId && isFacultyOrAdmin && activeTab === 'governance',
  });

  // Model Versions query
  const { data: modelVersions = [], refetch: refetchModels } = useQuery<RiskModelVersion[]>({
    queryKey: ['risk-models', selectedTargetId],
    queryFn: () => riskService.getModels(selectedTargetId || undefined),
    enabled: !!selectedTargetId && isFacultyOrAdmin && activeTab === 'governance',
  });

  // ---------------------------------------------------------------------------
  // Mutations
  // ---------------------------------------------------------------------------
  const generateMutation = useMutation({
    mutationFn: () =>
      riskService.generatePredictions({
        subject_id: selectedSubjectId,
        target_id: selectedTargetId,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cohort-risk-summary'] });
      queryClient.invalidateQueries({ queryKey: ['student-risk-profile'] });
    },
  });

  const trainMutation = useMutation({
    mutationFn: () =>
      riskService.trainModel(selectedSubjectId, {
        target_id: selectedTargetId,
        model_type: trainModelType,
        version_tag: trainVersionTag || `v${Date.now().toString().slice(-4)}`,
      }),
    onSuccess: () => {
      setIsTrainModalOpen(false);
      refetchModels();
      queryClient.invalidateQueries({ queryKey: ['cohort-risk-summary'] });
      queryClient.invalidateQueries({ queryKey: ['risk-readiness'] });
    },
  });

  const activateMutation = useMutation({
    mutationFn: (modelVersionId: string) => riskService.activateModel(modelVersionId),
    onSuccess: () => {
      refetchModels();
      queryClient.invalidateQueries({ queryKey: ['cohort-risk-summary'] });
    },
  });

  // ---------------------------------------------------------------------------
  // Placement Officer Privacy Guard
  // ---------------------------------------------------------------------------
  if (isPlacementOfficer) {
    return (
      <div className="p-8 max-w-4xl mx-auto">
        <div className="rounded-xl border border-red-500/20 bg-red-950/20 p-8 text-center backdrop-blur-sm">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-red-500/10 text-red-400 mb-4">
            <Lock className="h-7 w-7" />
          </div>
          <h2 className="text-xl font-semibold text-red-200">Governance Privacy Boundary Enforced</h2>
          <p className="mt-3 text-sm text-red-300/80 leading-relaxed max-w-xl mx-auto">
            Academic Risk Prediction signals are strictly compartmentalized for supportive faculty advising
            and learning intervention. To prevent systemic bias and algorithmic discrimination in campus
            recruitment, Placement Officers are barred from accessing student risk probabilities.
          </p>
          <div className="mt-6 inline-flex items-center gap-2 text-xs text-red-400 bg-red-950/50 px-4 py-2 rounded-lg border border-red-900/50">
            <ShieldAlert className="h-4 w-4" />
            MASTERY Ethical AI Charter § 4.2: Placement Isolation
          </div>
        </div>
      </div>
    );
  }

  // ---------------------------------------------------------------------------
  // Helper for Badge Colors
  // ---------------------------------------------------------------------------
  const getRiskBadge = (classification: RiskClassification) => {
    switch (classification) {
      case 'CRITICAL':
        return {
          bg: 'bg-red-500/10 border-red-500/30 text-red-400',
          dot: 'bg-red-500',
          label: 'Critical Risk',
        };
      case 'HIGH':
        return {
          bg: 'bg-orange-500/10 border-orange-500/30 text-orange-400',
          dot: 'bg-orange-500',
          label: 'High Risk',
        };
      case 'MODERATE':
        return {
          bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
          dot: 'bg-amber-500',
          label: 'Moderate Risk',
        };
      case 'LOW':
        return {
          bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
          dot: 'bg-emerald-500',
          label: 'Low Risk',
        };
      case 'INSUFFICIENT_EVIDENCE':
      default:
        return {
          bg: 'bg-slate-500/10 border-slate-500/30 text-slate-400',
          dot: 'bg-slate-400',
          label: 'Insufficient Evidence',
        };
    }
  };

  const filteredCohortStudents =
    cohortSummary?.students.filter((s) => {
      if (riskFilter === 'ALL') return true;
      return s.risk_classification === riskFilter;
    }) || [];

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      {/* --------------------------------------------------------------------- */}
      {/* Page Header */}
      {/* --------------------------------------------------------------------- */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border/40 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400">
              <ShieldAlert className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2 font-sans">
                Academic Risk Prediction Engine
                <span className="text-xs font-medium px-2 py-0.5 rounded-[3px] bg-[#EEF8F7] text-[#123E40] border border-[#BDCEC8] font-mono">
                  Module 05
                </span>
              </h1>
              <p className="text-sm text-muted-foreground mt-0.5">
                Time-bounded, explainable early warning signals derived strictly from verified academic records.
              </p>
            </div>
          </div>
        </div>

        {/* Global Controls */}
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={selectedSubjectId}
            onChange={(e) => setSelectedSubjectId(e.target.value)}
            className="h-9 px-3 rounded-md bg-secondary/50 border border-border text-sm focus:outline-none focus:ring-1 focus:ring-primary"
          >
            {subjects.map((s) => (
              <option key={s.id} value={s.id}>
                {s.code} - {s.name}
              </option>
            ))}
          </select>

          {targets.length > 0 && (
            <select
              value={selectedTargetId}
              onChange={(e) => setSelectedTargetId(e.target.value)}
              className="h-9 px-3 rounded-md bg-secondary/50 border border-border text-sm focus:outline-none focus:ring-1 focus:ring-primary"
            >
              {targets.map((t) => (
                <option key={t.id} value={t.id}>
                  Target: {t.target_name} ({t.passing_threshold_percentage}%)
                </option>
              ))}
            </select>
          )}

          {isFacultyOrAdmin && (
            <button
              onClick={() => generateMutation.mutate()}
              disabled={generateMutation.isPending || !selectedTargetId}
              className="inline-flex items-center gap-2 h-9 px-4 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
            >
              {generateMutation.isPending ? (
                <>
                  <RotateCcw className="h-4 w-4 animate-spin" />
                  Screening...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4" />
                  Run Screening
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {/* --------------------------------------------------------------------- */}
      {/* Mandatory Scientific Disclaimer Banner */}
      {/* --------------------------------------------------------------------- */}
      <div className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-4 flex items-start gap-3">
        <Info className="h-5 w-5 text-amber-400 mt-0.5 shrink-0" />
        <div className="text-xs text-amber-200/90 leading-relaxed">
          <span className="font-semibold text-amber-300">Mandatory Scientific & Governance Notice: </span>
          Predictive signals represent empirical risk indicators evaluated against institutional thresholds.
          They do <strong>NOT</strong> reflect student cognitive potential, intelligence, or definitive outcomes.
          Predictions are strictly time-bounded before cutoffs to prevent temporal and target leakage.
        </div>
      </div>

      {/* --------------------------------------------------------------------- */}
      {/* Metric Overview Strip (Faculty/Admin) */}
      {/* --------------------------------------------------------------------- */}
      {isFacultyOrAdmin && cohortSummary && (
        <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
          <div className="p-4 rounded-lg bg-card/50 border border-border/40">
            <span className="text-xs text-muted-foreground">Enrolled Students</span>
            <div className="text-2xl font-bold mt-1 text-foreground">{cohortSummary.total_enrolled}</div>
          </div>
          <div className="p-4 rounded-lg bg-card/50 border border-border/40">
            <span className="text-xs text-muted-foreground">Evaluated</span>
            <div className="text-2xl font-bold mt-1 text-primary">{cohortSummary.evaluated_count}</div>
          </div>
          <div className="p-4 rounded-lg bg-red-500/5 border border-red-500/20">
            <span className="text-xs text-red-400 font-medium">Critical Risk</span>
            <div className="text-2xl font-bold mt-1 text-red-400">{cohortSummary.critical_count}</div>
          </div>
          <div className="p-4 rounded-lg bg-orange-500/5 border border-orange-500/20">
            <span className="text-xs text-orange-400 font-medium">High Risk</span>
            <div className="text-2xl font-bold mt-1 text-orange-400">{cohortSummary.high_count}</div>
          </div>
          <div className="p-4 rounded-lg bg-amber-500/5 border border-amber-500/20">
            <span className="text-xs text-amber-400 font-medium">Moderate Risk</span>
            <div className="text-2xl font-bold mt-1 text-amber-400">{cohortSummary.moderate_count}</div>
          </div>
          <div className="p-4 rounded-lg bg-slate-500/5 border border-slate-500/20">
            <span className="text-xs text-slate-400 font-medium">Insufficient Evidence</span>
            <div className="text-2xl font-bold mt-1 text-slate-400">
              {cohortSummary.insufficient_evidence_count}
            </div>
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* Navigation Tabs */}
      {/* --------------------------------------------------------------------- */}
      <div className="flex items-center gap-2 border-b border-border/40 pb-2">
        {isFacultyOrAdmin && (
          <button
            onClick={() => setActiveTab('cohort')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'cohort'
                ? 'bg-secondary text-foreground'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Cohort Risk Ledger
          </button>
        )}
        <button
          onClick={() => setActiveTab('student')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'student'
              ? 'bg-secondary text-foreground'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          {isStudent ? 'My Academic Risk Assessment' : 'Student Risk Profile & Attributions'}
        </button>
        {isFacultyOrAdmin && (
          <button
            onClick={() => setActiveTab('governance')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'governance'
                ? 'bg-secondary text-foreground'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Model Governance & Readiness
          </button>
        )}
      </div>

      {/* --------------------------------------------------------------------- */}
      {/* TAB 1: COHORT RISK LEDGER (Faculty/Admin) */}
      {/* --------------------------------------------------------------------- */}
      {isFacultyOrAdmin && activeTab === 'cohort' && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-card/30 p-3 rounded-lg border border-border/40">
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-muted-foreground">Filter by Risk Tier:</span>
              <div className="flex flex-wrap gap-1.5">
                {['ALL', 'CRITICAL', 'HIGH', 'MODERATE', 'LOW', 'INSUFFICIENT_EVIDENCE'].map((tier) => (
                  <button
                    key={tier}
                    onClick={() => setRiskFilter(tier)}
                    className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                      riskFilter === tier
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-secondary/60 text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    {tier.replace('_', ' ')}
                  </button>
                ))}
              </div>
            </div>
            <div className="text-xs text-muted-foreground">
              Showing {filteredCohortStudents.length} of {cohortSummary?.students.length || 0} students
            </div>
          </div>

          {isLoadingCohort ? (
            <div className="p-12 text-center text-muted-foreground">
              <RotateCcw className="h-6 w-6 animate-spin mx-auto mb-2 text-primary" />
              Loading cohort risk ledger...
            </div>
          ) : filteredCohortStudents.length === 0 ? (
            <div className="p-12 text-center border border-dashed border-border/50 rounded-xl bg-card/20">
              <ShieldCheck className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
              <p className="text-sm font-medium text-foreground">No students match current filter.</p>
              <p className="text-xs text-muted-foreground mt-1">
                Run predictive screening or select another target.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto rounded-lg border border-border/40 bg-card/40">
              <table className="w-full text-left text-sm">
                <thead className="bg-muted/40 text-xs font-medium text-muted-foreground border-b border-border/40">
                  <tr>
                    <th className="px-4 py-3">Student Name</th>
                    <th className="px-4 py-3">Enrollment No.</th>
                    <th className="px-4 py-3">Risk Tier</th>
                    <th className="px-4 py-3">Probability Score</th>
                    <th className="px-4 py-3">Evidence Sufficiency</th>
                    <th className="px-4 py-3">Key Adverse Driver</th>
                    <th className="px-4 py-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/20">
                  {filteredCohortStudents.map((stud) => {
                    const badge = getRiskBadge(stud.risk_classification);
                    return (
                      <tr key={stud.student_id} className="hover:bg-muted/20 transition-colors">
                        <td className="px-4 py-3 font-medium text-foreground">{stud.student_name}</td>
                        <td className="px-4 py-3 font-mono text-xs text-muted-foreground">
                          {stud.enrollment_number}
                        </td>
                        <td className="px-4 py-3">
                          <span
                            className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${badge.bg}`}
                          >
                            <span className={`h-1.5 w-1.5 rounded-full ${badge.dot}`} />
                            {badge.label}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          {stud.risk_score !== null && stud.risk_score !== undefined ? (
                            <div className="flex items-center gap-2">
                              <span className="font-mono text-xs font-semibold">
                                {(stud.risk_score * 100).toFixed(0)}%
                              </span>
                              <div className="w-16 h-1.5 rounded-full bg-secondary overflow-hidden">
                                <div
                                  className={`h-full rounded-full ${
                                    stud.risk_score >= 0.75
                                      ? 'bg-red-500'
                                      : stud.risk_score >= 0.55
                                      ? 'bg-orange-500'
                                      : stud.risk_score >= 0.3
                                      ? 'bg-amber-500'
                                      : 'bg-emerald-500'
                                  }`}
                                  style={{ width: `${stud.risk_score * 100}%` }}
                                />
                              </div>
                            </div>
                          ) : (
                            <span className="text-xs text-muted-foreground italic">None (Baseline)</span>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <span
                            className={`text-xs px-2 py-0.5 rounded font-mono ${
                              stud.evidence_sufficiency === 'STRONG'
                                ? 'bg-emerald-500/10 text-emerald-400'
                                : stud.evidence_sufficiency === 'MODERATE'
                                ? 'bg-blue-500/10 text-blue-400'
                                : stud.evidence_sufficiency === 'LIMITED'
                                ? 'bg-amber-500/10 text-amber-400'
                                : 'bg-slate-500/10 text-slate-400'
                            }`}
                          >
                            {stud.evidence_sufficiency}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-xs text-muted-foreground max-w-xs truncate">
                          {stud.top_adverse_factor || 'None detected'}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <button
                            onClick={() => {
                              setSelectedStudentId(stud.student_id);
                              setActiveTab('student');
                            }}
                            className="inline-flex items-center gap-1 text-xs text-primary hover:underline font-medium"
                          >
                            Attributions <ChevronRight className="h-3.5 w-3.5" />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* TAB 2: STUDENT RISK PROFILE & EXPLAINABILITY */}
      {/* --------------------------------------------------------------------- */}
      {activeTab === 'student' && (
        <div className="space-y-6">
          {/* Faculty Student Selector */}
          {isFacultyOrAdmin && (
            <div className="flex items-center gap-3 bg-card/40 p-3 rounded-lg border border-border/40">
              <span className="text-xs font-medium text-muted-foreground">Select Inspected Student:</span>
              <select
                value={selectedStudentId}
                onChange={(e) => setSelectedStudentId(e.target.value)}
                className="h-8 px-2.5 rounded bg-secondary text-sm border border-border"
              >
                {students.map((stud) => (
                  <option key={stud.id} value={stud.id}>
                    {stud.first_name} {stud.last_name} ({stud.enrollment_number})
                  </option>
                ))}
              </select>
            </div>
          )}

          {isLoadingProfile ? (
            <div className="p-12 text-center text-muted-foreground">
              <RotateCcw className="h-6 w-6 animate-spin mx-auto mb-2 text-primary" />
              Loading student risk assessment...
            </div>
          ) : !studentRiskProfile?.active_prediction ? (
            <div className="p-12 text-center border border-dashed border-border/50 rounded-xl bg-card/20">
              <HelpCircle className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
              <p className="text-sm font-medium text-foreground">No predictive assessment on record.</p>
              <p className="text-xs text-muted-foreground mt-1">
                Continuous assessment evidence has not yet been processed for this subject.
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Profile Card */}
              <div className="rounded-xl border border-border/50 bg-card/60 p-6">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div>
                    <span className="text-xs text-muted-foreground uppercase tracking-wider font-semibold">
                      Academic Risk Evaluation
                    </span>
                    <h2 className="text-xl font-bold text-foreground mt-1">
                      {studentRiskProfile.student_name}
                    </h2>
                    <p className="text-xs text-muted-foreground font-mono mt-0.5">
                      Roll: {studentRiskProfile.enrollment_number} | Course: {studentRiskProfile.subject_code} -{' '}
                      {studentRiskProfile.subject_name}
                    </p>
                  </div>

                  <div className="flex items-center gap-4">
                    {(() => {
                      const badge = getRiskBadge(
                        studentRiskProfile.active_prediction.risk_classification
                      );
                      return (
                        <div className={`px-4 py-2 rounded-lg border ${badge.bg} text-center`}>
                          <span className="text-xs block text-muted-foreground font-medium">Risk Status</span>
                          <span className="text-base font-bold flex items-center gap-2 justify-center mt-0.5">
                            <span className={`h-2 w-2 rounded-full ${badge.dot}`} />
                            {badge.label}
                          </span>
                        </div>
                      );
                    })()}

                    {studentRiskProfile.active_prediction.risk_score !== null &&
                      studentRiskProfile.active_prediction.risk_score !== undefined && (
                        <div className="px-4 py-2 rounded-lg border border-border/40 bg-secondary/40 text-center">
                          <span className="text-xs block text-muted-foreground font-medium">
                            Deficit Probability
                          </span>
                          <span className="text-base font-bold font-mono text-foreground mt-0.5">
                            {(studentRiskProfile.active_prediction.risk_score * 100).toFixed(1)}%
                          </span>
                        </div>
                      )}

                    <div className="px-4 py-2 rounded-lg border border-border/40 bg-secondary/40 text-center">
                      <span className="text-xs block text-muted-foreground font-medium">
                        Evidence Sufficiency
                      </span>
                      <span className="text-sm font-semibold font-mono text-foreground mt-0.5">
                        {studentRiskProfile.active_prediction.evidence_sufficiency}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Explainability Attributions */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-semibold text-foreground flex items-center gap-2">
                    <Sliders className="h-4 w-4 text-primary" />
                    Transparent Grounded Feature Attributions
                  </h3>
                  <span className="text-xs text-muted-foreground">
                    Derived strictly from time-bounded student evidence
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {studentRiskProfile.active_prediction.explanations.map((exp) => (
                    <div
                      key={exp.id}
                      className={`p-4 rounded-lg border transition-all ${
                        exp.is_adverse_factor
                          ? 'border-red-500/20 bg-red-500/5'
                          : 'border-emerald-500/20 bg-emerald-500/5'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-mono font-medium text-foreground">
                          {exp.feature_name.replace(/_/g, ' ')}
                        </span>
                        <span
                          className={`text-xs px-2 py-0.5 rounded font-mono font-medium ${
                            exp.is_adverse_factor
                              ? 'bg-red-500/20 text-red-400'
                              : 'bg-emerald-500/20 text-emerald-400'
                          }`}
                        >
                          {exp.is_adverse_factor ? 'Adverse Risk Factor' : 'Protective Factor'}
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground leading-relaxed">
                        {exp.explanation_text}
                      </p>
                      <div className="mt-3 pt-2 border-t border-border/20 flex items-center justify-between text-xs text-muted-foreground">
                        <span className="flex items-center gap-1 font-mono">
                          Value: <strong>{exp.feature_value}</strong>
                        </span>
                        <span className="italic font-sans text-muted-foreground/80">
                          Provenance: {exp.source_evidence_reference}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Feature Vector Snapshot (when available) */}
              {studentRiskProfile.feature_snapshot && (
                <div className="rounded-lg border border-border/40 bg-card/30 p-4">
                  <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3">
                    Validated Feature Vector Snapshot
                  </h4>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                    {Object.entries(studentRiskProfile.feature_snapshot).map(([k, v]) => (
                      <div key={k} className="p-2.5 rounded bg-secondary/30 border border-border/30">
                        <span className="text-muted-foreground block text-[11px] truncate">
                          {k.replace(/_/g, ' ')}
                        </span>
                        <span className="font-mono font-semibold text-foreground mt-0.5 block">
                          {typeof v === 'number' ? v.toFixed(2) : String(v)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* TAB 3: MODEL GOVERNANCE & READINESS (Faculty/Admin) */}
      {/* --------------------------------------------------------------------- */}
      {isFacultyOrAdmin && activeTab === 'governance' && (
        <div className="space-y-6">
          {/* Dataset Readiness Audit */}
          <div className="rounded-xl border border-border/50 bg-card/40 p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold text-foreground flex items-center gap-2">
                  <Database className="h-4 w-4 text-primary" />
                  Dataset Readiness Gate Audit
                </h3>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Verifies that historical cohort labels satisfy minimum training requirements before model fitting.
                </p>
              </div>

              {readinessData?.is_dataset_ready_for_training ? (
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
                  <CheckCircle className="h-3.5 w-3.5" />
                  Dataset Ready for ML Training
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-amber-500/10 border border-amber-500/30 text-amber-400">
                  <AlertTriangle className="h-3.5 w-3.5" />
                  Deterministic Rules Fallback Active
                </span>
              )}
            </div>

            {isLoadingReadiness ? (
              <div className="py-6 text-center text-xs text-muted-foreground">
                Evaluating dataset readiness...
              </div>
            ) : readinessData ? (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                <div className="p-3 rounded-lg bg-secondary/30 border border-border/30">
                  <span className="text-muted-foreground">Eligible Labeled Samples</span>
                  <div className="text-lg font-bold text-foreground mt-0.5">
                    {readinessData.eligible_labeled_samples} / 20 required
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-secondary/30 border border-border/30">
                  <span className="text-muted-foreground">Positive Class (At-Risk)</span>
                  <div className="text-lg font-bold text-red-400 mt-0.5">
                    {readinessData.positive_class_count}
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-secondary/30 border border-border/30">
                  <span className="text-muted-foreground">Negative Class (Passed)</span>
                  <div className="text-lg font-bold text-emerald-400 mt-0.5">
                    {readinessData.negative_class_count}
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-secondary/30 border border-border/30">
                  <span className="text-muted-foreground">Recommended Engine</span>
                  <div className="text-lg font-bold text-primary mt-0.5">
                    {readinessData.recommended_model_type}
                  </div>
                </div>
              </div>
            ) : null}

            {readinessData?.readiness_notes && (
              <div className="p-3 rounded-lg bg-secondary/20 border border-border/30">
                <span className="text-xs font-semibold text-muted-foreground block mb-1">
                  Readiness Audit Findings:
                </span>
                <ul className="list-disc list-inside space-y-0.5 text-xs text-muted-foreground">
                  {readinessData.readiness_notes.map((n, i) => (
                    <li key={i}>{n}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setIsTrainModalOpen(true)}
                className="inline-flex items-center gap-2 h-9 px-4 rounded-md bg-secondary hover:bg-secondary/80 text-foreground text-sm font-medium transition-colors"
              >
                <Cpu className="h-4 w-4" />
                Train / Calibrate New Model
              </button>
            </div>
          </div>

          {/* Model Registry Table */}
          <div className="rounded-xl border border-border/50 bg-card/40 p-6 space-y-4">
            <h3 className="text-base font-semibold text-foreground flex items-center gap-2">
              <Layers className="h-4 w-4 text-primary" />
              Institutional Model Versions Registry
            </h3>

            {modelVersions.length === 0 ? (
              <div className="p-8 text-center text-xs text-muted-foreground">
                No model versions registered for this target yet.
              </div>
            ) : (
              <div className="overflow-x-auto rounded-lg border border-border/40">
                <table className="w-full text-left text-sm">
                  <thead className="bg-muted/40 text-xs font-medium text-muted-foreground border-b border-border/40">
                    <tr>
                      <th className="px-4 py-3">Version Tag</th>
                      <th className="px-4 py-3">Algorithm</th>
                      <th className="px-4 py-3">Training Samples</th>
                      <th className="px-4 py-3">Cutoff Applied</th>
                      <th className="px-4 py-3">Status</th>
                      <th className="px-4 py-3 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/20 text-xs">
                    {modelVersions.map((mv) => (
                      <tr key={mv.id} className="hover:bg-muted/20 transition-colors">
                        <td className="px-4 py-3 font-mono font-medium text-foreground">
                          {mv.version_tag}
                        </td>
                        <td className="px-4 py-3 text-muted-foreground">{mv.algorithm_name}</td>
                        <td className="px-4 py-3 font-mono">
                          {mv.training_sample_count} (Pos: {mv.positive_sample_count}, Neg:{' '}
                          {mv.negative_sample_count})
                        </td>
                        <td className="px-4 py-3 text-muted-foreground">
                          {new Date(mv.training_cutoff_date).toLocaleDateString()}
                        </td>
                        <td className="px-4 py-3">
                          {mv.is_active ? (
                            <span className="px-2 py-0.5 rounded text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                              Active Production
                            </span>
                          ) : (
                            <span className="px-2 py-0.5 rounded text-xs bg-secondary text-muted-foreground">
                              {mv.model_status}
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-right">
                          {!mv.is_active && (
                            <button
                              onClick={() => activateMutation.mutate(mv.id)}
                              disabled={activateMutation.isPending}
                              className="text-xs text-primary hover:underline font-medium"
                            >
                              Activate
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* --------------------------------------------------------------------- */}
      {/* Train Model Modal */}
      {/* --------------------------------------------------------------------- */}
      {isTrainModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-xl border border-border bg-card p-6 shadow-xl space-y-4">
            <h3 className="text-lg font-bold text-foreground">Train / Calibrate Risk Model</h3>
            <p className="text-xs text-muted-foreground">
              Select algorithm architecture. If dataset readiness criteria are not met, the system will
              automatically fall back to transparent deterministic rules.
            </p>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-muted-foreground mb-1 font-medium">Model Architecture</label>
                <select
                  value={trainModelType}
                  onChange={(e) => setTrainModelType(e.target.value as RiskModelType)}
                  className="w-full h-9 px-3 rounded-md bg-secondary border border-border text-sm"
                >
                  <option value="LOGISTIC_REGRESSION">Logistic Regression (L2 Regularized)</option>
                  <option value="DECISION_TREE">Decision Tree (Depth Limited)</option>
                  <option value="DETERMINISTIC_RULES">Deterministic Rule Baseline</option>
                </select>
              </div>

              <div>
                <label className="block text-muted-foreground mb-1 font-medium">Version Tag</label>
                <input
                  type="text"
                  placeholder="e.g. logreg-v1.2-fall2026"
                  value={trainVersionTag}
                  onChange={(e) => setTrainVersionTag(e.target.value)}
                  className="w-full h-9 px-3 rounded-md bg-secondary border border-border text-sm font-mono"
                />
              </div>
            </div>

            <div className="pt-2 flex justify-end gap-2">
              <button
                onClick={() => setIsTrainModalOpen(false)}
                className="px-4 py-2 rounded-md text-xs font-medium text-muted-foreground hover:bg-secondary"
              >
                Cancel
              </button>
              <button
                onClick={() => trainMutation.mutate()}
                disabled={trainMutation.isPending}
                className="px-4 py-2 rounded-md text-xs font-medium bg-primary text-primary-foreground hover:bg-primary/90"
              >
                {trainMutation.isPending ? 'Training...' : 'Initiate Training'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
