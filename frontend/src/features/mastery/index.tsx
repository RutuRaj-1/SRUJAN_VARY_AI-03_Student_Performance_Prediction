import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Compass,
  CheckCircle,
  AlertTriangle,
  Award,
  Layers,
  Activity,
  ShieldCheck,
  ShieldAlert,
  Play,
  TrendingUp,
  TrendingDown,
  Eye,
  X,
  BookOpen,
} from 'lucide-react';
import {
  masteryService,
  StudentMasteryProfileResponse,
  MasteryEvidenceItemResponse,
} from '@/services/mastery-service';
import { syllabusService, AcademicSubject } from '@/services/syllabus-service';
import { academicDataService, StudentAcademicProfile } from '@/services/academic-data-service';
import { useAuth } from '@/context/auth-context';

export const MasteryPage: React.FC = () => {
  const { profile } = useAuth();
  const queryClient = useQueryClient();

  const isFacultyOrAdmin =
    profile?.role === 'FACULTY' ||
    profile?.role === 'INSTITUTION_ADMIN' ||
    profile?.role === 'SUPER_ADMIN' ||
    profile?.role === 'PLACEMENT_OFFICER';

  // Navigation tab state
  const [activeTab, setActiveTab] = useState<'overview' | 'student_profile' | 'topics' | 'outcomes' | 'gaps' | 'trends'>(
    isFacultyOrAdmin ? 'overview' : 'student_profile'
  );

  // Global filters
  const [selectedSubjectId, setSelectedSubjectId] = useState<string>('');
  const [selectedStudentId, setSelectedStudentId] = useState<string>('');

  // -------------------------------------------------------------------------
  // Queries
  // -------------------------------------------------------------------------
  const { data: subjects = [] } = useQuery<AcademicSubject[]>({
    queryKey: ['syllabus-subjects'],
    queryFn: () => syllabusService.getSubjects(),
  });

  const { data: students = [] } = useQuery<StudentAcademicProfile[]>({
    queryKey: ['academic-students'],
    queryFn: () => academicDataService.getStudents(),
    enabled: isFacultyOrAdmin,
  });

  // Set default subject and student
  useEffect(() => {
    if (subjects.length > 0 && !selectedSubjectId) {
      setSelectedSubjectId(subjects[0].id);
    }
  }, [subjects, selectedSubjectId]);

  useEffect(() => {
    if (isFacultyOrAdmin) {
      if (students.length > 0 && !selectedStudentId) {
        setSelectedStudentId(students[0].id);
      }
    } else if (profile?.user_id) {
      // Find matching academic student record for current user
      const selfStudent = students.find((s) => s.profile_id === profile.user_id);
      if (selfStudent) {
        setSelectedStudentId(selfStudent.id);
      }
    }
  }, [students, profile, isFacultyOrAdmin, selectedStudentId]);

  // Cohort Summary Query
  const { data: cohortSummary, isLoading: isLoadingCohort } = useQuery({
    queryKey: ['cohort-mastery-summary', selectedSubjectId],
    queryFn: () => masteryService.getCohortSummary(selectedSubjectId),
    enabled: !!selectedSubjectId && isFacultyOrAdmin,
  });

  // Student Mastery Profile Query
  const {
    data: studentProfile,
    isLoading: isLoadingProfile,
  } = useQuery<StudentMasteryProfileResponse>({
    queryKey: ['student-mastery-profile', selectedStudentId, selectedSubjectId],
    queryFn: () => masteryService.getStudentMasteryProfile(selectedStudentId, selectedSubjectId),
    enabled: !!selectedStudentId && !!selectedSubjectId,
  });

  // Performance Trends Query
  const { data: performanceTrends } = useQuery({
    queryKey: ['student-performance-trends', selectedStudentId, selectedSubjectId],
    queryFn: () => masteryService.getStudentPerformanceTrends(selectedStudentId, selectedSubjectId),
    enabled: !!selectedStudentId && !!selectedSubjectId && activeTab === 'trends',
  });

  // -------------------------------------------------------------------------
  // State: Trigger Analysis Job Modal
  // -------------------------------------------------------------------------
  const [showAnalyzeModal, setShowAnalyzeModal] = useState(false);
  const [analyzeTargetMode, setAnalyzeTargetMode] = useState<'SINGLE' | 'ALL'>('ALL');
  const [includePractice, setIncludePractice] = useState(false);

  const triggerAnalysisMutation = useMutation({
    mutationFn: masteryService.triggerAnalysis,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cohort-mastery-summary'] });
      queryClient.invalidateQueries({ queryKey: ['student-mastery-profile'] });
      queryClient.invalidateQueries({ queryKey: ['student-performance-trends'] });
      setShowAnalyzeModal(false);
      alert('Mastery Analysis Job completed successfully!');
    },
    onError: (err: any) => {
      alert(err?.response?.data?.detail || 'Failed to execute analysis job.');
    },
  });

  // -------------------------------------------------------------------------
  // State: Evidence Inspection Drawer
  // -------------------------------------------------------------------------
  const [inspectingResultId, setInspectingResultId] = useState<string | null>(null);
  const [inspectingTopicName, setInspectingTopicName] = useState<string>('');

  const { data: contributingEvidence = [], isLoading: isLoadingEvidence } = useQuery<MasteryEvidenceItemResponse[]>({
    queryKey: ['result-contributing-evidence', inspectingResultId],
    queryFn: () => masteryService.inspectContributingEvidence(inspectingResultId!),
    enabled: !!inspectingResultId,
  });

  const { data: excludedEvidence = [] } = useQuery<MasteryEvidenceItemResponse[]>({
    queryKey: ['result-excluded-evidence', inspectingResultId],
    queryFn: () => masteryService.inspectExcludedEvidence(inspectingResultId!),
    enabled: !!inspectingResultId,
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 py-8">
      {/* ===================================================================== */}
      {/* HEADER SECTION */}
      {/* ===================================================================== */}
      <div className="bg-[#123E40] border border-[#18575A] rounded-[6px] p-6 shadow-subtle text-white">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-[#D9F0EE] text-xs font-semibold uppercase tracking-wider mb-1 font-mono">
              <Compass className="w-4 h-4 text-[#2D8E92]" />
              Module 04: Evidence-Based Learning Mastery
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight font-sans">
              Learning Mastery & Performance Analytics
            </h1>
            <p className="text-slate-300 text-xs mt-1">
              Evidence-based topic mastery, learning outcome attainment, and explainable performance intelligence derived from verified curriculum and assessment evidence.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <span className="px-2.5 py-1 bg-[#EEF8F7] text-[#123E40] rounded-[3px] text-xs font-semibold border border-[#BDCEC8]">
              Role: {profile?.role || 'STUDENT'}
            </span>
            {isFacultyOrAdmin && (
              <button
                onClick={() => setShowAnalyzeModal(true)}
                className="flex items-center gap-2 px-3.5 py-1.5 bg-[#237277] hover:bg-[#18575A] text-white rounded-[4px] text-xs font-semibold transition-colors shadow-sm"
              >
                <Play className="w-3.5 h-3.5" /> Run Mastery Analysis
              </button>
            )}
          </div>
        </div>

        {/* Global Selectors */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6 pt-4 border-t border-slate-800">
          <div>
            <label className="text-xs font-medium text-slate-400 block mb-1">Academic Subject:</label>
            <select
              value={selectedSubjectId}
              onChange={(e) => setSelectedSubjectId(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-2 text-sm"
            >
              {subjects.map((sub: AcademicSubject) => (
                <option key={sub.id} value={sub.id}>
                  {sub.code} — {sub.name} (Sem {sub.semester})
                </option>
              ))}
            </select>
          </div>

          {isFacultyOrAdmin && (
            <div>
              <label className="text-xs font-medium text-slate-400 block mb-1">Target Student:</label>
              <select
                value={selectedStudentId}
                onChange={(e) => setSelectedStudentId(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-2 text-sm"
              >
                {students.map((stud) => (
                  <option key={stud.id} value={stud.id}>
                    {stud.first_name} {stud.last_name} ({stud.enrollment_number})
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Navigation Tabs */}
        <div className="flex flex-wrap gap-2 mt-6 pt-4 border-t border-slate-800">
          {isFacultyOrAdmin && (
            <button
              onClick={() => setActiveTab('overview')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'overview'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              <Layers className="w-4 h-4" /> Cohort Mastery Overview
            </button>
          )}

          <button
            onClick={() => setActiveTab('student_profile')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'student_profile'
                ? 'bg-indigo-600 text-white'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            <Compass className="w-4 h-4" /> Student Mastery Profile
          </button>

          <button
            onClick={() => setActiveTab('topics')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'topics'
                ? 'bg-indigo-600 text-white'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            <BookOpen className="w-4 h-4" /> Topic Mastery Explorer
          </button>

          <button
            onClick={() => setActiveTab('outcomes')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'outcomes'
                ? 'bg-indigo-600 text-white'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            <Award className="w-4 h-4" /> Outcome Attainment
          </button>

          <button
            onClick={() => setActiveTab('gaps')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'gaps'
                ? 'bg-indigo-600 text-white'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            <AlertTriangle className="w-4 h-4" /> Learning Gap Findings
          </button>

          <button
            onClick={() => setActiveTab('trends')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'trends'
                ? 'bg-indigo-600 text-white'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            <Activity className="w-4 h-4" /> Cognitive Radar & Trends
          </button>
        </div>
      </div>

      {/* Scientific Governance Disclaimer Alert */}
      <div className="bg-slate-900 border border-indigo-900/60 rounded-xl p-4 flex items-start gap-3">
        <ShieldCheck className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
        <div className="text-xs text-slate-300 leading-relaxed">
          <span className="font-bold text-indigo-300">SCIENTIFIC GOVERNANCE NOTICE: </span>
          Learning mastery metrics reflect observed, normalized performance across eligible assessment items. They represent evidence-backed indicators of topic familiarity and must NEVER be equated with a scientifically proven measure of total internal conceptual mastery or student intelligence.
        </div>
      </div>

      {/* ===================================================================== */}
      {/* TAB 1: COHORT MASTERY OVERVIEW (FACULTY) */}
      {/* ===================================================================== */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {isLoadingCohort ? (
            <div className="p-12 text-center text-slate-400">Loading cohort mastery intelligence...</div>
          ) : !cohortSummary ? (
            <div className="p-12 text-center text-slate-400 bg-slate-900 rounded-xl border border-slate-800">
              No cohort mastery data found for this subject. Run a mastery analysis job above.
            </div>
          ) : (
            <div className="space-y-6">
              {/* Metric Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl text-center">
                  <div className="text-xs text-slate-400">Total Enrolled</div>
                  <div className="text-2xl font-bold text-white mt-1">{cohortSummary.total_students_enrolled}</div>
                </div>
                <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl text-center">
                  <div className="text-xs text-slate-400">Students Analyzed</div>
                  <div className="text-2xl font-bold text-indigo-400 mt-1">{cohortSummary.students_analyzed}</div>
                </div>
                <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl text-center">
                  <div className="text-xs text-slate-400">Curriculum Coverage</div>
                  <div className="text-2xl font-bold text-emerald-400 mt-1">
                    {cohortSummary.curriculum_coverage_percentage}%
                  </div>
                </div>
                <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl text-center">
                  <div className="text-xs text-slate-400">Syllabus Topics</div>
                  <div className="text-2xl font-bold text-amber-400 mt-1">
                    {cohortSummary.topic_aggregates.length}
                  </div>
                </div>
              </div>

              {/* Topic Cohort Table */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                <div className="p-4 border-b border-slate-800 flex items-center justify-between">
                  <h3 className="text-sm font-bold text-white">Syllabus Topic Performance Across Cohort</h3>
                  <span className="text-xs text-slate-400 font-mono">
                    Subject: {cohortSummary.subject_code}
                  </span>
                </div>

                <table className="w-full text-left text-sm">
                  <thead className="bg-slate-950 text-slate-400 text-xs uppercase border-b border-slate-800">
                    <tr>
                      <th className="px-4 py-3">Topic Name</th>
                      <th className="px-4 py-3 text-center">Assessed Students</th>
                      <th className="px-4 py-3 text-center">Average Mastery</th>
                      <th className="px-4 py-3 text-right">Evidence Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-slate-300">
                    {cohortSummary.topic_aggregates.map((item) => (
                      <tr key={item.topic_id} className="hover:bg-slate-850">
                        <td className="px-4 py-3 font-medium text-white">{item.topic_name}</td>
                        <td className="px-4 py-3 text-center">{item.assessed_candidates_count}</td>
                        <td className="px-4 py-3 text-center">
                          {item.average_mastery_percentage !== null && item.average_mastery_percentage !== undefined ? (
                            <span
                              className={`font-bold ${
                                item.average_mastery_percentage >= 75
                                  ? 'text-emerald-400'
                                  : item.average_mastery_percentage >= 50
                                  ? 'text-amber-400'
                                  : 'text-rose-400'
                              }`}
                            >
                              {item.average_mastery_percentage}%
                            </span>
                          ) : (
                            <span className="text-slate-500 font-mono text-xs">Unassessed</span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-right">
                          {item.has_sufficient_evidence ? (
                            <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800">
                              Assessed
                            </span>
                          ) : (
                            <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700">
                              Insufficient Evidence
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ===================================================================== */}
      {/* TAB 2: STUDENT MASTERY PROFILE */}
      {/* ===================================================================== */}
      {activeTab === 'student_profile' && (
        <div className="space-y-6">
          {isLoadingProfile ? (
            <div className="p-12 text-center text-slate-400">Loading student mastery profile...</div>
          ) : !studentProfile ? (
            <div className="p-12 text-center text-slate-400 bg-slate-900 rounded-xl border border-slate-800">
              No mastery profile found for this student. Run an analysis job to evaluate current evidence.
            </div>
          ) : (
            <div className="space-y-6">
              {/* Student Summary Card */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  <div>
                    <h2 className="text-xl font-bold text-white">{studentProfile.student_name}</h2>
                    <p className="text-xs text-slate-400 font-mono mt-0.5">
                      Enrollment #{studentProfile.enrollment_number} | Subject: {studentProfile.subject_code} - {studentProfile.subject_name}
                    </p>
                  </div>

                  <div className="text-right">
                    <div className="text-xs text-slate-400 font-medium">Demonstrated Subject Mastery</div>
                    <div className="text-3xl font-extrabold text-indigo-400">
                      {studentProfile.overall_mastery_percentage !== null
                        ? `${studentProfile.overall_mastery_percentage}%`
                        : 'Insufficient Evidence'}
                    </div>
                  </div>
                </div>

                {/* Status Tally */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6 pt-4 border-t border-slate-800 text-center">
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                    <div className="text-xs text-slate-500">Mastered Topics</div>
                    <div className="text-xl font-bold text-emerald-400 mt-1">
                      {studentProfile.mastered_topics_count}
                    </div>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                    <div className="text-xs text-slate-500">Progressing Topics</div>
                    <div className="text-xl font-bold text-amber-400 mt-1">
                      {studentProfile.progressing_topics_count}
                    </div>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                    <div className="text-xs text-slate-500">Needs Attention</div>
                    <div className="text-xl font-bold text-rose-400 mt-1">
                      {studentProfile.needs_attention_topics_count}
                    </div>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                    <div className="text-xs text-slate-500">Unassessed / Insufficient</div>
                    <div className="text-xl font-bold text-slate-400 mt-1">
                      {studentProfile.insufficient_evidence_topics_count}
                    </div>
                  </div>
                </div>
              </div>

              {/* Topic Mastery Summary List */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-indigo-400" /> Syllabus Topics Breakdown
                </h3>

                <div className="space-y-3">
                  {studentProfile.topic_results.map((tr) => (
                    <div
                      key={tr.id}
                      className="bg-slate-950 border border-slate-800 hover:border-slate-700 p-4 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-4 transition-colors"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-mono font-bold text-indigo-400">
                            Unit {tr.unit_number}:
                          </span>
                          <span className="text-sm font-bold text-white">{tr.topic_name}</span>
                        </div>
                        <p className="text-xs text-slate-400">{tr.plain_explanation}</p>
                      </div>

                      <div className="flex items-center gap-4 shrink-0">
                        <div className="text-right">
                          <div className="text-sm font-bold text-white">
                            {tr.mastery_percentage !== null ? `${tr.mastery_percentage}%` : '—'}
                          </div>
                          <span
                            className={`text-xs px-2 py-0.5 rounded font-semibold ${
                              tr.mastery_status === 'MASTERED'
                                ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                                : tr.mastery_status === 'PROGRESSING'
                                ? 'bg-amber-950 text-amber-400 border border-amber-800'
                                : tr.mastery_status === 'NEEDS_ATTENTION'
                                ? 'bg-rose-950 text-rose-400 border border-rose-800'
                                : 'bg-slate-800 text-slate-400 border border-slate-700'
                            }`}
                          >
                            {tr.mastery_status}
                          </span>
                        </div>

                        <button
                          onClick={() => {
                            setInspectingResultId(tr.id);
                            setInspectingTopicName(tr.topic_name);
                          }}
                          className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-medium transition-colors"
                        >
                          <Eye className="w-3.5 h-3.5" /> Evidence
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ===================================================================== */}
      {/* TAB 3: TOPIC MASTERY EXPLORER */}
      {/* ===================================================================== */}
      {activeTab === 'topics' && studentProfile && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-slate-800">
            <h3 className="text-sm font-bold text-white">Detailed Topic Evidence Attribution</h3>
          </div>
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950 text-slate-400 text-xs uppercase border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">Topic Name</th>
                <th className="px-4 py-3 text-center">Eligible Items</th>
                <th className="px-4 py-3 text-center">Marks Scored</th>
                <th className="px-4 py-3 text-center">Mastery %</th>
                <th className="px-4 py-3 text-center">Sufficiency</th>
                <th className="px-4 py-3 text-right">Audit</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {studentProfile.topic_results.map((tr) => (
                <tr key={tr.id} className="hover:bg-slate-850">
                  <td className="px-4 py-3 font-medium text-white">{tr.topic_name}</td>
                  <td className="px-4 py-3 text-center font-mono text-xs">{tr.eligible_question_count}</td>
                  <td className="px-4 py-3 text-center font-mono text-xs">
                    {tr.marks_obtained} / {tr.maximum_marks}
                  </td>
                  <td className="px-4 py-3 text-center font-bold">
                    {tr.mastery_percentage !== null ? `${tr.mastery_percentage}%` : '—'}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span
                      className={`text-xs px-2 py-0.5 rounded font-semibold ${
                        tr.evidence_sufficiency === 'STRONG'
                          ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                          : tr.evidence_sufficiency === 'MODERATE'
                          ? 'bg-indigo-950 text-indigo-400 border border-indigo-800'
                          : tr.evidence_sufficiency === 'LIMITED'
                          ? 'bg-amber-950 text-amber-400 border border-amber-800'
                          : 'bg-slate-800 text-slate-400 border border-slate-700'
                      }`}
                    >
                      {tr.evidence_sufficiency}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => {
                        setInspectingResultId(tr.id);
                        setInspectingTopicName(tr.topic_name);
                      }}
                      className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs font-medium"
                    >
                      Inspect
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ===================================================================== */}
      {/* TAB 4: OUTCOME ATTAINMENT */}
      {/* ===================================================================== */}
      {activeTab === 'outcomes' && studentProfile && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-slate-800">
            <h3 className="text-sm font-bold text-white">Course Learning Outcome (CLO) Attainment</h3>
          </div>
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950 text-slate-400 text-xs uppercase border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">Outcome</th>
                <th className="px-4 py-3">Outcome Description</th>
                <th className="px-4 py-3 text-center">Bloom Level</th>
                <th className="px-4 py-3 text-center">Items</th>
                <th className="px-4 py-3 text-center">Attainment %</th>
                <th className="px-4 py-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {studentProfile.outcome_results.map((o) => (
                <tr key={o.id} className="hover:bg-slate-850">
                  <td className="px-4 py-3 font-mono font-bold text-indigo-400">{o.outcome_code}</td>
                  <td className="px-4 py-3 text-xs text-slate-300 max-w-md">{o.description}</td>
                  <td className="px-4 py-3 text-center">
                    <span className="px-2 py-0.5 rounded text-xs bg-purple-950 text-purple-300">
                      {o.bloom_level}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-xs">{o.eligible_question_count}</td>
                  <td className="px-4 py-3 text-center font-bold">
                    {o.attainment_percentage !== null ? `${o.attainment_percentage}%` : '—'}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span
                      className={`text-xs px-2.5 py-0.5 rounded font-semibold ${
                        o.attainment_status === 'ATTAINED'
                          ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                          : o.attainment_status === 'PARTIALLY_ATTAINED'
                          ? 'bg-amber-950 text-amber-400 border border-amber-800'
                          : o.attainment_status === 'NOT_ATTAINED'
                          ? 'bg-rose-950 text-rose-400 border border-rose-800'
                          : 'bg-slate-800 text-slate-400 border border-slate-700'
                      }`}
                    >
                      {o.attainment_status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ===================================================================== */}
      {/* TAB 5: LEARNING GAP FINDINGS */}
      {/* ===================================================================== */}
      {activeTab === 'gaps' && studentProfile && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" /> Discovered Learning Gaps & Evidence Gaps
            </h3>
            <span className="text-xs text-slate-400 font-mono">
              Total Findings: {studentProfile.learning_gaps.length}
            </span>
          </div>

          {studentProfile.learning_gaps.length === 0 ? (
            <div className="p-12 text-center text-slate-400 bg-slate-900 rounded-xl border border-slate-800">
              No learning gaps detected. All assessed topics demonstrate strong understanding!
            </div>
          ) : (
            <div className="space-y-3">
              {studentProfile.learning_gaps.map((gap) => (
                <div
                  key={gap.id}
                  className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-2 hover:border-slate-700 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-xs font-semibold px-2.5 py-0.5 rounded ${
                          gap.severity === 'CRITICAL'
                            ? 'bg-rose-950 text-rose-400 border border-rose-800'
                            : gap.severity === 'HIGH'
                            ? 'bg-amber-950 text-amber-400 border border-amber-800'
                            : 'bg-slate-800 text-slate-300 border border-slate-700'
                        }`}
                      >
                        {gap.severity}
                      </span>
                      <span className="text-xs font-mono text-indigo-400 font-semibold">
                        {gap.finding_type}
                      </span>
                    </div>
                    <span className="text-xs font-mono text-slate-500">
                      Topic: {gap.topic_name || gap.outcome_code || 'General'}
                    </span>
                  </div>

                  <p className="text-sm text-white font-medium">{gap.evidence_summary}</p>

                  {gap.recommended_review_action && (
                    <div className="text-xs text-slate-400 bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                      <span className="text-slate-300 font-semibold">Recommended Action: </span>
                      {gap.recommended_review_action}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ===================================================================== */}
      {/* TAB 6: COGNITIVE RADAR & TRENDS */}
      {/* ===================================================================== */}
      {activeTab === 'trends' && studentProfile && (
        <div className="space-y-6">
          {/* Bloom's Taxonomy Cognitive Breakdown */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Compass className="w-4 h-4 text-indigo-400" /> Cognitive Performance Breakdown (Bloom's Taxonomy)
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-6 gap-3">
              {Object.entries(studentProfile.cognitive_breakdown).map(([tier, data]) => (
                <div key={tier} className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-center">
                  <div className="text-xs text-slate-400 font-semibold">{tier}</div>
                  <div className="text-lg font-bold text-white mt-1">
                    {data.percentage !== null ? `${data.percentage}%` : '—'}
                  </div>
                  <div className="text-xs text-slate-500 mt-0.5">{data.questions_assessed} items</div>
                </div>
              ))}
            </div>
          </div>

          {/* Longitudinal Trend Timeline */}
          {performanceTrends && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Activity className="w-4 h-4 text-emerald-400" /> Longitudinal Assessment Performance Timeline
                </h3>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400">Trend Direction:</span>
                  <span className="text-xs font-bold px-2.5 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800 flex items-center gap-1">
                    {performanceTrends.trend_direction === 'IMPROVING' ? (
                      <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
                    ) : (
                      <TrendingDown className="w-3.5 h-3.5 text-amber-400" />
                    )}
                    {performanceTrends.trend_direction}
                  </span>
                </div>
              </div>

              {performanceTrends.timeline.length === 0 ? (
                <div className="p-8 text-center text-slate-400 text-xs">
                  Insufficient historical assessment points to compute trend line.
                </div>
              ) : (
                <div className="space-y-2">
                  {performanceTrends.timeline.map((pt, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between text-xs bg-slate-950 p-3 rounded-lg border border-slate-800"
                    >
                      <div className="flex items-center gap-3">
                        <span className="font-mono text-slate-500">
                          {new Date(pt.timestamp).toLocaleDateString()}
                        </span>
                        <span className="text-white font-medium">{pt.assessment_name}</span>
                        {pt.topic_name && (
                          <span className="text-slate-400 font-mono">({pt.topic_name})</span>
                        )}
                      </div>

                      <div className="flex items-center gap-3">
                        <span className="font-bold text-emerald-400">{pt.percentage}%</span>
                        <span className="px-2 py-0.5 rounded text-xs bg-slate-800 text-slate-300">
                          {pt.is_official ? 'Official' : 'Practice'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ===================================================================== */}
      {/* MODAL: RUN MASTERY ANALYSIS */}
      {/* ===================================================================== */}
      {showAnalyzeModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-lg font-bold text-white">Execute Learning Mastery Analysis</h3>
              <button
                onClick={() => setShowAnalyzeModal(false)}
                className="p-1 rounded text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">
              Synthesizes verified curriculum structures from Phase 03 and assessment attempt evidence from Phase 05. Filters eligible evidence, eliminates double-counting, and produces topic mastery and outcome attainment metrics.
            </p>

            <div className="space-y-3 pt-2">
              <div>
                <label className="text-xs text-slate-400 block mb-1">Target Analysis Scope</label>
                <select
                  value={analyzeTargetMode}
                  onChange={(e) => setAnalyzeTargetMode(e.target.value as any)}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded px-3 py-2 text-xs"
                >
                  <option value="ALL">All Enrolled Students in Subject</option>
                  <option value="SINGLE">Single Selected Student Only</option>
                </select>
              </div>

              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="includePractice"
                  checked={includePractice}
                  onChange={(e) => setIncludePractice(e.target.checked)}
                  className="w-4 h-4 rounded text-indigo-600"
                />
                <label htmlFor="includePractice" className="text-xs text-slate-300">
                  Include diagnostic Practice Tests as supplementary evidence
                </label>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
              <button
                onClick={() => setShowAnalyzeModal(false)}
                className="px-4 py-2 rounded text-xs text-slate-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                disabled={triggerAnalysisMutation.isPending}
                onClick={() => {
                  triggerAnalysisMutation.mutate({
                    subject_id: selectedSubjectId,
                    student_id: analyzeTargetMode === 'SINGLE' ? selectedStudentId : undefined,
                    academic_year: '2024-2025',
                    semester: 4,
                    include_practice_tests: includePractice,
                  });
                }}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-semibold disabled:opacity-50"
              >
                {triggerAnalysisMutation.isPending ? 'Analyzing...' : 'Run Analysis Job'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ===================================================================== */}
      {/* DRAWER: EVIDENCE INSPECTION & AUDITABILITY */}
      {/* ===================================================================== */}
      {inspectingResultId && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50 overflow-y-auto">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-3xl w-full p-6 space-y-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div>
                <h3 className="text-lg font-bold text-white">Evidence Traceability Audit</h3>
                <p className="text-xs text-indigo-400 font-mono">Topic: {inspectingTopicName}</p>
              </div>
              <button
                onClick={() => setInspectingResultId(null)}
                className="p-1 rounded text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Contributing Eligible Evidence */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                <CheckCircle className="w-4 h-4" /> Eligible Contributing Items ({contributingEvidence.length})
              </h4>

              {isLoadingEvidence ? (
                <div className="text-xs text-slate-400">Loading evidence items...</div>
              ) : contributingEvidence.length === 0 ? (
                <div className="text-xs text-slate-500 bg-slate-950 p-3 rounded">
                  No eligible assessment items contributed to this result.
                </div>
              ) : (
                <div className="space-y-2">
                  {contributingEvidence.map((ev) => (
                    <div
                      key={ev.id}
                      className="bg-slate-950 border border-emerald-900/40 p-3 rounded-lg text-xs space-y-1.5"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-white">{ev.question_text || 'Assessment Question'}</span>
                        <span className="font-mono font-bold text-emerald-400">
                          {ev.marks_obtained} / {ev.maximum_marks} M
                        </span>
                      </div>
                      <div className="flex items-center gap-3 text-slate-400">
                        <span>Evaluation: {ev.verification_status || ev.evaluation_status}</span>
                        <span>Bloom: {ev.bloom_level || 'N/A'}</span>
                        <span>Recorded: {new Date(ev.evidence_timestamp).toLocaleDateString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Excluded Evidence (Audit Transparency) */}
            <div className="space-y-3 pt-3 border-t border-slate-800">
              <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                <ShieldAlert className="w-4 h-4" /> Excluded Items & Rejection Reasons ({excludedEvidence.length})
              </h4>

              {excludedEvidence.length === 0 ? (
                <div className="text-xs text-slate-500 bg-slate-950 p-3 rounded">
                  Zero candidate records were excluded during evidence qualification.
                </div>
              ) : (
                <div className="space-y-2">
                  {excludedEvidence.map((ex) => (
                    <div
                      key={ex.id}
                      className="bg-slate-950 border border-amber-900/40 p-3 rounded-lg text-xs space-y-1"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300 font-medium">{ex.source_entity_type}</span>
                        <span className="px-2 py-0.5 rounded font-mono text-amber-400 bg-amber-950 border border-amber-800">
                          {ex.exclusion_reason}
                        </span>
                      </div>
                      <p className="text-slate-500 text-xs font-mono">ID: {ex.source_entity_id}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
