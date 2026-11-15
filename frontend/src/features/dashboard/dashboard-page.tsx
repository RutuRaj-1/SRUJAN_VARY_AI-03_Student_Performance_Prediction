import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  BookOpen,
  Award,
  AlertTriangle,
  CheckCircle2,
  ArrowRight,
  Briefcase,
  RefreshCw,
  Lock,
} from 'lucide-react';

import { useAuth } from '@/context/auth-context';
import { useDemo } from '@/demo/demo-context';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  dashboardService,
  StudentOverviewResponse,
  FacultyOverviewResponse,
  InstitutionOverviewResponse,
  PlacementOverviewResponse,
} from '@/services/dashboard-service';

export const DashboardPage: React.FC = () => {
  const { role: authRole } = useAuth();
  const { isDemoMode, activeRole } = useDemo();

  // Effective role: Demo role takes precedence in demo mode
  const effectiveRole = isDemoMode ? activeRole : (authRole || 'STUDENT');

  return (
    <div className="space-y-6">
      {/* Render Role View based on selected perspective */}
      {effectiveRole === 'STUDENT' && <StudentDashboardView />}
      {effectiveRole === 'FACULTY' && <FacultyDashboardView />}
      {effectiveRole === 'INSTITUTION_ADMIN' && <InstitutionDashboardView />}
      {effectiveRole === 'PLACEMENT_OFFICER' && <PlacementDashboardView />}
      {effectiveRole === 'SUPER_ADMIN' && <SuperAdminDashboardView />}
    </div>
  );
};

// =========================================================================
// 1. Student Dashboard View
// =========================================================================

const StudentDashboardView: React.FC = () => {
  const {
    isDemoMode,
    activeScenario,
    currentStudent,
    currentMastery,
    currentRisk,
    currentInterventions,
    currentCareer,
    institution,
  } = useDemo();

  const { data: liveData, isLoading } = useQuery({
    queryKey: ['student-dashboard-overview'],
    queryFn: () => dashboardService.getStudentOverview(),
    staleTime: 30000,
    enabled: !isDemoMode,
    retry: 1,
  });

  // Construct synthetic fallback response for demo mode
  const demoData: StudentOverviewResponse = {
    student_profile: {
      id: currentStudent.id,
      full_name: `${currentStudent.first_name} ${currentStudent.last_name}`,
      enrollment_number: currentStudent.enrollment_number,
      program_name: 'B.Tech Computer Science & Engineering',
      department: currentStudent.department,
      current_semester: currentStudent.current_semester,
      institution_name: institution.name,
      academic_status: currentStudent.academic_status,
    },
    academic_performance: {
      average_marks:
        activeScenario === 'A'
          ? 92.4
          : activeScenario === 'B'
          ? 76.5
          : activeScenario === 'C'
          ? 48.0
          : null,
      attendance_rate: currentStudent.attendance_rate,
      total_records: 14,
      verified_records_count: activeScenario === 'D' ? 6 : 14,
      pending_records_count: 0,
      enrolled_subjects_count: 6,
      freshness: {
        source_module: 'Module 01: Academic Data Hub',
        freshness_status: 'FRESH',
        is_snapshot: false,
      },
    },
    mastery_summary: {
      topics_assessed_count: 6,
      topics_demonstrated_count: currentMastery.filter(
        (m) => m.mastery_state === 'MASTERED'
      ).length,
      topics_developing_count: currentMastery.filter(
        (m) => m.mastery_state === 'PROGRESSING'
      ).length,
      topics_insufficient_evidence_count: currentMastery.filter(
        (m) => m.mastery_state === 'INSUFFICIENT_EVIDENCE'
      ).length,
      clo_attainment_pct:
        activeScenario === 'A'
          ? 84.0
          : activeScenario === 'B'
          ? 71.5
          : activeScenario === 'C'
          ? 44.0
          : null,
      active_learning_gaps_count: currentMastery.filter(
        (m) => m.mastery_state === 'NEEDS_ATTENTION'
      ).length,
      freshness: {
        source_module: 'Module 04: Mastery Analytics',
        freshness_status: 'FRESH',
        is_snapshot: false,
      },
    },
    risk_summary: {
      has_prediction: currentRisk.risk_classification !== 'INSUFFICIENT_EVIDENCE',
      risk_classification: currentRisk.risk_classification,
      risk_probability:
        currentRisk.risk_probability !== null
          ? Math.round(currentRisk.risk_probability * 100)
          : null,
      prediction_horizon: currentRisk.prediction_cutoff,
      primary_adverse_factors: currentRisk.adverse_factors.map(
        (f) => f.factor_name
      ),
      protective_factors: currentRisk.protective_factors.map(
        (f) => f.factor_name
      ),
      prediction_timestamp: new Date().toISOString(),
      model_version: 'v1.4-baseline',
      disclaimer: 'Observational early support indicator. Not an institutional label.',
      freshness: {
        source_module: 'Module 05: Academic Risk Engine',
        freshness_status: 'FRESH',
        is_snapshot: false,
      },
    },
    intervention_summary: {
      active_plans_count: currentInterventions.filter(
        (p) => p.lifecycle_status === 'ACTIVE' || p.lifecycle_status === 'APPROVED'
      ).length,
      pending_actions_count: currentInterventions.reduce(
        (acc, p) => acc + p.action_items.filter((a) => !a.completed).length,
        0
      ),
      completed_actions_count: currentInterventions.reduce(
        (acc, p) => acc + p.action_items.filter((a) => a.completed).length,
        0
      ),
      latest_plan_title: currentInterventions[0]?.title || 'No active support plan',
      faculty_mentor_name: currentInterventions[0]?.faculty_advisor || 'Dr. Sarah Vance',
      freshness: {
        source_module: 'Module 06: Personalized Intervention',
        freshness_status: 'FRESH',
        is_snapshot: false,
      },
    },
    career_summary: {
      analyzed_roles_count: 4,
      target_role_title: currentCareer.role_title,
      core_coverage_pct: currentCareer.core_competency_coverage,
      practical_coverage_pct: currentCareer.practical_project_coverage,
      alignment_status: currentCareer.alignment_status,
      verified_projects_count: currentCareer.verified_projects.filter(
        (p) => p.verified_by_faculty
      ).length,
      pending_projects_count: currentCareer.verified_projects.filter(
        (p) => !p.verified_by_faculty
      ).length,
      active_skill_gaps_count: currentCareer.skill_gaps.length,
      freshness: {
        source_module: 'Module 07: Career Readiness',
        freshness_status: 'FRESH',
        is_snapshot: false,
      },
    },
    system_freshness: new Date().toISOString(),
  };

  const data = isDemoMode || !liveData ? demoData : liveData;

  if (isLoading && !isDemoMode) {
    return (
      <div className="p-12 text-center space-y-3">
        <RefreshCw className="h-8 w-8 animate-spin mx-auto text-[#237277]" />
        <p className="text-sm text-[#40524E] font-medium">
          Aggregating cross-module intelligence...
        </p>
      </div>
    );
  }

  const {
    student_profile,
    academic_performance,
    mastery_summary,
    risk_summary,
    intervention_summary,
    career_summary,
  } = data;

  return (
    <div className="space-y-6">
      {/* Student Profile Header */}
      <div className="bg-[#123E40] text-white rounded-[6px] p-6 shadow-subtle border border-[#18575A]">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded-[3px] bg-[#EEF8F7] text-[#123E40] font-mono text-xs font-bold">
                {student_profile.enrollment_number}
              </span>
              <span className="px-2 py-0.5 rounded-[3px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-medium">
                {student_profile.academic_status}
              </span>
              {isDemoMode && (
                <span className="px-2 py-0.5 rounded-[3px] bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[11px] font-mono">
                  Scenario {activeScenario} Active
                </span>
              )}
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-white font-sans">
              {student_profile.full_name}
            </h1>
            <p className="text-xs text-slate-300">
              {student_profile.program_name} • Semester {student_profile.current_semester} • {student_profile.department}
            </p>
          </div>
          <div className="text-right">
            <span className="text-xs text-[#BDCEC8] block font-mono">
              {student_profile.institution_name}
            </span>
            <span className="text-[11px] text-slate-400 block mt-1">
              Evidence Freshness: Real-time Synchronized
            </span>
          </div>
        </div>
      </div>

      {/* 5 Core Intelligence Dimension Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {/* Dimension 1: Academic Performance */}
        <Card>
          <CardHeader className="pb-3 border-b border-[#DCE6E2] flex flex-row items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-[#EEF8F7] text-[#237277] rounded-[4px]">
                <BookOpen className="h-4 w-4" />
              </div>
              <CardTitle className="text-sm font-semibold">Academic Records</CardTitle>
            </div>
            <span className="text-[10px] text-[#687A75] font-mono bg-[#F7FAF9] px-1.5 py-0.5 rounded border border-[#DCE6E2]">
              Module 01
            </span>
          </CardHeader>
          <CardContent className="pt-4 space-y-4">
            <div className="grid grid-cols-2 gap-3 text-center">
              <div className="bg-[#F7FAF9] p-2.5 rounded-[4px] border border-[#DCE6E2]">
                <span className="text-xs text-[#687A75] block">Continuous Avg</span>
                <span className="text-xl font-bold text-[#172825] tabular-nums">
                  {academic_performance.average_marks !== null
                    ? `${academic_performance.average_marks}%`
                    : 'N/A (Excused)'}
                </span>
              </div>
              <div className="bg-[#F7FAF9] p-2.5 rounded-[4px] border border-[#DCE6E2]">
                <span className="text-xs text-[#687A75] block">Attendance</span>
                <span className="text-xl font-bold text-[#172825] tabular-nums">
                  {academic_performance.attendance_rate !== null
                    ? `${academic_performance.attendance_rate}%`
                    : 'N/A'}
                </span>
              </div>
            </div>
            <div className="text-xs text-[#40524E] space-y-1">
              <div className="flex justify-between">
                <span>Verified Records:</span>
                <span className="font-semibold text-[#172825]">
                  {academic_performance.verified_records_count} / {academic_performance.total_records}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Enrolled Subjects:</span>
                <span className="font-semibold text-[#172825]">
                  {academic_performance.enrolled_subjects_count} Courses
                </span>
              </div>
            </div>
            <div className="pt-2 border-t border-[#DCE6E2] flex items-center justify-between text-[11px] text-[#687A75]">
              <span className="truncate">{academic_performance.freshness.source_module}</span>
              <Link to="/app/academic-data" className="text-[#237277] hover:underline flex items-center gap-1 font-medium">
                Ledger <ArrowRight className="h-3 w-3" />
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Dimension 2: Learning Mastery */}
        <Card>
          <CardHeader className="pb-3 border-b border-[#DCE6E2] flex flex-row items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-[#EEF8F7] text-[#237277] rounded-[4px]">
                <Award className="h-4 w-4" />
              </div>
              <CardTitle className="text-sm font-semibold">Topic Mastery</CardTitle>
            </div>
            <span className="text-[10px] text-[#687A75] font-mono bg-[#F7FAF9] px-1.5 py-0.5 rounded border border-[#DCE6E2]">
              Module 04
            </span>
          </CardHeader>
          <CardContent className="pt-4 space-y-4">
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs text-[#40524E]">
                <span>Demonstrated Understanding:</span>
                <span className="font-bold text-[#172825]">
                  {mastery_summary.topics_demonstrated_count} / {mastery_summary.topics_assessed_count} Topics
                </span>
              </div>
              <div className="w-full bg-[#EFF5F3] rounded-[2px] h-2 overflow-hidden flex">
                <div
                  className="bg-[#169C73] h-2"
                  style={{
                    width: `${
                      mastery_summary.topics_assessed_count
                        ? (mastery_summary.topics_demonstrated_count / mastery_summary.topics_assessed_count) * 100
                        : 0
                    }%`,
                  }}
                />
                <div
                  className="bg-[#D89B22] h-2"
                  style={{
                    width: `${
                      mastery_summary.topics_assessed_count
                        ? (mastery_summary.topics_developing_count / mastery_summary.topics_assessed_count) * 100
                        : 0
                    }%`,
                  }}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs text-[#40524E]">
              <div className="bg-[#F7FAF9] p-2 rounded-[4px] border border-[#DCE6E2]">
                <span className="text-[11px] text-[#687A75] block">CLO Attainment</span>
                <span className="font-semibold text-[#172825] tabular-nums">
                  {mastery_summary.clo_attainment_pct !== null ? `${mastery_summary.clo_attainment_pct}%` : 'Pending Evidence'}
                </span>
              </div>
              <div className="bg-[#F7FAF9] p-2 rounded-[4px] border border-[#DCE6E2]">
                <span className="text-[11px] text-[#687A75] block">Open Deficits</span>
                <span className="font-semibold text-rose-700">{mastery_summary.active_learning_gaps_count} Flagged</span>
              </div>
            </div>
            <div className="pt-2 border-t border-[#DCE6E2] flex items-center justify-between text-[11px] text-[#687A75]">
              <span>Topic-Level Evidence</span>
              <Link to="/app/mastery" className="text-[#237277] hover:underline flex items-center gap-1 font-medium">
                Mastery Radar <ArrowRight className="h-3 w-3" />
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Dimension 3: Explainable Academic Risk */}
        <Card>
          <CardHeader className="pb-3 border-b border-[#DCE6E2] flex flex-row items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-amber-50 text-amber-700 rounded-[4px]">
                <AlertTriangle className="h-4 w-4" />
              </div>
              <CardTitle className="text-sm font-semibold">Academic Risk Horizon</CardTitle>
            </div>
            <span className="text-[10px] text-[#687A75] font-mono bg-[#F7FAF9] px-1.5 py-0.5 rounded border border-[#DCE6E2]">
              Module 05
            </span>
          </CardHeader>
          <CardContent className="pt-4 space-y-3">
            {risk_summary.has_prediction ? (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-[#40524E]">Risk Classification:</span>
                  <Badge
                    variant={
                      risk_summary.risk_classification === 'LOW'
                        ? 'success'
                        : risk_summary.risk_classification === 'MODERATE'
                        ? 'warning'
                        : 'error'
                    }
                  >
                    {risk_summary.risk_classification} RISK ({risk_summary.risk_probability}%)
                  </Badge>
                </div>
                {risk_summary.primary_adverse_factors.length > 0 && (
                  <div className="space-y-1">
                    <span className="text-[11px] font-semibold text-[#687A75] block uppercase">
                      Primary Adverse Factor:
                    </span>
                    <p className="text-xs text-amber-900 bg-amber-50 p-2 rounded-[4px] border border-amber-200">
                      {risk_summary.primary_adverse_factors[0]}
                    </p>
                  </div>
                )}
                <p className="text-[10px] text-[#687A75] italic leading-snug">
                  {risk_summary.disclaimer}
                </p>
              </>
            ) : (
              <div className="p-4 bg-[#F7FAF9] text-center rounded-[4px] border border-[#DCE6E2] text-xs text-[#687A75]">
                {activeScenario === 'D'
                  ? 'INSUFFICIENT EVIDENCE (Excused Absence Gate Active)'
                  : 'No active risk warning.'}
              </div>
            )}
            <div className="pt-2 border-t border-[#DCE6E2] flex items-center justify-between text-[11px] text-[#687A75]">
              <span>Time-Bounded Cutoff</span>
              <Link to="/app/risk" className="text-[#237277] hover:underline flex items-center gap-1 font-medium">
                Risk Engine <ArrowRight className="h-3 w-3" />
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Dimension 4: Personalized Academic Interventions */}
        <Card>
          <CardHeader className="pb-3 border-b border-[#DCE6E2] flex flex-row items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-[#EEF8F7] text-[#237277] rounded-[4px]">
                <CheckCircle2 className="h-4 w-4" />
              </div>
              <CardTitle className="text-sm font-semibold">Supervised Interventions</CardTitle>
            </div>
            <span className="text-[10px] text-[#687A75] font-mono bg-[#F7FAF9] px-1.5 py-0.5 rounded border border-[#DCE6E2]">
              Module 06
            </span>
          </CardHeader>
          <CardContent className="pt-4 space-y-3">
            <div className="bg-[#F7FAF9] p-3 rounded-[4px] border border-[#DCE6E2] space-y-1">
              <span className="text-[11px] text-[#687A75] block font-medium">Active Support Plan:</span>
              <span className="text-xs font-bold text-[#172825] line-clamp-1">
                {intervention_summary.latest_plan_title}
              </span>
              <span className="text-[11px] text-[#237277] block">
                Supervisor: {intervention_summary.faculty_mentor_name}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-center text-xs">
              <div className="p-2 bg-[#F7FAF9] rounded-[4px] border border-[#DCE6E2]">
                <span className="text-[11px] text-[#687A75] block">Completed Actions</span>
                <span className="font-bold text-[#169C73]">{intervention_summary.completed_actions_count}</span>
              </div>
              <div className="p-2 bg-[#F7FAF9] rounded-[4px] border border-[#DCE6E2]">
                <span className="text-[11px] text-[#687A75] block">Pending Milestones</span>
                <span className="font-bold text-amber-700">{intervention_summary.pending_actions_count}</span>
              </div>
            </div>
            <div className="pt-2 border-t border-[#DCE6E2] flex items-center justify-between text-[11px] text-[#687A75]">
              <span>Faculty Supervised</span>
              <Link to="/app/interventions" className="text-[#237277] hover:underline flex items-center gap-1 font-medium">
                Action Plan <ArrowRight className="h-3 w-3" />
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Dimension 5: Career Readiness */}
        <Card className="md:col-span-2">
          <CardHeader className="pb-3 border-b border-[#DCE6E2] flex flex-row items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-[#EEF8F7] text-[#237277] rounded-[4px]">
                <Briefcase className="h-4 w-4" />
              </div>
              <CardTitle className="text-sm font-semibold">Career Readiness & Practical Alignment</CardTitle>
            </div>
            <span className="text-[10px] text-[#687A75] font-mono bg-[#F7FAF9] px-1.5 py-0.5 rounded border border-[#DCE6E2]">
              Module 07
            </span>
          </CardHeader>
          <CardContent className="pt-4 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-[#EEF8F7] p-3 rounded-[4px] border border-[#BDCEC8]">
              <div>
                <span className="text-xs text-[#123E40] block font-medium">Target Industry Role:</span>
                <span className="text-base font-bold text-[#172825]">
                  {career_summary.target_role_title}
                </span>
              </div>
              <Badge variant="brand" className="self-start sm:self-auto text-xs">
                {career_summary.alignment_status?.replace('_', ' ')}
              </Badge>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1">
                <div className="flex justify-between text-xs text-[#40524E]">
                  <span>Core Academic Competency Coverage:</span>
                  <span className="font-bold text-[#172825]">{career_summary.core_coverage_pct ?? 0}%</span>
                </div>
                <div className="w-full bg-[#EFF5F3] rounded-[2px] h-2 overflow-hidden">
                  <div className="bg-[#237277] h-2" style={{ width: `${career_summary.core_coverage_pct ?? 0}%` }} />
                </div>
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-xs text-[#40524E]">
                  <span>Practical Project Portfolio Evidence:</span>
                  <span className="font-bold text-[#172825]">{career_summary.practical_coverage_pct ?? 0}%</span>
                </div>
                <div className="w-full bg-[#EFF5F3] rounded-[2px] h-2 overflow-hidden">
                  <div className="bg-[#169C73] h-2" style={{ width: `${career_summary.practical_coverage_pct ?? 0}%` }} />
                </div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2 text-center text-xs">
              <div className="p-2 bg-[#F7FAF9] rounded-[4px] border border-[#DCE6E2]">
                <span className="text-[11px] text-[#687A75] block">Verified Projects</span>
                <span className="font-semibold text-emerald-700">{career_summary.verified_projects_count}</span>
              </div>
              <div className="p-2 bg-[#F7FAF9] rounded-[4px] border border-[#DCE6E2]">
                <span className="text-[11px] text-[#687A75] block">Pending Review</span>
                <span className="font-semibold text-amber-700">{career_summary.pending_projects_count}</span>
              </div>
              <div className="p-2 bg-[#F7FAF9] rounded-[4px] border border-[#DCE6E2]">
                <span className="text-[11px] text-[#687A75] block">Skill Deficits</span>
                <span className="font-semibold text-[#172825]">{career_summary.active_skill_gaps_count} Gaps</span>
              </div>
            </div>

            <div className="pt-2 border-t border-[#DCE6E2] flex items-center justify-between text-[11px] text-[#687A75]">
              <span>Verified Portfolio Evidence</span>
              <Link to="/app/career-readiness" className="text-[#237277] hover:underline flex items-center gap-1 font-medium">
                Role Skill Radar <ArrowRight className="h-3 w-3" />
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// =========================================================================
// 2. Faculty Dashboard View
// =========================================================================

const FacultyDashboardView: React.FC = () => {
  const { isDemoMode, subjects, faculty, dashboardData, institution } = useDemo();

  const { data: liveData, isLoading } = useQuery({
    queryKey: ['faculty-dashboard-overview'],
    queryFn: () => dashboardService.getFacultyOverview(),
    staleTime: 30000,
    enabled: !isDemoMode,
  });

  const demoData: FacultyOverviewResponse = {
    faculty_name: faculty[0].name,
    department: faculty[0].department,
    institution_name: institution.name,
    total_students_monitored: dashboardData.total_students,
    verification_queue: {
      pending_academic_records: 3,
      pending_interventions_review: 2,
      pending_practical_projects: 4,
    },
    cohort_risk_overview: {
      high_risk_students_count: dashboardData.risk_distribution.high,
      moderate_risk_students_count: dashboardData.risk_distribution.moderate,
      low_risk_students_count: dashboardData.risk_distribution.low,
      active_interventions_count: dashboardData.active_interventions_count,
      learning_gaps_flagged_count: 5,
    },
    assigned_subjects: subjects.slice(0, 3).map((s) => ({
      subject_id: s.id,
      code: s.code,
      name: s.name,
      semester: s.semester,
      enrolled_students_count: 24,
      average_attendance: 84.5,
      average_marks: 78.2,
    })),
    freshness: {
      source_module: 'Module 01: Academic Data Hub',
      freshness_status: 'FRESH',
      is_snapshot: false,
    },
  };

  const data = isDemoMode || !liveData ? demoData : liveData;
  const { verification_queue, cohort_risk_overview, assigned_subjects } = data;

  if (isLoading && !isDemoMode) {
    return (
      <div className="p-12 text-center space-y-3">
        <RefreshCw className="h-8 w-8 animate-spin mx-auto text-[#237277]" />
        <p className="text-sm text-[#40524E]">Loading faculty academic queue...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Faculty Profile Banner */}
      <div className="bg-[#123E40] text-white rounded-[6px] p-6 shadow-subtle border border-[#18575A]">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <span className="px-2 py-0.5 rounded-[3px] bg-[#EEF8F7] text-[#123E40] text-xs font-mono font-bold">
              FACULTY INTELLIGENCE WORKSPACE
            </span>
            <h1 className="text-2xl font-bold tracking-tight text-white mt-1 font-sans">{data.faculty_name}</h1>
            <p className="text-xs text-slate-300">
              Department of {data.department} • {data.institution_name}
            </p>
          </div>
          <div className="text-right">
            <span className="text-xs text-[#BDCEC8] block font-mono">Academic Year 2025-2026</span>
            <span className="text-[11px] text-slate-400 block mt-1">Supervisory Privileges Active</span>
          </div>
        </div>
      </div>

      {/* Verification Queue & Risk Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <Card className="border-l-4 border-l-[#237277]">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <span className="text-xs text-[#687A75] block font-medium">Pending Marks Verification</span>
              <span className="text-2xl font-bold text-[#172825]">{verification_queue.pending_academic_records}</span>
            </div>
            <Link to="/app/academic-data">
              <Button variant="outline" size="sm" className="text-xs border-[#BDCEC8]">
                Verify Ledgers
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-amber-500">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <span className="text-xs text-[#687A75] block font-medium">Support Plans Pending Review</span>
              <span className="text-2xl font-bold text-amber-700">{verification_queue.pending_interventions_review}</span>
            </div>
            <Link to="/app/interventions">
              <Button variant="outline" size="sm" className="text-xs border-[#BDCEC8]">
                Review Plans
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-purple-500">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <span className="text-xs text-[#687A75] block font-medium">Project Portfolios for Review</span>
              <span className="text-2xl font-bold text-purple-700">{verification_queue.pending_practical_projects}</span>
            </div>
            <Link to="/app/career-readiness">
              <Button variant="outline" size="sm" className="text-xs border-[#BDCEC8]">
                Review Projects
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Cohort Risk Breakdown Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-rose-50 border border-rose-200 rounded-[4px] p-3 text-center">
          <span className="text-xs text-rose-800 block font-medium">High Risk Students</span>
          <span className="text-2xl font-bold text-rose-900">{cohort_risk_overview.high_risk_students_count}</span>
        </div>
        <div className="bg-amber-50 border border-amber-200 rounded-[4px] p-3 text-center">
          <span className="text-xs text-amber-800 block font-medium">Moderate Risk</span>
          <span className="text-2xl font-bold text-amber-900">{cohort_risk_overview.moderate_risk_students_count}</span>
        </div>
        <div className="bg-[#EEF8F7] border border-[#BDCEC8] rounded-[4px] p-3 text-center">
          <span className="text-xs text-[#123E40] block font-medium">Active Support Plans</span>
          <span className="text-2xl font-bold text-[#123E40]">{cohort_risk_overview.active_interventions_count}</span>
        </div>
        <div className="bg-[#F7FAF9] border border-[#DCE6E2] rounded-[4px] p-3 text-center">
          <span className="text-xs text-[#687A75] block font-medium">Flagged Topic Gaps</span>
          <span className="text-2xl font-bold text-[#172825]">{cohort_risk_overview.learning_gaps_flagged_count}</span>
        </div>
      </div>

      {/* Assigned Subjects Table */}
      <Card>
        <CardHeader className="pb-3 border-b border-[#DCE6E2]">
          <CardTitle className="text-sm font-semibold">Assigned Subjects & Performance Health</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-[#EEF8F7] text-[#123E40] border-b border-[#DCE6E2] font-semibold">
                <tr>
                  <th className="py-2.5 px-4 font-mono">Code</th>
                  <th className="py-2.5 px-4">Subject Name</th>
                  <th className="py-2.5 px-4">Semester</th>
                  <th className="py-2.5 px-4">Students</th>
                  <th className="py-2.5 px-4">Avg Attendance</th>
                  <th className="py-2.5 px-4">Continuous Avg</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#DCE6E2]">
                {assigned_subjects.map((s) => (
                  <tr key={s.subject_id} className="hover:bg-[#F7FAF9]">
                    <td className="py-2.5 px-4 font-mono font-medium text-[#237277]">{s.code}</td>
                    <td className="py-2.5 px-4 font-semibold text-[#172825]">{s.name}</td>
                    <td className="py-2.5 px-4 text-[#40524E]">Sem {s.semester}</td>
                    <td className="py-2.5 px-4 text-[#40524E]">{s.enrolled_students_count}</td>
                    <td className="py-2.5 px-4 font-medium text-[#172825] tabular-nums">
                      {s.average_attendance !== null ? `${s.average_attendance}%` : 'N/A'}
                    </td>
                    <td className="py-2.5 px-4 font-medium text-[#172825] tabular-nums">
                      {s.average_marks !== null ? `${s.average_marks}%` : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// =========================================================================
// 3. Institution Admin Dashboard View
// =========================================================================

const InstitutionDashboardView: React.FC = () => {
  const { isDemoMode, dashboardData, institution } = useDemo();

  const { data: liveData } = useQuery({
    queryKey: ['institution-dashboard-overview'],
    queryFn: () => dashboardService.getInstitutionOverview(),
    staleTime: 30000,
    enabled: !isDemoMode,
  });

  const demoData: InstitutionOverviewResponse = {
    institution_id: institution.id,
    institution_name: institution.name,
    institution_code: institution.code,
    summary_counts: {
      total_active_students: dashboardData.total_students,
      total_faculty: 5,
      total_programs: 2,
      total_subjects: 6,
    },
    academic_data_status: {
      total_academic_records: 120,
      verified_records_pct: 95.8,
      data_quality_findings_count: 2,
    },
    mastery_overview: {
      mastery_demonstrated_pct: 78.4,
      mastery_developing_pct: 16.2,
      insufficient_evidence_pct: 5.4,
      total_evaluated_topics: 48,
    },
    risk_distribution: {
      high_risk_count: dashboardData.risk_distribution.high,
      medium_risk_count: dashboardData.risk_distribution.moderate,
      low_risk_count: dashboardData.risk_distribution.low,
      unscreened_count: 2,
    },
    intervention_metrics: {
      active_plans_count: dashboardData.active_interventions_count,
      completed_plans_count: 8,
      pending_review_count: 2,
    },
    career_readiness_overview: {
      students_evaluated_count: 24,
      ready_students_count: 14,
      approaching_students_count: 6,
      developing_students_count: 4,
      verified_projects_total: 18,
    },
    freshness: {
      source_module: 'Unified Aggregator',
      freshness_status: 'FRESH',
      is_snapshot: false,
    },
  };

  const data = isDemoMode || !liveData ? demoData : liveData;
  const {
    summary_counts,
    academic_data_status,
    mastery_overview,
    risk_distribution,
    career_readiness_overview,
  } = data;

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="bg-[#123E40] text-white rounded-[6px] p-6 shadow-subtle border border-[#18575A]">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <span className="px-2 py-0.5 rounded-[3px] bg-[#EEF8F7] text-[#123E40] text-xs font-mono font-bold">
              INSTITUTIONAL INTELLIGENCE
            </span>
            <h1 className="text-2xl font-bold tracking-tight text-white mt-1 font-sans">{data.institution_name}</h1>
            <p className="text-xs text-slate-300">Code: {data.institution_code} • Multi-Tenant Isolation Active</p>
          </div>
          <div className="text-right">
            <span className="text-xs text-[#BDCEC8] block font-mono">Academic Year 2025-2026</span>
            <span className="text-[11px] text-slate-400 block mt-1">Tenant Status: Operational</span>
          </div>
        </div>
      </div>

      {/* Summary Counts Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <Card className="text-center p-4">
          <span className="text-xs text-[#687A75] block">Active Cohort</span>
          <span className="text-2xl font-bold text-[#172825]">{summary_counts.total_active_students} Students</span>
        </Card>
        <Card className="text-center p-4">
          <span className="text-xs text-[#687A75] block">Faculty Members</span>
          <span className="text-2xl font-bold text-[#172825]">{summary_counts.total_faculty}</span>
        </Card>
        <Card className="text-center p-4">
          <span className="text-xs text-[#687A75] block">Degree Programs</span>
          <span className="text-2xl font-bold text-[#172825]">{summary_counts.total_programs}</span>
        </Card>
        <Card className="text-center p-4">
          <span className="text-xs text-[#687A75] block">Academic Subjects</span>
          <span className="text-2xl font-bold text-[#172825]">{summary_counts.total_subjects}</span>
        </Card>
      </div>

      {/* 4 Quadrants: Academic Data, Mastery, Risk, Career */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <Card>
          <CardHeader className="pb-3 border-b border-[#DCE6E2]">
            <CardTitle className="text-sm font-semibold">Academic Data Health (Module 01)</CardTitle>
          </CardHeader>
          <CardContent className="pt-4 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-[#687A75]">Total Academic Records:</span>
              <span className="font-semibold text-[#172825]">{academic_data_status.total_academic_records}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#687A75]">Verification Rate:</span>
              <span className="font-semibold text-[#169C73]">{academic_data_status.verified_records_pct}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#687A75]">Open Data Quality Findings:</span>
              <span className="font-semibold text-amber-700">{academic_data_status.data_quality_findings_count}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3 border-b border-[#DCE6E2]">
            <CardTitle className="text-sm font-semibold">Mastery Distribution (Module 04)</CardTitle>
          </CardHeader>
          <CardContent className="pt-4 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-[#687A75]">Demonstrated Mastery:</span>
              <span className="font-semibold text-[#169C73]">{mastery_overview.mastery_demonstrated_pct}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#687A75]">Developing Mastery:</span>
              <span className="font-semibold text-amber-700">{mastery_overview.mastery_developing_pct}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#687A75]">Insufficient Assessment Evidence:</span>
              <span className="font-semibold text-[#687A75]">{mastery_overview.insufficient_evidence_pct}%</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3 border-b border-[#DCE6E2]">
            <CardTitle className="text-sm font-semibold">Academic Risk Screening (Module 05)</CardTitle>
          </CardHeader>
          <CardContent className="pt-4 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-[#687A75]">High Risk Students:</span>
              <span className="font-semibold text-rose-700">{risk_distribution.high_risk_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#687A75]">Moderate Risk Students:</span>
              <span className="font-semibold text-amber-700">{risk_distribution.medium_risk_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#687A75]">Low Risk Students:</span>
              <span className="font-semibold text-[#169C73]">{risk_distribution.low_risk_count}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3 border-b border-[#DCE6E2]">
            <CardTitle className="text-sm font-semibold">Career Readiness & Projects (Module 07)</CardTitle>
          </CardHeader>
          <CardContent className="pt-4 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-[#687A75]">Evaluated Students:</span>
              <span className="font-semibold text-[#172825]">{career_readiness_overview.students_evaluated_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#687A75]">Industry Aligned Students:</span>
              <span className="font-semibold text-[#169C73]">{career_readiness_overview.ready_students_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#687A75]">Verified Practical Projects:</span>
              <span className="font-semibold text-purple-700">{career_readiness_overview.verified_projects_total}</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// =========================================================================
// 4. Placement Officer Dashboard View (Firewalled from Risk & Interventions)
// =========================================================================

const PlacementDashboardView: React.FC = () => {
  const { isDemoMode } = useDemo();

  const { data: liveData } = useQuery({
    queryKey: ['placement-dashboard-overview'],
    queryFn: () => dashboardService.getPlacementOverview(),
    staleTime: 30000,
    enabled: !isDemoMode,
  });

  const demoData: PlacementOverviewResponse = {
    institution_name: 'VARY Institute of Technology',
    active_role_profiles_count: 4,
    total_evaluated_students: 24,
    readiness_distribution: {
      ready_count: 14,
      approaching_count: 6,
      developing_count: 4,
      emerging_or_unassessed_count: 0,
    },
    project_verification_summary: {
      verified_projects_count: 18,
      pending_verification_count: 4,
    },
    top_industry_skill_gaps: [
      {
        competency_name: 'Distributed Concurrency & Locks',
        gap_type: 'PRACTICAL_APPLICATION',
        affected_students_count: 7,
      },
      {
        competency_name: 'Database Indexing Optimization',
        gap_type: 'CORE_FOUNDATION',
        affected_students_count: 5,
      },
      {
        competency_name: 'OpenTelemetry Distributed Tracing',
        gap_type: 'PRACTICAL_APPLICATION',
        affected_students_count: 8,
      },
    ],
    freshness: {
      source_module: 'Module 07: Career Readiness',
      freshness_status: 'FRESH',
      is_snapshot: false,
    },
  };

  const data = isDemoMode || !liveData ? demoData : liveData;
  const { readiness_distribution, project_verification_summary, top_industry_skill_gaps } = data;

  return (
    <div className="space-y-6">
      {/* Firewall Notice Banner */}
      <div className="bg-[#123E40] text-white rounded-[6px] p-5 shadow-subtle border border-[#18575A] flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-xs text-[#D9F0EE] font-semibold uppercase tracking-wider font-mono">
            <Lock className="h-4 w-4 text-[#2D8E92]" />
            <span>Placement Officer Defense-in-Depth Firewall</span>
          </div>
          <h1 className="text-xl font-bold text-white font-sans">Career Readiness & Placement Workspace</h1>
          <p className="text-xs text-slate-300 max-w-2xl">
            This workspace provides verified role readiness, competency evidence, and practical project portfolios.
            Academic risk models (Module 05) and confidential intervention plans (Module 06) are permanently firewalled.
          </p>
        </div>
        <Badge variant="brand" className="text-xs">Privacy Firewall Active</Badge>
      </div>

      {/* Readiness Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="text-center p-4 border-l-4 border-l-[#169C73]">
          <span className="text-xs text-[#687A75] block">Strong Alignment</span>
          <span className="text-2xl font-bold text-[#169C73]">{readiness_distribution.ready_count}</span>
        </Card>
        <Card className="text-center p-4 border-l-4 border-l-[#237277]">
          <span className="text-xs text-[#687A75] block">Partial Alignment</span>
          <span className="text-2xl font-bold text-[#237277]">{readiness_distribution.approaching_count}</span>
        </Card>
        <Card className="text-center p-4 border-l-4 border-l-[#D89B22]">
          <span className="text-xs text-[#687A75] block">Developing Alignment</span>
          <span className="text-2xl font-bold text-amber-700">{readiness_distribution.developing_count}</span>
        </Card>
        <Card className="text-center p-4 border-l-4 border-l-purple-600">
          <span className="text-xs text-[#687A75] block">Verified Projects</span>
          <span className="text-2xl font-bold text-purple-700">{project_verification_summary.verified_projects_count}</span>
        </Card>
      </div>

      {/* Top Industry Skill Gaps */}
      <Card>
        <CardHeader className="pb-3 border-b border-[#DCE6E2] flex flex-row items-center justify-between">
          <CardTitle className="text-sm font-semibold">Top Cohort Industry Skill Gaps</CardTitle>
          <Link to="/app/career-readiness" className="text-xs text-[#237277] hover:underline flex items-center gap-1 font-medium">
            Explore All Roles <ArrowRight className="h-3 w-3" />
          </Link>
        </CardHeader>
        <CardContent className="p-0">
          <div className="divide-y divide-[#DCE6E2]">
            {top_industry_skill_gaps.map((gap, i) => (
              <div key={i} className="p-4 flex items-center justify-between hover:bg-[#F7FAF9]">
                <div>
                  <div className="font-semibold text-xs text-[#172825]">{gap.competency_name}</div>
                  <div className="text-[11px] text-[#687A75] mt-0.5">Tier: {gap.gap_type.replace('_', ' ')}</div>
                </div>
                <Badge variant="warning" className="text-xs">
                  {gap.affected_students_count} Students
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// =========================================================================
// 5. Super Admin Dashboard View
// =========================================================================

const SuperAdminDashboardView: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-[#123E40] text-white rounded-[6px] p-6 shadow-subtle border border-[#18575A]">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <span className="px-2 py-0.5 rounded-[3px] bg-[#EEF8F7] text-[#123E40] text-xs font-mono font-bold">
              PLATFORM GOVERNANCE
            </span>
            <h1 className="text-2xl font-bold tracking-tight text-white mt-1 font-sans">Platform Super Admin Workspace</h1>
            <p className="text-xs text-slate-300">Global multi-tenant governance, model version registries, and security telemetry.</p>
          </div>
        </div>
      </div>
      <InstitutionDashboardView />
    </div>
  );
};
