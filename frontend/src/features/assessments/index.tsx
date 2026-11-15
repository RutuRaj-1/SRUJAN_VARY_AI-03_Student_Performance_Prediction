import React, { useState, useEffect, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  BookOpen,
  CheckCircle,
  AlertTriangle,
  Clock,
  Play,
  Award,
  BarChart2,
  ShieldCheck,
  Filter,
  Plus,
  Send,
  ShieldAlert,
  X,
  FileCheck,
  Activity,
  Layers,
  ArrowRight,
  ArrowLeft,
} from 'lucide-react';
import {
  assessmentService,
  QuestionType,
  QuestionDifficulty,
  AttemptStartResponse,
  AttemptDetail,
} from '@/services/assessment-service';
import { syllabusService, AcademicSubject } from '@/services/syllabus-service';
import { useAuth } from '@/context/auth-context';

export const AssessmentPage: React.FC = () => {
  const { profile } = useAuth();
  const queryClient = useQueryClient();

  const isFacultyOrAdmin =
    profile?.role === 'FACULTY' ||
    profile?.role === 'INSTITUTION_ADMIN' ||
    profile?.role === 'SUPER_ADMIN';

  // Navigation tab state
  const [activeTab, setActiveTab] = useState<'questions' | 'assessments' | 'student_tests' | 'evaluations' | 'analytics'>(
    isFacultyOrAdmin ? 'assessments' : 'student_tests'
  );

  // Global filters
  const [selectedSubjectId, setSelectedSubjectId] = useState<string>('');

  // -------------------------------------------------------------------------
  // Queries
  // -------------------------------------------------------------------------
  const { data: subjects = [] } = useQuery<AcademicSubject[]>({
    queryKey: ['syllabus-subjects'],
    queryFn: () => syllabusService.getSubjects(),
  });

  // Set default subject once loaded
  useEffect(() => {
    if (subjects.length > 0 && !selectedSubjectId) {
      setSelectedSubjectId(subjects[0].id);
    }
  }, [subjects, selectedSubjectId]);

  // Questions query
  const [questionTypeFilter, setQuestionTypeFilter] = useState<string>('');
  const [difficultyFilter, setDifficultyFilter] = useState<string>('');
  const { data: questions = [], isLoading: isLoadingQuestions } = useQuery({
    queryKey: ['assessment-questions', selectedSubjectId, questionTypeFilter, difficultyFilter],
    queryFn: () =>
      assessmentService.listQuestions(
        selectedSubjectId || undefined,
        questionTypeFilter || undefined,
        difficultyFilter || undefined
      ),
    enabled: !!selectedSubjectId,
  });

  // Assessments query
  const { data: assessments = [], isLoading: isLoadingAssessments } = useQuery({
    queryKey: ['assessments-list', selectedSubjectId],
    queryFn: () => assessmentService.listAssessments(selectedSubjectId || undefined),
    enabled: !!selectedSubjectId,
  });

  // Available Assessments for Student
  const { data: availableAssessments = [], isLoading: isLoadingAvailable, refetch: refetchAvailable } = useQuery({
    queryKey: ['available-assessments'],
    queryFn: () => assessmentService.getAvailableAssessments(),
  });

  // -------------------------------------------------------------------------
  // State: Question Bank Modal
  // -------------------------------------------------------------------------
  const [showCreateQuestionModal, setShowCreateQuestionModal] = useState(false);
  const [qText, setQText] = useState('');
  const [qType, setQType] = useState<QuestionType>('MCQ');
  const [qDifficulty, setQDifficulty] = useState<QuestionDifficulty>('MEDIUM');
  const [qBloom, setQBloom] = useState('APPLY');
  const [qMarks, setQMarks] = useState(2.0);
  const [qExplanation, setQExplanation] = useState('');
  const [qCodeLang, setQCodeLang] = useState('python');
  const [qCodeTemplate, setQCodeTemplate] = useState('def solution():\n    # Implement here\n    pass');
  const [qOptions, setQOptions] = useState([
    { option_text: '', is_correct: true, display_order: 1 },
    { option_text: '', is_correct: false, display_order: 2 },
    { option_text: '', is_correct: false, display_order: 3 },
    { option_text: '', is_correct: false, display_order: 4 },
  ]);

  const createQuestionMutation = useMutation({
    mutationFn: assessmentService.createQuestion,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessment-questions'] });
      setShowCreateQuestionModal(false);
      resetQuestionForm();
    },
  });

  const resetQuestionForm = () => {
    setQText('');
    setQType('MCQ');
    setQDifficulty('MEDIUM');
    setQBloom('APPLY');
    setQMarks(2.0);
    setQExplanation('');
    setQOptions([
      { option_text: '', is_correct: true, display_order: 1 },
      { option_text: '', is_correct: false, display_order: 2 },
      { option_text: '', is_correct: false, display_order: 3 },
      { option_text: '', is_correct: false, display_order: 4 },
    ]);
  };

  // -------------------------------------------------------------------------
  // State: Assessment Builder Modal
  // -------------------------------------------------------------------------
  const [showCreateAsmtModal, setShowCreateAsmtModal] = useState(false);
  const [asmtName, setAsmtName] = useState('');
  const [asmtType, setAsmtType] = useState('INTERNAL_TEST');
  const [asmtMaxMarks, setAsmtMaxMarks] = useState(25);
  const [asmtPassingMarks, setAsmtPassingMarks] = useState(10);
  const [asmtDuration, setAsmtDuration] = useState(45);
  const [asmtAttemptLimit, setAsmtAttemptLimit] = useState(1);
  const [asmtInstructions, setAsmtInstructions] = useState('Answer all questions within the allocated duration. Auto-save is active.');
  const [selectedQuestionIds, setSelectedQuestionIds] = useState<string[]>([]);

  // Calculate sum of marks of selected questions
  const selectedQuestionsMarksSum = useMemo(() => {
    return selectedQuestionIds.reduce((sum, qId) => {
      const q = questions.find((item) => item.id === qId);
      return sum + (q?.default_marks || 0);
    }, 0);
  }, [selectedQuestionIds, questions]);

  const createAssessmentMutation = useMutation({
    mutationFn: assessmentService.createAssessment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessments-list'] });
      setShowCreateAsmtModal(false);
      resetAssessmentForm();
    },
  });

  const publishAssessmentMutation = useMutation({
    mutationFn: assessmentService.publishAssessment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessments-list'] });
      refetchAvailable();
    },
  });

  const closeAssessmentMutation = useMutation({
    mutationFn: assessmentService.closeAssessment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessments-list'] });
      refetchAvailable();
    },
  });

  const resetAssessmentForm = () => {
    setAsmtName('');
    setAsmtType('INTERNAL_TEST');
    setAsmtMaxMarks(25);
    setAsmtPassingMarks(10);
    setAsmtDuration(45);
    setAsmtAttemptLimit(1);
    setSelectedQuestionIds([]);
  };

  // -------------------------------------------------------------------------
  // State: Active Student Test Session
  // -------------------------------------------------------------------------
  const [activeTestSession, setActiveTestSession] = useState<AttemptStartResponse | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [studentAnswers, setStudentAnswers] = useState<Record<string, any>>({});
  const [autosaveStatus, setAutosaveStatus] = useState<string>('All changes saved');
  const [timeRemainingSeconds, setTimeRemainingSeconds] = useState<number | null>(null);
  const [showSubmitConfirmModal, setShowSubmitConfirmModal] = useState(false);
  const [testCompletedSummary, setTestCompletedSummary] = useState<AttemptDetail | null>(null);

  // Timer countdown hook
  useEffect(() => {
    if (!activeTestSession?.deadline_at) return;

    const interval = setInterval(() => {
      const deadline = new Date(activeTestSession.deadline_at!).getTime();
      const now = new Date().getTime();
      const diff = Math.max(0, Math.floor((deadline - now) / 1000));
      setTimeRemainingSeconds(diff);

      if (diff <= 0) {
        clearInterval(interval);
        handleAutoSubmitOnTimeout();
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [activeTestSession]);

  const handleStartAttempt = async (asmtId: string) => {
    try {
      const session = await assessmentService.startAttempt(asmtId);
      setActiveTestSession(session);
      setCurrentQuestionIndex(0);
      setStudentAnswers({});
      setTestCompletedSummary(null);
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to start assessment attempt.');
    }
  };

  const handleSelectOption = (questionId: string, optionId: string, isMulti: boolean) => {
    let currentSelected: string[] = studentAnswers[questionId]?.selected_option_ids || [];
    if (isMulti) {
      if (currentSelected.includes(optionId)) {
        currentSelected = currentSelected.filter((id) => id !== optionId);
      } else {
        currentSelected = [...currentSelected, optionId];
      }
    } else {
      currentSelected = [optionId];
    }

    const newPayload = { selected_option_ids: currentSelected };
    setStudentAnswers((prev) => ({ ...prev, [questionId]: newPayload }));
    debouncedAutosave(questionId, newPayload);
  };

  const handleTextAnswerChange = (questionId: string, text: string) => {
    const newPayload = { answer_text: text };
    setStudentAnswers((prev) => ({ ...prev, [questionId]: newPayload }));
    debouncedAutosave(questionId, newPayload);
  };

  const debouncedAutosave = async (questionId: string, payload: Record<string, any>) => {
    if (!activeTestSession) return;
    setAutosaveStatus('Saving...');
    try {
      await assessmentService.saveResponse(activeTestSession.attempt_id, questionId, payload);
      setAutosaveStatus('All changes saved');
    } catch (err) {
      setAutosaveStatus('Error saving');
    }
  };

  const handleSubmitAttempt = async () => {
    if (!activeTestSession) return;
    try {
      const result = await assessmentService.submitAttempt(activeTestSession.attempt_id);
      setTestCompletedSummary(result);
      setActiveTestSession(null);
      setShowSubmitConfirmModal(false);
      refetchAvailable();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to submit assessment.');
    }
  };

  const handleAutoSubmitOnTimeout = async () => {
    if (!activeTestSession) return;
    try {
      const result = await assessmentService.submitAttempt(activeTestSession.attempt_id);
      setTestCompletedSummary(result);
      setActiveTestSession(null);
      refetchAvailable();
    } catch (err) {
      console.error('Auto submission failed', err);
    }
  };

  // -------------------------------------------------------------------------
  // State: Faculty Evaluation Workspace
  // -------------------------------------------------------------------------
  const [evalAssessmentId, setEvalAssessmentId] = useState<string>('');
  const [selectedSubmission, setSelectedSubmission] = useState<AttemptDetail | null>(null);
  const [manualMarks, setManualMarks] = useState<Record<string, number>>({});
  const [manualFeedback, setManualFeedback] = useState<Record<string, string>>({});
  const [verificationRemarks, setVerificationRemarks] = useState('');

  const { data: submissions = [], isLoading: isLoadingSubmissions, refetch: refetchSubmissions } = useQuery({
    queryKey: ['assessment-submissions', evalAssessmentId],
    queryFn: () => assessmentService.listSubmissions(evalAssessmentId),
    enabled: !!evalAssessmentId,
  });

  const evaluateMutation = useMutation({
    mutationFn: ({ attemptId, payload }: { attemptId: string; payload: any }) =>
      assessmentService.evaluateSubmission(attemptId, payload),
    onSuccess: (updated) => {
      setSelectedSubmission(updated);
      refetchSubmissions();
      alert('Evaluations saved successfully.');
    },
  });

  const releaseResultMutation = useMutation({
    mutationFn: ({ attemptId, payload }: { attemptId: string; payload: any }) =>
      assessmentService.releaseVerifiedResult(attemptId, payload),
    onSuccess: (updated) => {
      setSelectedSubmission(updated);
      refetchSubmissions();
      alert('Assessment marks verified and published to Phase 04 official academic records!');
    },
    onError: (err: any) => {
      alert(err?.response?.data?.detail || 'Failed to release verified result.');
    },
  });

  // -------------------------------------------------------------------------
  // State: Analytics & Engagement Telemetry
  // -------------------------------------------------------------------------
  const [analyticsAssessmentId, setAnalyticsAssessmentId] = useState<string>('');

  const { data: analyticsData } = useQuery({
    queryKey: ['assessment-analytics', analyticsAssessmentId],
    queryFn: () => assessmentService.getAssessmentAnalytics(analyticsAssessmentId),
    enabled: !!analyticsAssessmentId,
  });

  const { data: engagementSummary } = useQuery({
    queryKey: ['assessment-engagement', analyticsAssessmentId],
    queryFn: () => assessmentService.getEngagementSummary(analyticsAssessmentId),
    enabled: !!analyticsAssessmentId,
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 py-8">
      {/* ===================================================================== */}
      {/* HEADER SECTION */}
      {/* ===================================================================== */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-indigo-400 text-sm font-semibold uppercase tracking-wider mb-1">
              <ShieldCheck className="w-4 h-4" />
              Module 04: Phase 05/11
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Intelligent Assessment & Attentiveness Engine
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Multi-modal question authoring, scheduled test delivery, autosave attempts, rubric grading & observable learning engagement telemetry.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <span className="px-3 py-1 bg-indigo-950 text-indigo-300 border border-indigo-800 rounded-full text-xs font-semibold">
              Role: {profile?.role || 'STUDENT'}
            </span>
            {isFacultyOrAdmin && (
              <span className="px-3 py-1 bg-emerald-950 text-emerald-300 border border-emerald-800 rounded-full text-xs font-semibold flex items-center gap-1">
                <CheckCircle className="w-3.5 h-3.5" /> Faculty Authoring Mode
              </span>
            )}
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex flex-wrap gap-2 mt-6 pt-4 border-t border-slate-800">
          {isFacultyOrAdmin && (
            <button
              onClick={() => setActiveTab('assessments')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'assessments'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              <FileCheck className="w-4 h-4" /> Assessment Delivery Builder
            </button>
          )}

          {isFacultyOrAdmin && (
            <button
              onClick={() => setActiveTab('questions')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'questions'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              <BookOpen className="w-4 h-4" /> Question Bank
            </button>
          )}

          <button
            onClick={() => setActiveTab('student_tests')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'student_tests'
                ? 'bg-indigo-600 text-white'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            <Play className="w-4 h-4" /> Student Assessment Workspace
          </button>

          {isFacultyOrAdmin && (
            <button
              onClick={() => setActiveTab('evaluations')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'evaluations'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              <Award className="w-4 h-4" /> Faculty Grading & Verification
            </button>
          )}

          <button
            onClick={() => setActiveTab('analytics')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'analytics'
                ? 'bg-indigo-600 text-white'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            <BarChart2 className="w-4 h-4" /> Analytics & Engagement Telemetry
          </button>
        </div>
      </div>

      {/* ===================================================================== */}
      {/* TAB 1: QUESTION BANK & ITEM AUTHORING */}
      {/* ===================================================================== */}
      {activeTab === 'questions' && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-900 border border-slate-800 rounded-xl p-4">
            <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
              <div className="flex items-center gap-2 text-sm text-slate-400">
                <Filter className="w-4 h-4" /> Subject:
              </div>
              <select
                value={selectedSubjectId}
                onChange={(e) => setSelectedSubjectId(e.target.value)}
                className="bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-1.5 text-sm"
              >
                {subjects.map((sub: AcademicSubject) => (
                  <option key={sub.id} value={sub.id}>
                    {sub.code} - {sub.name}
                  </option>
                ))}
              </select>

              <select
                value={questionTypeFilter}
                onChange={(e) => setQuestionTypeFilter(e.target.value)}
                className="bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-1.5 text-sm"
              >
                <option value="">All Question Types</option>
                <option value="MCQ">Multiple Choice (MCQ)</option>
                <option value="MULTI_SELECT">Multi-Select</option>
                <option value="TRUE_FALSE">True / False</option>
                <option value="SHORT_ANSWER">Short Answer</option>
                <option value="LONG_ANSWER">Long Descriptive</option>
                <option value="CODE_RESPONSE">Code Response</option>
              </select>

              <select
                value={difficultyFilter}
                onChange={(e) => setDifficultyFilter(e.target.value)}
                className="bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-1.5 text-sm"
              >
                <option value="">All Difficulties</option>
                <option value="EASY">Easy</option>
                <option value="MEDIUM">Medium</option>
                <option value="HARD">Hard</option>
              </select>
            </div>

            <button
              onClick={() => setShowCreateQuestionModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors w-full sm:w-auto justify-center"
            >
              <Plus className="w-4 h-4" /> Add New Question
            </button>
          </div>

          {/* Question List */}
          {isLoadingQuestions ? (
            <div className="p-8 text-center text-slate-400">Loading questions from Question Bank...</div>
          ) : questions.length === 0 ? (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center">
              <BookOpen className="w-12 h-12 text-slate-600 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-white">No questions found</h3>
              <p className="text-slate-400 text-sm mt-1 max-w-md mx-auto">
                No questions exist yet for this subject and filter criteria. Create your first curriculum-aligned item using the button above.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {questions.map((q, idx) => (
                <div
                  key={q.id}
                  className="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-xl p-5 transition-colors space-y-3"
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-slate-400 bg-slate-800 px-2 py-0.5 rounded">
                        #{idx + 1}
                      </span>
                      <span className="text-xs font-semibold px-2.5 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
                        {q.question_type}
                      </span>
                      <span
                        className={`text-xs font-semibold px-2.5 py-0.5 rounded ${
                          q.difficulty === 'EASY'
                            ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                            : q.difficulty === 'MEDIUM'
                            ? 'bg-amber-950 text-amber-400 border border-amber-800'
                            : 'bg-rose-950 text-rose-400 border border-rose-800'
                        }`}
                      >
                        {q.difficulty}
                      </span>
                      <span className="text-xs font-semibold px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800">
                        Bloom: {q.bloom_level}
                      </span>
                    </div>

                    <div className="text-sm font-semibold text-slate-300">
                      {q.default_marks} Marks
                    </div>
                  </div>

                  <p className="text-white text-base font-medium">{q.question_text}</p>

                  {/* Options Preview for MCQ / True False */}
                  {q.options && q.options.length > 0 && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-2">
                      {q.options.map((opt) => (
                        <div
                          key={opt.id}
                          className={`flex items-center justify-between text-xs p-2.5 rounded-lg border ${
                            opt.is_correct
                              ? 'bg-emerald-950/40 border-emerald-800 text-emerald-200'
                              : 'bg-slate-800/40 border-slate-800 text-slate-400'
                          }`}
                        >
                          <span>{opt.option_text}</span>
                          {opt.is_correct && (
                            <span className="flex items-center gap-1 font-semibold text-emerald-400">
                              <CheckCircle className="w-3.5 h-3.5" /> Correct Key
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  {q.code_template && (
                    <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 font-mono text-xs text-slate-300">
                      <div className="text-slate-500 mb-1">Code Template ({q.code_language}):</div>
                      <pre>{q.code_template}</pre>
                    </div>
                  )}

                  {q.explanation && (
                    <div className="text-xs text-slate-400 bg-slate-800/30 p-2.5 rounded border border-slate-800/60">
                      <span className="text-slate-300 font-medium">Faculty Explanation: </span>
                      {q.explanation}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ===================================================================== */}
      {/* TAB 2: ASSESSMENT BUILDER & DELIVERY */}
      {/* ===================================================================== */}
      {activeTab === 'assessments' && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-900 border border-slate-800 rounded-xl p-4">
            <div className="flex items-center gap-3">
              <span className="text-sm text-slate-400">Subject:</span>
              <select
                value={selectedSubjectId}
                onChange={(e) => setSelectedSubjectId(e.target.value)}
                className="bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-1.5 text-sm"
              >
                {subjects.map((sub: AcademicSubject) => (
                  <option key={sub.id} value={sub.id}>
                    {sub.code} - {sub.name}
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={() => setShowCreateAsmtModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors"
            >
              <Plus className="w-4 h-4" /> Create Assessment Session
            </button>
          </div>

          {isLoadingAssessments ? (
            <div className="p-8 text-center text-slate-400">Loading assessments...</div>
          ) : assessments.length === 0 ? (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center">
              <FileCheck className="w-12 h-12 text-slate-600 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-white">No assessments configured</h3>
              <p className="text-slate-400 text-sm mt-1 max-w-md mx-auto">
                No online assessments exist for this subject. Create a new assessment, map questions from the bank, and publish it for students.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {assessments.map((asmt) => (
                <div
                  key={asmt.id}
                  className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col justify-between space-y-4"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold px-2.5 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
                        {asmt.assessment_type}
                      </span>
                      <span
                        className={`text-xs font-semibold px-2.5 py-0.5 rounded ${
                          asmt.status === 'PUBLISHED'
                            ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                            : asmt.status === 'DRAFT'
                            ? 'bg-amber-950 text-amber-400 border border-amber-800'
                            : 'bg-slate-800 text-slate-400 border border-slate-700'
                        }`}
                      >
                        {asmt.status}
                      </span>
                    </div>

                    <h3 className="text-lg font-bold text-white">{asmt.assessment_name}</h3>
                    <p className="text-xs text-slate-400">{asmt.instructions || 'No instructions provided.'}</p>
                  </div>

                  <div className="grid grid-cols-3 gap-2 py-3 border-y border-slate-800 text-center text-xs">
                    <div>
                      <div className="text-slate-500">Max Marks</div>
                      <div className="text-white font-bold text-sm">{asmt.maximum_marks}</div>
                    </div>
                    <div>
                      <div className="text-slate-500">Duration</div>
                      <div className="text-white font-bold text-sm">
                        {asmt.duration_minutes ? `${asmt.duration_minutes}m` : 'Untimed'}
                      </div>
                    </div>
                    <div>
                      <div className="text-slate-500">Attempts</div>
                      <div className="text-white font-bold text-sm">{asmt.attempt_limit} Limit</div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between gap-2 pt-1">
                    <button
                      onClick={() => {
                        setEvalAssessmentId(asmt.id);
                        setActiveTab('evaluations');
                      }}
                      className="text-xs text-indigo-400 hover:text-indigo-300 font-medium"
                    >
                      View Submissions &rarr;
                    </button>

                    <div className="flex items-center gap-2">
                      {asmt.status === 'DRAFT' && (
                        <button
                          onClick={() => publishAssessmentMutation.mutate(asmt.id)}
                          className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-medium transition-colors"
                        >
                          Publish
                        </button>
                      )}
                      {asmt.status === 'PUBLISHED' && (
                        <button
                          onClick={() => closeAssessmentMutation.mutate(asmt.id)}
                          className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-medium transition-colors"
                        >
                          Close Session
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ===================================================================== */}
      {/* TAB 3: STUDENT ASSESSMENT WORKSPACE */}
      {/* ===================================================================== */}
      {activeTab === 'student_tests' && (
        <div className="space-y-6">
          {/* Active Test Session View */}
          {activeTestSession ? (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
              {/* Sticky Top Header with Timer */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
                <div>
                  <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">
                    Continuous Online Evaluation Session
                  </span>
                  <h2 className="text-xl font-bold text-white mt-0.5">{activeTestSession.assessment_name}</h2>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-xs text-slate-400 font-mono">
                    Status: <span className="text-emerald-400 font-semibold">{autosaveStatus}</span>
                  </div>

                  {timeRemainingSeconds !== null && (
                    <div
                      className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border font-mono text-sm font-bold ${
                        timeRemainingSeconds < 300
                          ? 'bg-rose-950 text-rose-400 border-rose-800 animate-pulse'
                          : 'bg-slate-800 text-white border-slate-700'
                      }`}
                    >
                      <Clock className="w-4 h-4 text-amber-400" />
                      {Math.floor(timeRemainingSeconds / 60)}:
                      {String(timeRemainingSeconds % 60).padStart(2, '0')}
                    </div>
                  )}

                  <button
                    onClick={() => setShowSubmitConfirmModal(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-semibold transition-colors"
                  >
                    <Send className="w-4 h-4" /> Submit Assessment
                  </button>
                </div>
              </div>

              {/* Question Navigator */}
              <div className="flex items-center gap-2 overflow-x-auto pb-2">
                {activeTestSession.questions.map((q, idx) => {
                  const isAnswered = !!studentAnswers[q.id];
                  const isCurrent = idx === currentQuestionIndex;
                  return (
                    <button
                      key={q.id}
                      onClick={() => setCurrentQuestionIndex(idx)}
                      className={`w-9 h-9 rounded-lg font-bold text-xs flex items-center justify-center transition-colors ${
                        isCurrent
                          ? 'bg-indigo-600 text-white ring-2 ring-indigo-400'
                          : isAnswered
                          ? 'bg-emerald-950 text-emerald-300 border border-emerald-700'
                          : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                      }`}
                    >
                      {idx + 1}
                    </button>
                  );
                })}
              </div>

              {/* Current Question Display */}
              {(() => {
                const q = activeTestSession.questions[currentQuestionIndex];
                if (!q) return null;

                const selectedOptionIds: string[] = studentAnswers[q.id]?.selected_option_ids || [];
                const currentText = studentAnswers[q.id]?.answer_text || '';

                return (
                  <div className="space-y-4 bg-slate-950/60 p-6 rounded-xl border border-slate-800">
                    <div className="flex items-center justify-between text-xs text-slate-400">
                      <span>
                        Question {currentQuestionIndex + 1} of {activeTestSession.questions.length}
                      </span>
                      <span className="font-semibold text-slate-300">{q.marks_allocated} Marks</span>
                    </div>

                    <h3 className="text-lg font-semibold text-white">{q.question_text}</h3>

                    {/* Options for MCQ / Multi Select */}
                    {q.options && q.options.length > 0 && (
                      <div className="space-y-2 pt-2">
                        {q.options.map((opt) => {
                          const isSelected = selectedOptionIds.includes(opt.id);
                          return (
                            <button
                              key={opt.id}
                              onClick={() =>
                                handleSelectOption(q.id, opt.id, q.question_type === 'MULTI_SELECT')
                              }
                              className={`w-full text-left p-3.5 rounded-lg border text-sm transition-all flex items-center justify-between ${
                                isSelected
                                  ? 'bg-indigo-950/60 border-indigo-600 text-white font-medium shadow-sm'
                                  : 'bg-slate-900 border-slate-800 text-slate-300 hover:border-slate-700'
                              }`}
                            >
                              <span>{opt.option_text}</span>
                              <div
                                className={`w-5 h-5 rounded-full border flex items-center justify-center ${
                                  isSelected
                                    ? 'border-indigo-500 bg-indigo-600 text-white'
                                    : 'border-slate-600'
                                }`}
                              >
                                {isSelected && <CheckCircle className="w-3.5 h-3.5" />}
                              </div>
                            </button>
                          );
                        })}
                      </div>
                    )}

                    {/* Descriptive Text Input */}
                    {(q.question_type === 'SHORT_ANSWER' || q.question_type === 'LONG_ANSWER') && (
                      <div className="pt-2">
                        <textarea
                          rows={q.question_type === 'LONG_ANSWER' ? 6 : 3}
                          value={currentText}
                          onChange={(e) => handleTextAnswerChange(q.id, e.target.value)}
                          placeholder="Type your structured explanation or response here..."
                          className="w-full bg-slate-900 border border-slate-800 focus:border-indigo-600 rounded-lg p-3 text-white text-sm focus:outline-none"
                        />
                      </div>
                    )}

                    {/* Code Response Editor Area */}
                    {q.question_type === 'CODE_RESPONSE' && (
                      <div className="pt-2 space-y-2">
                        <div className="text-xs text-slate-400 font-mono">
                          Language: {q.code_language || 'python'}
                        </div>
                        <textarea
                          rows={8}
                          value={currentText || q.code_template || ''}
                          onChange={(e) => handleTextAnswerChange(q.id, e.target.value)}
                          placeholder="Write executable solution code..."
                          className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-600 rounded-lg p-3 text-emerald-400 font-mono text-sm focus:outline-none"
                        />
                      </div>
                    )}

                    {/* Navigation Buttons */}
                    <div className="flex items-center justify-between pt-4 border-t border-slate-800">
                      <button
                        disabled={currentQuestionIndex === 0}
                        onClick={() => setCurrentQuestionIndex((prev) => Math.max(0, prev - 1))}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white disabled:opacity-40"
                      >
                        <ArrowLeft className="w-4 h-4" /> Previous
                      </button>

                      <button
                        disabled={currentQuestionIndex === activeTestSession.questions.length - 1}
                        onClick={() =>
                          setCurrentQuestionIndex((prev) =>
                            Math.min(activeTestSession.questions.length - 1, prev + 1)
                          )
                        }
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-white disabled:opacity-40"
                      >
                        Next <ArrowRight className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                );
              })()}
            </div>
          ) : testCompletedSummary ? (
            /* Test Completed Summary Screen */
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center max-w-xl mx-auto space-y-4">
              <CheckCircle className="w-16 h-16 text-emerald-400 mx-auto" />
              <h2 className="text-2xl font-bold text-white">Assessment Submitted Successfully!</h2>
              <p className="text-slate-400 text-sm">
                Your responses have been recorded with cryptographic evidence capture and submitted for evaluation.
              </p>

              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 grid grid-cols-2 gap-4 text-center my-4">
                <div>
                  <div className="text-xs text-slate-500">Attempt Status</div>
                  <div className="text-sm font-bold text-emerald-400">{testCompletedSummary.attempt_status}</div>
                </div>
                <div>
                  <div className="text-xs text-slate-500">Responses Recorded</div>
                  <div className="text-sm font-bold text-white">
                    {testCompletedSummary.responses?.length || 0}
                  </div>
                </div>
              </div>

              <button
                onClick={() => setTestCompletedSummary(null)}
                className="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-semibold transition-colors"
              >
                Return to Available Tests
              </button>
            </div>
          ) : (
            /* Available Assessments for Student */
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-bold text-white">Your Scheduled & Practice Assessments</h2>
                <button
                  onClick={() => refetchAvailable()}
                  className="text-xs text-indigo-400 hover:text-indigo-300 font-medium"
                >
                  Refresh Available
                </button>
              </div>

              {isLoadingAvailable ? (
                <div className="p-8 text-center text-slate-400">Loading available assessments...</div>
              ) : availableAssessments.length === 0 ? (
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center">
                  <Play className="w-12 h-12 text-slate-600 mx-auto mb-3" />
                  <h3 className="text-lg font-semibold text-white">No active assessments right now</h3>
                  <p className="text-slate-400 text-sm mt-1 max-w-md mx-auto">
                    You have no scheduled continuous evaluations or practice assessments currently published for your enrolled subjects.
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {availableAssessments.map((item) => {
                    const asmt = item.assessment;
                    return (
                      <div
                        key={asmt.id}
                        className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col justify-between space-y-4"
                      >
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-semibold px-2.5 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
                              {asmt.assessment_type}
                            </span>
                            <span className="text-xs text-slate-400">
                              Attempts: {item.completed_attempts} / {item.attempt_limit}
                            </span>
                          </div>

                          <h3 className="text-lg font-bold text-white">{asmt.assessment_name}</h3>
                          <p className="text-xs text-slate-400">{asmt.instructions || 'No special instructions.'}</p>
                        </div>

                        <div className="grid grid-cols-2 gap-2 py-3 border-y border-slate-800 text-center text-xs">
                          <div>
                            <div className="text-slate-500">Maximum Marks</div>
                            <div className="text-white font-bold">{asmt.maximum_marks}</div>
                          </div>
                          <div>
                            <div className="text-slate-500">Allocated Time</div>
                            <div className="text-white font-bold">
                              {asmt.duration_minutes ? `${asmt.duration_minutes} Mins` : 'Untimed'}
                            </div>
                          </div>
                        </div>

                        <div>
                          {item.can_attempt ? (
                            <button
                              onClick={() => handleStartAttempt(asmt.id)}
                              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-semibold transition-colors"
                            >
                              <Play className="w-4 h-4" /> Start / Resume Assessment
                            </button>
                          ) : (
                            <div className="w-full text-center py-2 bg-slate-800/60 rounded-lg text-xs font-medium text-slate-500">
                              Attempt limit reached or outside test window
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ===================================================================== */}
      {/* TAB 4: FACULTY GRADING & VERIFICATION */}
      {/* ===================================================================== */}
      {activeTab === 'evaluations' && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-900 border border-slate-800 rounded-xl p-4">
            <div className="flex items-center gap-3">
              <span className="text-sm text-slate-400">Assessment:</span>
              <select
                value={evalAssessmentId}
                onChange={(e) => setEvalAssessmentId(e.target.value)}
                className="bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-1.5 text-sm"
              >
                <option value="">-- Select an Assessment --</option>
                {assessments.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.assessment_name} ({a.assessment_type})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {!evalAssessmentId ? (
            <div className="p-12 text-center text-slate-400 bg-slate-900 border border-slate-800 rounded-xl">
              Please select an assessment above to review student submissions and grade descriptive responses.
            </div>
          ) : isLoadingSubmissions ? (
            <div className="p-8 text-center text-slate-400">Loading student submissions...</div>
          ) : submissions.length === 0 ? (
            <div className="p-12 text-center text-slate-400 bg-slate-900 border border-slate-800 rounded-xl">
              No student attempts submitted yet for this assessment session.
            </div>
          ) : (
            <div className="space-y-4">
              <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                <table className="w-full text-left text-sm">
                  <thead className="bg-slate-950 text-slate-400 text-xs uppercase border-b border-slate-800">
                    <tr>
                      <th className="px-4 py-3">Student ID</th>
                      <th className="px-4 py-3">Attempt #</th>
                      <th className="px-4 py-3">Status</th>
                      <th className="px-4 py-3">Marks Obtained</th>
                      <th className="px-4 py-3">Evaluation Status</th>
                      <th className="px-4 py-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-slate-300">
                    {submissions.map((sub) => (
                      <tr key={sub.id} className="hover:bg-slate-850">
                        <td className="px-4 py-3 font-mono text-xs">{sub.student_id.slice(0, 8)}...</td>
                        <td className="px-4 py-3">Attempt {sub.attempt_number}</td>
                        <td className="px-4 py-3">
                          <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                            {sub.attempt_status}
                          </span>
                        </td>
                        <td className="px-4 py-3 font-semibold text-white">
                          {sub.marks_obtained !== null ? `${sub.marks_obtained} / ${sub.total_marks}` : 'Pending'}
                        </td>
                        <td className="px-4 py-3">
                          <span
                            className={`text-xs px-2.5 py-0.5 rounded font-semibold ${
                              sub.evaluation_status === 'EVALUATED'
                                ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                                : 'bg-amber-950 text-amber-400 border border-amber-800'
                            }`}
                          >
                            {sub.evaluation_status}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right">
                          <button
                            onClick={() => setSelectedSubmission(sub)}
                            className="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-medium transition-colors"
                          >
                            Review & Grade
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Submission Evaluation Drawer */}
          {selectedSubmission && (
            <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50 overflow-y-auto">
              <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-3xl w-full p-6 space-y-6 max-h-[90vh] overflow-y-auto">
                <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                  <div>
                    <h3 className="text-lg font-bold text-white">Faculty Grading & Evaluation</h3>
                    <p className="text-xs text-slate-400 font-mono">Attempt ID: {selectedSubmission.id}</p>
                  </div>
                  <button
                    onClick={() => setSelectedSubmission(null)}
                    className="p-1 rounded text-slate-400 hover:text-white"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                {/* Question Responses */}
                <div className="space-y-4">
                  {selectedSubmission.responses.map((resp, idx) => (
                    <div key={resp.id} className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-semibold text-slate-400">Response #{idx + 1}</span>
                        <span
                          className={`px-2 py-0.5 rounded text-xs font-semibold ${
                            resp.is_auto_evaluated
                              ? 'bg-purple-950 text-purple-300'
                              : 'bg-amber-950 text-amber-300'
                          }`}
                        >
                          {resp.is_auto_evaluated ? 'Auto-Graded' : 'Faculty Review'}
                        </span>
                      </div>

                      <div className="text-xs text-slate-300 font-mono bg-slate-900 p-2.5 rounded border border-slate-800">
                        Payload: {JSON.stringify(resp.response_payload)}
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                        <div>
                          <label className="text-xs text-slate-400 block mb-1">Marks Awarded</label>
                          <input
                            type="number"
                            step="0.5"
                            defaultValue={resp.marks_awarded ?? 0}
                            onChange={(e) =>
                              setManualMarks((prev) => ({
                                ...prev,
                                [resp.question_id]: parseFloat(e.target.value) || 0,
                              }))
                            }
                            className="bg-slate-900 border border-slate-700 text-white rounded px-3 py-1.5 text-sm w-full"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-slate-400 block mb-1">Feedback</label>
                          <input
                            type="text"
                            defaultValue={resp.feedback ?? ''}
                            onChange={(e) =>
                              setManualFeedback((prev) => ({
                                ...prev,
                                [resp.question_id]: e.target.value,
                              }))
                            }
                            placeholder="Optional feedback..."
                            className="bg-slate-900 border border-slate-700 text-white rounded px-3 py-1.5 text-sm w-full"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Save Evaluation Action */}
                <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                  <button
                    onClick={() => {
                      const payload = {
                        evaluations: selectedSubmission.responses.map((r) => ({
                          question_id: r.question_id,
                          marks_awarded: manualMarks[r.question_id] ?? r.marks_awarded ?? 0,
                          feedback: manualFeedback[r.question_id] ?? r.feedback ?? '',
                        })),
                        overall_remarks: 'Graded by faculty.',
                      };
                      evaluateMutation.mutate({ attemptId: selectedSubmission.id, payload });
                    }}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-semibold transition-colors"
                  >
                    Save Evaluations
                  </button>
                </div>

                {/* Phase 04 Official Record Publishing Section */}
                <div className="bg-slate-950 p-4 rounded-xl border border-indigo-900/60 space-y-3">
                  <div className="flex items-center gap-2 text-indigo-400 text-sm font-semibold">
                    <ShieldCheck className="w-4 h-4" /> Official Phase 04 Academic Record Publishing
                  </div>
                  <p className="text-xs text-slate-400">
                    Publishing writes verified marks directly to institutional gradebooks (`student_assessment_records`) with cryptographic audit logging. Practice tests are strictly excluded.
                  </p>
                  <input
                    type="text"
                    value={verificationRemarks}
                    onChange={(e) => setVerificationRemarks(e.target.value)}
                    placeholder="Enter faculty verification remarks (e.g. Verified by Prof. Knuth)..."
                    className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded px-3 py-2"
                  />
                  <button
                    onClick={() =>
                      releaseResultMutation.mutate({
                        attemptId: selectedSubmission.id,
                        payload: {
                          publish_to_official_records: true,
                          verification_remarks: verificationRemarks || 'Verified by Faculty',
                        },
                      })
                    }
                    className="w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold transition-colors"
                  >
                    Verify & Release to Official Academic Gradebook
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ===================================================================== */}
      {/* TAB 5: ANALYTICS & LEARNING ENGAGEMENT TELEMETRY */}
      {/* ===================================================================== */}
      {activeTab === 'analytics' && (
        <div className="space-y-6">
          {/* Scientific Non-Attention Disclaimer Alert Box */}
          <div className="bg-amber-950/40 border border-amber-800/80 rounded-xl p-5 flex items-start gap-4">
            <ShieldAlert className="w-6 h-6 text-amber-400 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <h4 className="text-sm font-bold text-amber-300">
                SCIENTIFIC GOVERNANCE & PRIVACY DISCLAIMER
              </h4>
              <p className="text-xs text-amber-200/90 leading-relaxed">
                Learning engagement telemetry reflects observable human-computer interactions (events, timestamps, revisions). These behavioral traces must NEVER be equated with internal cognitive attention, mental concentration, or student intelligence.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 bg-slate-900 border border-slate-800 rounded-xl p-4">
            <span className="text-sm text-slate-400">Select Assessment:</span>
            <select
              value={analyticsAssessmentId}
              onChange={(e) => setAnalyticsAssessmentId(e.target.value)}
              className="bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-1.5 text-sm"
            >
              <option value="">-- Select an Assessment --</option>
              {assessments.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.assessment_name}
                </option>
              ))}
            </select>
          </div>

          {analyticsData && (
            <div className="space-y-6">
              {/* Analytics Metric Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl text-center">
                  <div className="text-xs text-slate-400">Total Attempts</div>
                  <div className="text-2xl font-bold text-white mt-1">{analyticsData.total_attempts}</div>
                </div>
                <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl text-center">
                  <div className="text-xs text-slate-400">Completed Attempts</div>
                  <div className="text-2xl font-bold text-indigo-400 mt-1">{analyticsData.completed_attempts}</div>
                </div>
                <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl text-center">
                  <div className="text-xs text-slate-400">Average Score</div>
                  <div className="text-2xl font-bold text-emerald-400 mt-1">
                    {analyticsData.average_score.toFixed(1)}
                  </div>
                </div>
                <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl text-center">
                  <div className="text-xs text-slate-400">Pass Rate</div>
                  <div className="text-2xl font-bold text-amber-400 mt-1">
                    {analyticsData.pass_rate_percentage.toFixed(1)}%
                  </div>
                </div>
              </div>

              {/* Learning Outcome Coverage */}
              {analyticsData.learning_outcome_coverage && analyticsData.learning_outcome_coverage.length > 0 && (
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Layers className="w-4 h-4 text-indigo-400" /> Syllabus Learning Outcome Coverage
                  </h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-slate-950 text-slate-400 uppercase">
                        <tr>
                          <th className="px-3 py-2">Code</th>
                          <th className="px-3 py-2">Outcome Description</th>
                          <th className="px-3 py-2">Bloom Level</th>
                          <th className="px-3 py-2 text-right">Questions</th>
                          <th className="px-3 py-2 text-right">Marks</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800 text-slate-300">
                        {analyticsData.learning_outcome_coverage.map((lo, idx) => (
                          <tr key={idx}>
                            <td className="px-3 py-2 font-mono font-bold text-indigo-400">{lo.outcome_code}</td>
                            <td className="px-3 py-2">{lo.description}</td>
                            <td className="px-3 py-2">
                              <span className="px-2 py-0.5 rounded bg-purple-950 text-purple-300">
                                {lo.bloom_level}
                              </span>
                            </td>
                            <td className="px-3 py-2 text-right font-semibold text-white">{lo.questions_mapped}</td>
                            <td className="px-3 py-2 text-right font-semibold text-white">{lo.marks_allocated}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Engagement Telemetry Summary */}
              {engagementSummary && (
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-bold text-white flex items-center gap-2">
                      <Activity className="w-4 h-4 text-emerald-400" /> Observable Telemetry Events
                    </h3>
                    <span className="text-xs text-slate-400 font-mono">
                      Total Signals: {engagementSummary.total_events}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                    <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                      <div className="text-xs text-slate-500">Average Events / Attempt</div>
                      <div className="text-lg font-bold text-white mt-1">
                        {engagementSummary.average_events_per_attempt.toFixed(1)}
                      </div>
                    </div>
                    <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                      <div className="text-xs text-slate-500">Revisions / Item</div>
                      <div className="text-lg font-bold text-indigo-400 mt-1">
                        {engagementSummary.average_revisions_per_response.toFixed(1)}
                      </div>
                    </div>
                    <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 col-span-2">
                      <div className="text-xs text-slate-500">Scientific Governance Tag</div>
                      <div className="text-xs font-semibold text-emerald-400 mt-1 flex items-center justify-center gap-1">
                        <ShieldCheck className="w-3.5 h-3.5" /> Observable Traces Only (Zero Invasive Sensors)
                      </div>
                    </div>
                  </div>

                  {/* Event Breakdown */}
                  <div className="space-y-1.5 pt-2">
                    <div className="text-xs text-slate-400 font-semibold mb-2">Event Distribution Breakdown</div>
                    {Object.entries(engagementSummary.event_breakdown).map(([event, count]) => (
                      <div key={event} className="flex items-center justify-between text-xs bg-slate-950 p-2 rounded">
                        <span className="font-mono text-slate-300">{event}</span>
                        <span className="font-bold text-white bg-slate-800 px-2 py-0.5 rounded">{count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ===================================================================== */}
      {/* MODAL: CREATE QUESTION */}
      {/* ===================================================================== */}
      {showCreateQuestionModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50 overflow-y-auto">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-2xl w-full p-6 space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-lg font-bold text-white">Add Question to Bank</h3>
              <button
                onClick={() => setShowCreateQuestionModal(false)}
                className="p-1 rounded text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-xs text-slate-400 block mb-1">Question Prompt</label>
                <textarea
                  rows={3}
                  value={qText}
                  onChange={(e) => setQText(e.target.value)}
                  placeholder="Enter detailed question text..."
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded p-2.5 text-sm"
                />
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Type</label>
                  <select
                    value={qType}
                    onChange={(e) => setQType(e.target.value as QuestionType)}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded px-2.5 py-1.5 text-xs"
                  >
                    <option value="MCQ">MCQ</option>
                    <option value="MULTI_SELECT">Multi-Select</option>
                    <option value="TRUE_FALSE">True/False</option>
                    <option value="SHORT_ANSWER">Short Answer</option>
                    <option value="LONG_ANSWER">Long Answer</option>
                    <option value="CODE_RESPONSE">Code</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Difficulty</label>
                  <select
                    value={qDifficulty}
                    onChange={(e) => setQDifficulty(e.target.value as QuestionDifficulty)}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded px-2.5 py-1.5 text-xs"
                  >
                    <option value="EASY">Easy</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HARD">Hard</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Bloom Level</label>
                  <select
                    value={qBloom}
                    onChange={(e) => setQBloom(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded px-2.5 py-1.5 text-xs"
                  >
                    <option value="REMEMBER">Remember</option>
                    <option value="UNDERSTAND">Understand</option>
                    <option value="APPLY">Apply</option>
                    <option value="ANALYZE">Analyze</option>
                    <option value="EVALUATE">Evaluate</option>
                    <option value="CREATE">Create</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Default Marks</label>
                  <input
                    type="number"
                    step="0.5"
                    value={qMarks}
                    onChange={(e) => setQMarks(parseFloat(e.target.value) || 1)}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded px-2.5 py-1.5 text-xs"
                  />
                </div>
              </div>

              {/* Options for MCQ / True False */}
              {(qType === 'MCQ' || qType === 'MULTI_SELECT' || qType === 'TRUE_FALSE') && (
                <div className="space-y-2 pt-2">
                  <div className="text-xs font-semibold text-slate-300">Answer Options & Correct Key:</div>
                  {qOptions.map((opt, idx) => (
                    <div key={idx} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={opt.is_correct}
                        onChange={(e) => {
                          const updated = [...qOptions];
                          if (qType === 'MCQ' || qType === 'TRUE_FALSE') {
                            updated.forEach((o, i) => (o.is_correct = i === idx));
                          } else {
                            updated[idx].is_correct = e.target.checked;
                          }
                          setQOptions(updated);
                        }}
                        className="w-4 h-4 rounded text-indigo-600"
                      />
                      <input
                        type="text"
                        value={opt.option_text}
                        onChange={(e) => {
                          const updated = [...qOptions];
                          updated[idx].option_text = e.target.value;
                          setQOptions(updated);
                        }}
                        placeholder={`Option ${idx + 1}`}
                        className="flex-1 bg-slate-800 border border-slate-700 text-white rounded px-2.5 py-1.5 text-xs"
                      />
                    </div>
                  ))}
                </div>
              )}

              {qType === 'CODE_RESPONSE' && (
                <div className="space-y-2 pt-2">
                  <div>
                    <label className="text-xs text-slate-400 block mb-1">Code Language</label>
                    <input
                      type="text"
                      value={qCodeLang}
                      onChange={(e) => setQCodeLang(e.target.value)}
                      placeholder="e.g. python, javascript, sql"
                      className="w-full bg-slate-800 border border-slate-700 text-white rounded px-2.5 py-1.5 text-xs"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-slate-400 block mb-1">Starter Code Template</label>
                    <textarea
                      rows={3}
                      value={qCodeTemplate}
                      onChange={(e) => setQCodeTemplate(e.target.value)}
                      className="w-full bg-slate-800 border border-slate-700 text-emerald-400 font-mono rounded p-2 text-xs"
                    />
                  </div>
                </div>
              )}

              <div>
                <label className="text-xs text-slate-400 block mb-1">Explanation / Rationale</label>
                <textarea
                  rows={2}
                  value={qExplanation}
                  onChange={(e) => setQExplanation(e.target.value)}
                  placeholder="Rationale shown to students during review..."
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded p-2 text-xs"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
              <button
                onClick={() => setShowCreateQuestionModal(false)}
                className="px-4 py-2 rounded text-xs text-slate-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                disabled={!qText.trim() || createQuestionMutation.isPending}
                onClick={() => {
                  createQuestionMutation.mutate({
                    subject_id: selectedSubjectId,
                    question_text: qText,
                    question_type: qType,
                    difficulty: qDifficulty,
                    bloom_level: qBloom,
                    default_marks: qMarks,
                    explanation: qExplanation,
                    code_language: qType === 'CODE_RESPONSE' ? qCodeLang : undefined,
                    code_template: qType === 'CODE_RESPONSE' ? qCodeTemplate : undefined,
                    options:
                      qType === 'MCQ' || qType === 'MULTI_SELECT' || qType === 'TRUE_FALSE'
                        ? qOptions
                        : undefined,
                  });
                }}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-semibold disabled:opacity-50"
              >
                Save Question to Bank
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ===================================================================== */}
      {/* MODAL: CREATE ASSESSMENT SESSION */}
      {/* ===================================================================== */}
      {showCreateAsmtModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50 overflow-y-auto">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-2xl w-full p-6 space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-lg font-bold text-white">Create Assessment Delivery Session</h3>
              <button
                onClick={() => setShowCreateAsmtModal(false)}
                className="p-1 rounded text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-xs text-slate-400 block mb-1">Assessment Name</label>
                <input
                  type="text"
                  value={asmtName}
                  onChange={(e) => setAsmtName(e.target.value)}
                  placeholder="e.g. Mid-Term Continuous Evaluation 1"
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded px-3 py-2 text-sm"
                />
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Type</label>
                  <select
                    value={asmtType}
                    onChange={(e) => setAsmtType(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded px-2.5 py-1.5 text-xs"
                  >
                    <option value="INTERNAL_TEST">Internal Test</option>
                    <option value="MID_TERM">Mid Term</option>
                    <option value="END_TERM">End Term</option>
                    <option value="QUIZ">Quiz</option>
                    <option value="PRACTICE_TEST">Practice Test</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Max Marks</label>
                  <input
                    type="number"
                    value={asmtMaxMarks}
                    onChange={(e) => setAsmtMaxMarks(parseFloat(e.target.value) || 0)}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded px-2.5 py-1.5 text-xs"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Duration (Mins)</label>
                  <input
                    type="number"
                    value={asmtDuration}
                    onChange={(e) => setAsmtDuration(parseInt(e.target.value) || 0)}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded px-2.5 py-1.5 text-xs"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Attempt Limit</label>
                  <input
                    type="number"
                    value={asmtAttemptLimit}
                    onChange={(e) => setAsmtAttemptLimit(parseInt(e.target.value) || 1)}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded px-2.5 py-1.5 text-xs"
                  />
                </div>
              </div>

              {/* Question Selection for Mapping */}
              <div className="space-y-2 pt-2">
                <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
                  <span>Select Questions from Bank ({selectedQuestionIds.length} chosen)</span>
                  <span
                    className={
                      selectedQuestionsMarksSum === asmtMaxMarks
                        ? 'text-emerald-400 font-bold'
                        : 'text-amber-400 font-bold'
                    }
                  >
                    Sum: {selectedQuestionsMarksSum} / {asmtMaxMarks} Marks
                  </span>
                </div>

                <div className="max-h-48 overflow-y-auto space-y-1.5 bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                  {questions.map((q) => {
                    const isChecked = selectedQuestionIds.includes(q.id);
                    return (
                      <div
                        key={q.id}
                        className="flex items-center justify-between p-2 rounded bg-slate-900 border border-slate-800 text-xs"
                      >
                        <div className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedQuestionIds([...selectedQuestionIds, q.id]);
                              } else {
                                setSelectedQuestionIds(selectedQuestionIds.filter((id) => id !== q.id));
                              }
                            }}
                            className="w-4 h-4 rounded text-indigo-600"
                          />
                          <span className="text-white truncate max-w-sm">{q.question_text}</span>
                        </div>
                        <span className="text-slate-400 font-mono">{q.default_marks} M</span>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div>
                <label className="text-xs text-slate-400 block mb-1">Instructions for Students</label>
                <textarea
                  rows={2}
                  value={asmtInstructions}
                  onChange={(e) => setAsmtInstructions(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded p-2 text-xs"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
              <button
                onClick={() => setShowCreateAsmtModal(false)}
                className="px-4 py-2 rounded text-xs text-slate-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                disabled={!asmtName.trim() || selectedQuestionIds.length === 0 || createAssessmentMutation.isPending}
                onClick={() => {
                  createAssessmentMutation.mutate({
                    subject_id: selectedSubjectId,
                    assessment_name: asmtName,
                    assessment_type: asmtType,
                    academic_year: '2024-2025',
                    semester: 4,
                    maximum_marks: asmtMaxMarks,
                    passing_marks: asmtPassingMarks,
                    is_online_assessment: true,
                    duration_minutes: asmtDuration,
                    attempt_limit: asmtAttemptLimit,
                    instructions: asmtInstructions,
                    question_mappings: selectedQuestionIds.map((qId, idx) => {
                      const q = questions.find((item) => item.id === qId);
                      return {
                        question_id: qId,
                        display_order: idx + 1,
                        marks_allocated: q?.default_marks || 1,
                        required: true,
                      };
                    }),
                  });
                }}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-semibold disabled:opacity-50"
              >
                Create Assessment
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ===================================================================== */}
      {/* MODAL: SUBMIT CONFIRMATION */}
      {/* ===================================================================== */}
      {showSubmitConfirmModal && activeTestSession && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-md w-full p-6 space-y-4 text-center">
            <AlertTriangle className="w-12 h-12 text-amber-400 mx-auto" />
            <h3 className="text-lg font-bold text-white">Submit Assessment Attempt?</h3>
            <p className="text-slate-400 text-xs">
              You have answered {Object.keys(studentAnswers).length} of {activeTestSession.questions.length} questions.
              Once submitted, you cannot change your answers for this attempt session.
            </p>

            <div className="flex items-center justify-center gap-3 pt-3">
              <button
                onClick={() => setShowSubmitConfirmModal(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-semibold"
              >
                Back to Questions
              </button>
              <button
                onClick={handleSubmitAttempt}
                className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold"
              >
                Confirm & Submit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
