import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  BookOpen,
  Award,
  AlertTriangle,
  CheckCircle2,
  ArrowRight,
  ShieldCheck,
  Briefcase,
  RefreshCw,
  AlertCircle,
  Lock,
} from 'lucide-react';

import { useAuth } from '@/context/auth-context';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { dashboardService } from '@/services/dashboard-service';
import { UserRole } from '@/types/auth';

export const DashboardPage: React.FC = () => {
  const { role } = useAuth();
  const [activeRoleView, setActiveRoleView] = useState<UserRole>(role || 'STUDENT');

  // Allow Super Admins or Admins to preview other role perspectives
  const canSwitchPerspective = role === 'SUPER_ADMIN' || role === 'INSTITUTION_ADMIN';

  return (
    <div className="space-y-6">
      {/* Role View Switcher (for Admins / Demonstrations) */}
      {canSwitchPerspective && (
        <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-900 text-white p-3 rounded-lg border border-slate-800 shadow-sm text-xs">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
            <span className="font-semibold text-slate-300">Perspective Switcher:</span>
            <span className="text-slate-400">Authenticated as {role}</span>
          </div>
          <div className="flex items-center gap-1.5">
            {(['STUDENT', 'FACULTY', 'INSTITUTION_ADMIN', 'PLACEMENT_OFFICER', 'SUPER_ADMIN'] as UserRole[]).map((r) => (
              <button
                key={r}
                onClick={() => setActiveRoleView(r)}
                className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                  activeRoleView === r
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
              >
                {r.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Render Role View based on selected perspective */}
      {activeRoleView === 'STUDENT' && <StudentDashboardView />}
      {activeRoleView === 'FACULTY' && <FacultyDashboardView />}
      {activeRoleView === 'INSTITUTION_ADMIN' && <InstitutionDashboardView />}
      {activeRoleView === 'PLACEMENT_OFFICER' && <PlacementDashboardView />}
      {activeRoleView === 'SUPER_ADMIN' && <SuperAdminDashboardView />}
    </div>
  );
};

// =========================================================================
// 1. Student Dashboard View
// =========================================================================

const StudentDashboardView: React.FC = () => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['student-dashboard-overview'],
    queryFn: () => dashboardService.getStudentOverview(),
    staleTime: 30000,
  });

  if (isLoading) {
    return (
      <div className="p-12 text-center space-y-3">
        <RefreshCw className="h-8 w-8 animate-spin mx-auto text-blue-600" />
        <p className="text-sm text-slate-600 font-medium">Aggregating cross-module intelligence...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8 bg-red-50 border border-red-200 rounded-lg text-center space-y-3">
        <AlertCircle className="h-8 w-8 text-red-600 mx-auto" />
        <h3 className="text-sm font-semibold text-red-900">Student Profile Not Found</h3>
        <p className="text-xs text-red-700 max-w-md mx-auto">
          No student academic profile is linked to this account, or the academic database records are uninitialized.
        </p>
      </div>
    );
  }

  const { student_profile, academic_performance, mastery_summary, risk_summary, intervention_summary, career_summary } = data;

  return (
    <div className="space-y-6">
      {/* Student Profile Header */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white rounded-xl p-6 shadow-md border border-slate-800">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-indigo-300 border-indigo-700 font-mono text-xs">
                {student_profile.enrollment_number}
              </Badge>
              <Badge className="bg-emerald-600/30 text-emerald-300 border-emerald-600/50 text-xs">
                {student_profile.academic_status}
              </Badge>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-white">{student_profile.full_name}</h1>
            <p className="text-xs text-slate-300">
              {student_profile.program_name} • Semester {student_profile.current_semester} • {student_profile.department}
            </p>
          </div>
          <div className="text-right">
            <span className="text-xs text-slate-400 block font-mono">{student_profile.institution_name}</span>
            <span className="text-[11px] text-slate-400 block mt-1">
              Freshness: {new Date(data.system_freshness).toLocaleTimeString()}
            </span>
          </div>
        </div>
      </div>

      {/* 5 Core Intelligence Dimension Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {/* Dimension 1: Academic Performance */}
        <Card className="hover:border-slate-300 transition-shadow shadow-sm">
          <CardHeader className="pb-3 border-b border-slate-100 flex flex-row items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-blue-50 text-blue-600 rounded-md">
                <BookOpen className="h-4 w-4" />
              </div>
              <CardTitle className="text-sm font-semibold">Academic Records</CardTitle>
            </div>
            <Badge variant="outline" className="text-[10px] text-slate-500 font-mono">
              Module 03
            </Badge>
          </CardHeader>
          <CardContent className="pt-4 space-y-4">
            <div className="grid grid-cols-2 gap-3 text-center">
              <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                <span className="text-xs text-slate-500 block">Verified Average</span>
                <span className="text-xl font-bold text-slate-900">
                  {academic_performance.average_marks !== null ? `${academic_performance.average_marks}%` : 'N/A'}
                </span>
              </div>
              <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                <span className="text-xs text-slate-500 block">Attendance</span>
                <span className="text-xl font-bold text-slate-900">
                  {academic_performance.attendance_rate !== null ? `${academic_performance.attendance_rate}%` : 'N/A'}
                </span>
              </div>
            </div>
            <div className="text-xs text-slate-600 space-y-1">
              <div className="flex justify-between">
                <span>Verified Records:</span>
                <span className="font-semibold">{academic_performance.verified_records_count} / {academic_performance.total_records}</span>
              </div>
              <div className="flex justify-between">
                <span>Enrolled Subjects:</span>
                <span className="font-semibold">{academic_performance.enrolled_subjects_count}</span>
              </div>
            </div>
            <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
              <span className="truncate">{academic_performance.freshness.source_module}</span>
              <Link to="/academic-data" className="text-blue-600 hover:underline flex items-center gap-1 font-medium">
                Details <ArrowRight className="h-3 w-3" />
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Dimension 2: Learning Mastery */}
        <Card className="hover:border-slate-300 transition-shadow shadow-sm">
          <CardHeader className="pb-3 border-b border-slate-100 flex flex-row items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-emerald-50 text-emerald-600 rounded-md">
                <Award className="h-4 w-4" />
              </div>
              <CardTitle className="text-sm font-semibold">Learning Mastery</CardTitle>
            </div>
            <Badge variant="outline" className="text-[10px] text-slate-500 font-mono">
              Module 05
            </Badge>
          </CardHeader>
          <CardContent className="pt-4 space-y-4">
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs text-slate-600">
                <span>Demonstrated Topics</span>
                <span className="font-semibold text-emerald-700">
                  {mastery_summary.topics_demonstrated_count} / {mastery_summary.topics_assessed_count}
                </span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden flex">
                <div
                  className="bg-emerald-500 h-2"
                  style={{
                    width: `${mastery_summary.topics_assessed_count ? (mastery_summary.topics_demonstrated_count / mastery_summary.topics_assessed_count) * 100 : 0}%`,
                  }}
                />
                <div
                  className="bg-amber-400 h-2"
                  style={{
                    width: `${mastery_summary.topics_assessed_count ? (mastery_summary.topics_developing_count / mastery_summary.topics_assessed_count) * 100 : 0}%`,
                  }}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs text-slate-600">
              <div className="bg-slate-50 p-2 rounded border border-slate-100">
                <span className="text-[11px] text-slate-500 block">CLO Attainment</span>
                <span className="font-semibold text-slate-900">
                  {mastery_summary.clo_attainment_pct !== null ? `${mastery_summary.clo_attainment_pct}%` : 'Pending'}
                </span>
              </div>
              <div className="bg-slate-50 p-2 rounded border border-slate-100">
                <span className="text-[11px] text-slate-500 block">Open Gaps</span>
                <span className="font-semibold text-amber-700">{mastery_summary.active_learning_gaps_count} flagged</span>
              </div>
            </div>
            <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
              <span>Calibration: Deterministic</span>
              <Link to="/mastery" className="text-emerald-600 hover:underline flex items-center gap-1 font-medium">
                Mastery Radar <ArrowRight className="h-3 w-3" />
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Dimension 3: Explainable Academic Risk */}
        <Card className="hover:border-slate-300 transition-shadow shadow-sm">
          <CardHeader className="pb-3 border-b border-slate-100 flex flex-row items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-amber-50 text-amber-600 rounded-md">
                <AlertTriangle className="h-4 w-4" />
              </div>
              <CardTitle className="text-sm font-semibold">Academic Risk Horizon</CardTitle>
            </div>
            <Badge variant="outline" className="text-[10px] text-slate-500 font-mono">
              Module 06
            </Badge>
          </CardHeader>
          <CardContent className="pt-4 space-y-3">
            {risk_summary.has_prediction ? (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-600">Risk Screening:</span>
                  <Badge
                    className={
                      risk_summary.risk_classification === 'LOW'
                        ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                        : risk_summary.risk_classification === 'MODERATE'
                        ? 'bg-amber-100 text-amber-800 border-amber-300'
                        : 'bg-red-100 text-red-800 border-red-300'
                    }
                  >
                    {risk_summary.risk_classification} RISK
                  </Badge>
                </div>
                {risk_summary.primary_adverse_factors.length > 0 && (
                  <div className="space-y-1">
                    <span className="text-[11px] font-semibold text-slate-500 block uppercase">Primary Factor:</span>
                    <p className="text-xs text-slate-700 bg-amber-50/60 p-2 rounded border border-amber-100">
                      {risk_summary.primary_adverse_factors[0]}
                    </p>
                  </div>
                )}
                <p className="text-[10px] text-slate-400 italic leading-snug">
                  {risk_summary.disclaimer}
                </p>
              </>
            ) : (
              <div className="p-4 bg-slate-50 text-center rounded border border-slate-100 text-xs text-slate-500">
                No active risk screening on record.
              </div>
            )}
            <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
              <span>Time-Bounded Cutoff</span>
              <Link to="/academic-risk" className="text-amber-600 hover:underline flex items-center gap-1 font-medium">
                Risk Profile <ArrowRight className="h-3 w-3" />
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Dimension 4: Personalized Academic Interventions */}
        <Card className="hover:border-slate-300 transition-shadow shadow-sm">
          <CardHeader className="pb-3 border-b border-slate-100 flex flex-row items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-indigo-50 text-indigo-600 rounded-md">
                <CheckCircle2 className="h-4 w-4" />
              </div>
              <CardTitle className="text-sm font-semibold">Active Interventions</CardTitle>
            </div>
            <Badge variant="outline" className="text-[10px] text-slate-500 font-mono">
              Module 07
            </Badge>
          </CardHeader>
          <CardContent className="pt-4 space-y-3">
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-600">Active Support Plans:</span>
              <span className="font-bold text-slate-900">{intervention_summary.active_plans_count}</span>
            </div>
            {intervention_summary.latest_plan_title ? (
              <div className="bg-indigo-50/50 p-2.5 rounded border border-indigo-100 text-xs space-y-1">
                <span className="font-semibold text-indigo-950 block truncate">
                  {intervention_summary.latest_plan_title}
                </span>
                <span className="text-[11px] text-indigo-700 block">
                  Mentor: {intervention_summary.faculty_mentor_name || 'Faculty Mentor'}
                </span>
              </div>
            ) : (
              <p className="text-xs text-slate-500">No active academic remediation required.</p>
            )}
            <div className="grid grid-cols-2 gap-2 text-center text-xs">
              <div className="p-2 bg-slate-50 rounded border border-slate-100">
                <span className="text-[11px] text-slate-500 block">Pending</span>
                <span className="font-semibold text-amber-700">{intervention_summary.pending_actions_count} items</span>
              </div>
              <div className="p-2 bg-slate-50 rounded border border-slate-100">
                <span className="text-[11px] text-slate-500 block">Completed</span>
                <span className="font-semibold text-emerald-700">{intervention_summary.completed_actions_count} items</span>
              </div>
            </div>
            <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
              <span>Faculty Supervised</span>
              <Link to="/interventions" className="text-indigo-600 hover:underline flex items-center gap-1 font-medium">
                My Support Plan <ArrowRight className="h-3 w-3" />
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Dimension 5: Career Readiness & Industry Mapping */}
        <Card className="hover:border-slate-300 transition-shadow shadow-sm md:col-span-2 lg:col-span-2">
          <CardHeader className="pb-3 border-b border-slate-100 flex flex-row items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-purple-50 text-purple-600 rounded-md">
                <Briefcase className="h-4 w-4" />
              </div>
              <CardTitle className="text-sm font-semibold">Career Readiness & Practical Projects</CardTitle>
            </div>
            <Badge variant="outline" className="text-[10px] text-slate-500 font-mono">
              Module 08
            </Badge>
          </CardHeader>
          <CardContent className="pt-4 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-purple-50/50 p-3 rounded-lg border border-purple-100">
              <div>
                <span className="text-xs text-purple-700 block font-medium">Target Role Profile:</span>
                <span className="text-base font-bold text-purple-950">
                  {career_summary.target_role_title || 'Software Development Engineer'}
                </span>
              </div>
              <Badge className="bg-purple-600 text-white self-start sm:self-auto text-xs">
                {career_summary.alignment_status?.replace('_', ' ') || 'EVALUATED'}
              </Badge>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1">
                <div className="flex justify-between text-xs text-slate-600">
                  <span>Core Competency Coverage:</span>
                  <span className="font-bold text-slate-900">{career_summary.core_coverage_pct ?? 0}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div className="bg-blue-600 h-2" style={{ width: `${career_summary.core_coverage_pct ?? 0}%` }} />
                </div>
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-xs text-slate-600">
                  <span>Practical Project Coverage:</span>
                  <span className="font-bold text-slate-900">{career_summary.practical_coverage_pct ?? 0}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div className="bg-emerald-600 h-2" style={{ width: `${career_summary.practical_coverage_pct ?? 0}%` }} />
                </div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2 text-center text-xs">
              <div className="p-2 bg-slate-50 rounded border border-slate-100">
                <span className="text-[11px] text-slate-500 block">Verified Projects</span>
                <span className="font-semibold text-emerald-700">{career_summary.verified_projects_count}</span>
              </div>
              <div className="p-2 bg-slate-50 rounded border border-slate-100">
                <span className="text-[11px] text-slate-500 block">Pending Review</span>
                <span className="font-semibold text-amber-700">{career_summary.pending_projects_count}</span>
              </div>
              <div className="p-2 bg-slate-50 rounded border border-slate-100">
                <span className="text-[11px] text-slate-500 block">Identified Gaps</span>
                <span className="font-semibold text-slate-900">{career_summary.active_skill_gaps_count}</span>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
              <span>Non-Aggregated Multi-Modal Evidence</span>
              <Link to="/career-readiness" className="text-purple-600 hover:underline flex items-center gap-1 font-medium">
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
  const { data, isLoading, error } = useQuery({
    queryKey: ['faculty-dashboard-overview'],
    queryFn: () => dashboardService.getFacultyOverview(),
    staleTime: 30000,
  });

  if (isLoading) {
    return (
      <div className="p-12 text-center space-y-3">
        <RefreshCw className="h-8 w-8 animate-spin mx-auto text-blue-600" />
        <p className="text-sm text-slate-600 font-medium">Loading faculty academic queue...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8 bg-red-50 border border-red-200 rounded-lg text-center space-y-3">
        <AlertCircle className="h-8 w-8 text-red-600 mx-auto" />
        <h3 className="text-sm font-semibold text-red-900">Faculty Workspace Error</h3>
        <p className="text-xs text-red-700">Could not retrieve assigned academic subjects or verification queues.</p>
      </div>
    );
  }

  const { verification_queue, cohort_risk_overview, assigned_subjects } = data;

  return (
    <div className="space-y-6">
      <div className="bg-slate-900 text-white rounded-xl p-6 shadow-md border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <Badge className="bg-blue-600 text-white text-xs mb-2">Faculty Intelligence Hub</Badge>
          <h1 className="text-2xl font-bold tracking-tight text-white">{data.faculty_name}</h1>
          <p className="text-xs text-slate-300">
            {data.department} • {data.institution_name} • {data.total_students_monitored} Students Monitored
          </p>
        </div>
      </div>

      {/* Verification Queue Cards */}
      <div>
        <h2 className="text-sm font-semibold text-slate-900 uppercase tracking-wider mb-3">Action Required: Verification Queues</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="border-l-4 border-l-amber-500">
            <CardContent className="pt-4 flex items-center justify-between">
              <div>
                <span className="text-xs text-slate-500 block">Pending Academic Marks</span>
                <span className="text-2xl font-bold text-slate-900">{verification_queue.pending_academic_records}</span>
              </div>
              <Link to="/academic-data">
                <Button size="sm" variant="outline" className="text-xs">
                  Review Records
                </Button>
              </Link>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-indigo-500">
            <CardContent className="pt-4 flex items-center justify-between">
              <div>
                <span className="text-xs text-slate-500 block">Interventions Awaiting Review</span>
                <span className="text-2xl font-bold text-slate-900">{verification_queue.pending_interventions_review}</span>
              </div>
              <Link to="/interventions">
                <Button size="sm" variant="outline" className="text-xs">
                  Review Plans
                </Button>
              </Link>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-purple-500">
            <CardContent className="pt-4 flex items-center justify-between">
              <div>
                <span className="text-xs text-slate-500 block">Practical Projects to Verify</span>
                <span className="text-2xl font-bold text-slate-900">{verification_queue.pending_practical_projects}</span>
              </div>
              <Link to="/career-readiness">
                <Button size="sm" variant="outline" className="text-xs">
                  Verify Projects
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Cohort Risk and Learning Gap Indicators */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-center">
          <span className="text-xs text-red-700 block font-medium">High Risk Students</span>
          <span className="text-2xl font-bold text-red-900">{cohort_risk_overview.high_risk_students_count}</span>
        </div>
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-center">
          <span className="text-xs text-amber-700 block font-medium">Moderate Risk</span>
          <span className="text-2xl font-bold text-amber-900">{cohort_risk_overview.moderate_risk_students_count}</span>
        </div>
        <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-3 text-center">
          <span className="text-xs text-indigo-700 block font-medium">Active Support Plans</span>
          <span className="text-2xl font-bold text-indigo-900">{cohort_risk_overview.active_interventions_count}</span>
        </div>
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-center">
          <span className="text-xs text-slate-600 block font-medium">Flagged Topic Gaps</span>
          <span className="text-2xl font-bold text-slate-900">{cohort_risk_overview.learning_gaps_flagged_count}</span>
        </div>
      </div>

      {/* Assigned Subjects Table */}
      <Card>
        <CardHeader className="pb-3 border-b border-slate-100">
          <CardTitle className="text-sm font-semibold">Assigned Subjects & Performance Health</CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-50 text-slate-600 border-b border-slate-200">
                <tr>
                  <th className="py-2.5 px-3">Subject Code</th>
                  <th className="py-2.5 px-3">Subject Name</th>
                  <th className="py-2.5 px-3">Semester</th>
                  <th className="py-2.5 px-3">Enrolled Students</th>
                  <th className="py-2.5 px-3">Avg Attendance</th>
                  <th className="py-2.5 px-3">Avg Marks</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {assigned_subjects.map((s) => (
                  <tr key={s.subject_id} className="hover:bg-slate-50/50">
                    <td className="py-2.5 px-3 font-mono font-medium">{s.code}</td>
                    <td className="py-2.5 px-3 font-semibold text-slate-900">{s.name}</td>
                    <td className="py-2.5 px-3">{s.semester}</td>
                    <td className="py-2.5 px-3">{s.enrolled_students_count}</td>
                    <td className="py-2.5 px-3 font-medium">
                      {s.average_attendance !== null ? `${s.average_attendance}%` : 'N/A'}
                    </td>
                    <td className="py-2.5 px-3 font-medium">
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
  const { data, isLoading } = useQuery({
    queryKey: ['institution-dashboard-overview'],
    queryFn: () => dashboardService.getInstitutionOverview(),
    staleTime: 30000,
  });

  if (isLoading || !data) {
    return (
      <div className="p-12 text-center space-y-3">
        <RefreshCw className="h-8 w-8 animate-spin mx-auto text-blue-600" />
        <p className="text-sm text-slate-600">Compiling institutional intelligence...</p>
      </div>
    );
  }

  const { summary_counts, academic_data_status, mastery_overview, risk_distribution, intervention_metrics, career_readiness_overview } = data;

  return (
    <div className="space-y-6">
      <div className="bg-slate-900 text-white rounded-xl p-6 shadow-md border border-slate-800">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <Badge className="bg-emerald-600 text-white text-xs mb-2">Institutional Intelligence</Badge>
            <h1 className="text-2xl font-bold tracking-tight text-white">{data.institution_name}</h1>
            <p className="text-xs text-slate-300">Code: {data.institution_code} • Multi-Tenant Tenant Isolation Active</p>
          </div>
        </div>
      </div>

      {/* Summary Counts Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <Card className="text-center p-4">
          <span className="text-xs text-slate-500 block">Active Students</span>
          <span className="text-2xl font-bold text-slate-900">{summary_counts.total_active_students}</span>
        </Card>
        <Card className="text-center p-4">
          <span className="text-xs text-slate-500 block">Faculty Members</span>
          <span className="text-2xl font-bold text-slate-900">{summary_counts.total_faculty}</span>
        </Card>
        <Card className="text-center p-4">
          <span className="text-xs text-slate-500 block">Degree Programs</span>
          <span className="text-2xl font-bold text-slate-900">{summary_counts.total_programs}</span>
        </Card>
        <Card className="text-center p-4">
          <span className="text-xs text-slate-500 block">Academic Subjects</span>
          <span className="text-2xl font-bold text-slate-900">{summary_counts.total_subjects}</span>
        </Card>
      </div>

      {/* 4 Quadrants: Academic Data, Mastery, Risk, Career */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <Card>
          <CardHeader className="pb-3 border-b border-slate-100">
            <CardTitle className="text-sm font-semibold">Academic Data Health (Module 03)</CardTitle>
          </CardHeader>
          <CardContent className="pt-4 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-600">Total Academic Records:</span>
              <span className="font-semibold text-slate-900">{academic_data_status.total_academic_records}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600">Verification Rate:</span>
              <span className="font-semibold text-emerald-700">{academic_data_status.verified_records_pct}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600">Open Data Quality Findings:</span>
              <span className="font-semibold text-amber-700">{academic_data_status.data_quality_findings_count}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3 border-b border-slate-100">
            <CardTitle className="text-sm font-semibold">Learning Mastery Distribution (Module 05)</CardTitle>
          </CardHeader>
          <CardContent className="pt-4 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-600">Demonstrated Mastery:</span>
              <span className="font-semibold text-emerald-700">{mastery_overview.mastery_demonstrated_pct}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600">Developing Mastery:</span>
              <span className="font-semibold text-amber-700">{mastery_overview.mastery_developing_pct}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600">Insufficient Assessment Evidence:</span>
              <span className="font-semibold text-slate-500">{mastery_overview.insufficient_evidence_pct}%</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3 border-b border-slate-100">
            <CardTitle className="text-sm font-semibold">Academic Risk Screening (Module 06)</CardTitle>
          </CardHeader>
          <CardContent className="pt-4 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-600">High / Critical Risk Students:</span>
              <span className="font-semibold text-red-700">{risk_distribution.high_risk_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600">Moderate Risk Students:</span>
              <span className="font-semibold text-amber-700">{risk_distribution.medium_risk_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600">Low Risk Students:</span>
              <span className="font-semibold text-emerald-700">{risk_distribution.low_risk_count}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3 border-b border-slate-100">
            <CardTitle className="text-sm font-semibold">Career Readiness & Projects (Module 08)</CardTitle>
          </CardHeader>
          <CardContent className="pt-4 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-600">Evaluated Students:</span>
              <span className="font-semibold text-slate-900">{career_readiness_overview.students_evaluated_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600">Industry Ready Students:</span>
              <span className="font-semibold text-emerald-700">{career_readiness_overview.ready_students_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600">Verified Practical Projects:</span>
              <span className="font-semibold text-purple-700">{career_readiness_overview.verified_projects_total}</span>
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader className="pb-3 border-b border-slate-100">
            <CardTitle className="text-sm font-semibold">Academic Support & Interventions (Module 07)</CardTitle>
          </CardHeader>
          <CardContent className="pt-4 space-y-2 text-xs">
            <div className="grid grid-cols-3 gap-3 text-center">
              <div className="bg-slate-50 p-2.5 rounded border border-slate-100">
                <span className="text-[11px] text-slate-500 block">Active Support Plans</span>
                <span className="text-base font-bold text-indigo-700">{intervention_metrics.active_plans_count}</span>
              </div>
              <div className="bg-slate-50 p-2.5 rounded border border-slate-100">
                <span className="text-[11px] text-slate-500 block">Completed Plans</span>
                <span className="text-base font-bold text-emerald-700">{intervention_metrics.completed_plans_count}</span>
              </div>
              <div className="bg-slate-50 p-2.5 rounded border border-slate-100">
                <span className="text-[11px] text-slate-500 block">Pending Faculty Review</span>
                <span className="text-base font-bold text-amber-700">{intervention_metrics.pending_review_count}</span>
              </div>
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
  const { data, isLoading } = useQuery({
    queryKey: ['placement-dashboard-overview'],
    queryFn: () => dashboardService.getPlacementOverview(),
    staleTime: 30000,
  });

  if (isLoading || !data) {
    return (
      <div className="p-12 text-center space-y-3">
        <RefreshCw className="h-8 w-8 animate-spin mx-auto text-blue-600" />
        <p className="text-sm text-slate-600">Loading career readiness intelligence...</p>
      </div>
    );
  }

  const { readiness_distribution, project_verification_summary, top_industry_skill_gaps } = data;

  return (
    <div className="space-y-6">
      {/* Firewall Notice Banner */}
      <div className="bg-slate-900 text-white rounded-xl p-5 shadow-sm border border-slate-800 flex items-center justify-between">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-xs text-emerald-400 font-semibold uppercase tracking-wider">
            <Lock className="h-4 w-4" />
            <span>Placement Officer Defense-in-Depth Firewall</span>
          </div>
          <h1 className="text-xl font-bold">Career Readiness & Placement Workspace</h1>
          <p className="text-xs text-slate-400 max-w-2xl">
            This workspace provides verified role readiness, competency evidence, and practical project portfolios.
            Academic risk models (Module 06) and confidential intervention plans (Module 07) are permanently firewalled.
          </p>
        </div>
        <Badge className="bg-emerald-600 text-white font-mono text-xs">Firewall Active</Badge>
      </div>

      {/* Readiness Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="text-center p-4 border-l-4 border-l-emerald-500">
          <span className="text-xs text-slate-500 block">Strong Alignment</span>
          <span className="text-2xl font-bold text-emerald-700">{readiness_distribution.ready_count}</span>
        </Card>
        <Card className="text-center p-4 border-l-4 border-l-blue-500">
          <span className="text-xs text-slate-500 block">Partial Alignment</span>
          <span className="text-2xl font-bold text-blue-700">{readiness_distribution.approaching_count}</span>
        </Card>
        <Card className="text-center p-4 border-l-4 border-l-amber-500">
          <span className="text-xs text-slate-500 block">Limited Alignment</span>
          <span className="text-2xl font-bold text-amber-700">{readiness_distribution.developing_count}</span>
        </Card>
        <Card className="text-center p-4 border-l-4 border-l-purple-500">
          <span className="text-xs text-slate-500 block">Verified Projects</span>
          <span className="text-2xl font-bold text-purple-700">{project_verification_summary.verified_projects_count}</span>
        </Card>
      </div>

      {/* Top Industry Skill Gaps */}
      <Card>
        <CardHeader className="pb-3 border-b border-slate-100 flex flex-row items-center justify-between">
          <CardTitle className="text-sm font-semibold">Top Cohort Industry Skill Gaps</CardTitle>
          <Link to="/career-readiness" className="text-xs text-blue-600 hover:underline flex items-center gap-1 font-medium">
            Explore All Roles <ArrowRight className="h-3 w-3" />
          </Link>
        </CardHeader>
        <CardContent className="pt-0">
          {top_industry_skill_gaps.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-50 text-slate-600 border-b border-slate-200">
                  <tr>
                    <th className="py-2.5 px-3">Competency</th>
                    <th className="py-2.5 px-3">Gap Type</th>
                    <th className="py-2.5 px-3">Affected Students</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {top_industry_skill_gaps.map((g, idx) => (
                    <tr key={idx} className="hover:bg-slate-50/50">
                      <td className="py-2.5 px-3 font-semibold text-slate-900">{g.competency_name}</td>
                      <td className="py-2.5 px-3">
                        <Badge variant="outline" className="text-[10px] font-mono">
                          {g.gap_type}
                        </Badge>
                      </td>
                      <td className="py-2.5 px-3 font-bold text-slate-700">{g.affected_students_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-6 text-center text-xs text-slate-500">No pervasive skill gaps recorded in current cohort.</div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// =========================================================================
// 5. Super Admin Platform Overview
// =========================================================================

const SuperAdminDashboardView: React.FC = () => {
  const { data, isLoading } = useQuery({
    queryKey: ['super-admin-dashboard-overview'],
    queryFn: () => dashboardService.getSuperAdminOverview(),
    staleTime: 30000,
  });

  if (isLoading || !data) {
    return (
      <div className="p-12 text-center space-y-3">
        <RefreshCw className="h-8 w-8 animate-spin mx-auto text-blue-600" />
        <p className="text-sm text-slate-600">Gathering platform operational telemetry...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-slate-900 text-white rounded-xl p-6 shadow-md border border-slate-800">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <Badge className="bg-purple-600 text-white text-xs mb-2">Platform Master Telemetry</Badge>
            <h1 className="text-2xl font-bold tracking-tight text-white">MASTERY Global Platform Overview</h1>
            <p className="text-xs text-slate-300">
              Database: {data.database_connectivity} {data.database_latency_ms ? `(${data.database_latency_ms}ms)` : ''} • Latest Migration: {data.latest_migration}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Badge className="bg-emerald-600 text-white text-xs">All Systems Nominal</Badge>
          </div>
        </div>
      </div>

      {/* Multi-Tenant Counts */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="text-center p-4">
          <span className="text-xs text-slate-500 block">Total Institutions</span>
          <span className="text-2xl font-bold text-slate-900">{data.total_institutions}</span>
        </Card>
        <Card className="text-center p-4">
          <span className="text-xs text-slate-500 block">Total User Identities</span>
          <span className="text-2xl font-bold text-slate-900">{data.total_users}</span>
        </Card>
        <Card className="text-center p-4">
          <span className="text-xs text-slate-500 block">Database Status</span>
          <span className="text-xl font-bold text-emerald-600 capitalize">{data.database_connectivity}</span>
        </Card>
        <Card className="text-center p-4">
          <span className="text-xs text-slate-500 block">Alembic Revision</span>
          <span className="text-sm font-bold font-mono text-slate-800 mt-1 block">{data.latest_migration}</span>
        </Card>
      </div>

      {/* Module Health Grid */}
      <Card>
        <CardHeader className="pb-3 border-b border-slate-100">
          <CardTitle className="text-sm font-semibold">Subsystem Module Operational Matrix</CardTitle>
        </CardHeader>
        <CardContent className="pt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {Object.entries(data.module_health_status).map(([moduleName, healthStatus]) => (
              <div
                key={moduleName}
                className="flex items-center justify-between p-3 rounded-lg border border-slate-200 bg-slate-50/50"
              >
                <span className="text-xs font-medium text-slate-800">{moduleName}</span>
                <Badge className="bg-emerald-100 text-emerald-800 border-emerald-200 text-[10px]">
                  {healthStatus}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
