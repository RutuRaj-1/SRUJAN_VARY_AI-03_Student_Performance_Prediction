import { apiClient } from '@/lib/api-client';

export type QuestionType =
  | 'MCQ'
  | 'MULTI_SELECT'
  | 'TRUE_FALSE'
  | 'SHORT_ANSWER'
  | 'LONG_ANSWER'
  | 'CODE_RESPONSE';

export type QuestionDifficulty = 'EASY' | 'MEDIUM' | 'HARD';

export type QuestionEvaluationMethod =
  | 'AUTOMATED_EXACT'
  | 'AUTOMATED_PATTERN'
  | 'MANUAL_RUBRIC'
  | 'MANUAL_FACULTY'
  | 'HYBRID';

export type AttemptStatus =
  | 'NOT_STARTED'
  | 'IN_PROGRESS'
  | 'PAUSED'
  | 'SUBMITTED'
  | 'EVALUATED'
  | 'EXPIRED'
  | 'CANCELLED';

export type ResponseEvaluationStatus =
  | 'PENDING'
  | 'AUTO_EVALUATED'
  | 'MANUAL_EVALUATED'
  | 'FACULTY_REVIEW_REQUIRED'
  | 'DISPUTED';

export type LearningEngagementEventType =
  | 'ASSESSMENT_STARTED'
  | 'ASSESSMENT_RESUMED'
  | 'QUESTION_VIEWED'
  | 'ANSWER_INPUT_FOCUSED'
  | 'ANSWER_SAVED'
  | 'ANSWER_REVISED'
  | 'ASSESSMENT_SUBMITTED'
  | 'ASSESSMENT_TIMED_OUT'
  | 'TAB_SWITCH_OBSERVED'
  | 'SESSION_IDLE_DETECTED';

export interface QuestionOption {
  id?: string;
  option_text: string;
  display_order: number;
  is_correct?: boolean;
}

export interface QuestionDetail {
  id: string;
  institution_id: string;
  subject_id: string;
  syllabus_unit_id?: string | null;
  syllabus_topic_id?: string | null;
  learning_outcome_id?: string | null;
  competency_id?: string | null;
  question_text: string;
  question_type: QuestionType;
  difficulty: QuestionDifficulty;
  bloom_level: string;
  default_marks: number;
  evaluation_method: QuestionEvaluationMethod;
  explanation?: string | null;
  code_language?: string | null;
  code_template?: string | null;
  options: QuestionOption[];
  created_at: string;
  updated_at: string;
}

export interface QuestionCreatePayload {
  subject_id: string;
  syllabus_unit_id?: string;
  syllabus_topic_id?: string;
  learning_outcome_id?: string;
  competency_id?: string;
  question_text: string;
  question_type: QuestionType;
  difficulty: QuestionDifficulty;
  bloom_level: string;
  default_marks: number;
  evaluation_method?: QuestionEvaluationMethod;
  explanation?: string;
  expected_answer?: string;
  code_language?: string;
  code_template?: string;
  options?: QuestionOption[];
}

export interface AssessmentQuestionMapping {
  id: string;
  question_id: string;
  display_order: number;
  marks_allocated: number;
  required: boolean;
  question?: QuestionDetail;
}

export interface AssessmentDetail {
  id: string;
  institution_id: string;
  subject_id: string;
  assessment_name: string;
  assessment_type: string;
  academic_year: string;
  semester: number;
  maximum_marks: number;
  passing_marks: number;
  is_online_assessment: boolean;
  duration_minutes?: number | null;
  start_time?: string | null;
  end_time?: string | null;
  instructions?: string | null;
  evaluation_mode: string;
  attempt_limit: number;
  allow_review: boolean;
  status: string;
  question_mappings?: AssessmentQuestionMapping[];
  created_at: string;
  updated_at: string;
}

export interface AssessmentCreatePayload {
  subject_id: string;
  assessment_name: string;
  assessment_type: string;
  academic_year: string;
  semester: number;
  maximum_marks: number;
  passing_marks: number;
  is_online_assessment?: boolean;
  duration_minutes?: number;
  start_time?: string;
  end_time?: string;
  instructions?: string;
  evaluation_mode?: string;
  attempt_limit?: number;
  allow_review?: boolean;
  question_mappings?: {
    question_id: string;
    display_order: number;
    marks_allocated: number;
    required: boolean;
  }[];
  learning_outcome_ids?: string[];
}

export interface StudentQuestionOptionView {
  id: string;
  option_text: string;
  display_order: number;
}

export interface StudentQuestionView {
  id: string;
  question_text: string;
  question_type: QuestionType;
  marks_allocated: number;
  display_order: number;
  required: boolean;
  code_language?: string | null;
  code_template?: string | null;
  options: StudentQuestionOptionView[];
}

export interface AttemptStartResponse {
  attempt_id: string;
  assessment_id: string;
  assessment_name: string;
  duration_minutes?: number | null;
  deadline_at?: string | null;
  started_at: string;
  attempt_number: number;
  questions: StudentQuestionView[];
}

export interface AvailableAssessmentItem {
  assessment: AssessmentDetail;
  can_attempt: boolean;
  completed_attempts: number;
  attempt_limit: number;
  active_attempt_id?: string | null;
  is_window_active: boolean;
}

export interface AssessmentResponseItem {
  id: string;
  question_id: string;
  response_payload: Record<string, any>;
  marks_awarded?: number | null;
  feedback?: string | null;
  evaluation_status: ResponseEvaluationStatus;
  is_auto_evaluated: boolean;
  revision_count: number;
  saved_at: string;
}

export interface AttemptDetail {
  id: string;
  institution_id: string;
  assessment_id: string;
  student_id: string;
  attempt_number: number;
  attempt_status: AttemptStatus;
  started_at: string;
  submitted_at?: string | null;
  deadline_at?: string | null;
  total_marks: number;
  marks_obtained?: number | null;
  evaluation_status: string;
  evaluator_feedback?: string | null;
  responses: AssessmentResponseItem[];
  created_at: string;
  updated_at: string;
}

export interface ItemEvaluationInput {
  question_id: string;
  marks_awarded: number;
  feedback?: string;
}

export interface BatchEvaluationPayload {
  evaluations: ItemEvaluationInput[];
  overall_remarks?: string;
}

export interface ReleaseResultPayload {
  publish_to_official_records: boolean;
  verification_remarks?: string;
}

export interface LearningEngagementSummary {
  assessment_id: string;
  assessment_name: string;
  total_events: number;
  total_attempts: number;
  completed_attempts: number;
  event_breakdown: Record<string, number>;
  average_events_per_attempt: number;
  average_revisions_per_response: number;
  scientific_disclaimer: string;
}

export interface OutcomeCoverageItem {
  outcome_code: string;
  description: string;
  bloom_level: string;
  questions_mapped: number;
  marks_allocated: number;
}

export interface AssessmentAnalyticsResponse {
  assessment_id: string;
  assessment_name: string;
  total_attempts: number;
  completed_attempts: number;
  average_score: number;
  pass_rate_percentage: number;
  highest_score: number;
  lowest_score: number;
  score_distribution: Record<string, number>;
  question_discrimination: Record<string, any>[];
  learning_outcome_coverage: OutcomeCoverageItem[];
}

export const assessmentService = {
  // Question Bank
  listQuestions: async (subjectId?: string, questionType?: string, difficulty?: string): Promise<QuestionDetail[]> => {
    const params = new URLSearchParams();
    if (subjectId) params.append('subject_id', subjectId);
    if (questionType) params.append('question_type', questionType);
    if (difficulty) params.append('difficulty', difficulty);
    return apiClient.get<QuestionDetail[]>(`/assessments/questions?${params.toString()}`);
  },

  getQuestion: async (questionId: string): Promise<QuestionDetail> => {
    return apiClient.get<QuestionDetail>(`/assessments/questions/${questionId}`);
  },

  createQuestion: async (payload: QuestionCreatePayload): Promise<QuestionDetail> => {
    return apiClient.post<QuestionDetail>('/assessments/questions', payload);
  },

  deleteQuestion: async (questionId: string): Promise<void> => {
    await apiClient.delete(`/assessments/questions/${questionId}`);
  },

  // Assessment Configuration & Delivery
  listAssessments: async (subjectId?: string, statusFilter?: string): Promise<AssessmentDetail[]> => {
    const params = new URLSearchParams();
    if (subjectId) params.append('subject_id', subjectId);
    if (statusFilter) params.append('status_filter', statusFilter);
    return apiClient.get<AssessmentDetail[]>(`/assessments?${params.toString()}`);
  },

  getAssessment: async (assessmentId: string): Promise<AssessmentDetail> => {
    return apiClient.get<AssessmentDetail>(`/assessments/${assessmentId}`);
  },

  createAssessment: async (payload: AssessmentCreatePayload): Promise<AssessmentDetail> => {
    return apiClient.post<AssessmentDetail>('/assessments', payload);
  },

  publishAssessment: async (assessmentId: string): Promise<AssessmentDetail> => {
    return apiClient.post<AssessmentDetail>(`/assessments/${assessmentId}/publish`);
  },

  closeAssessment: async (assessmentId: string): Promise<AssessmentDetail> => {
    return apiClient.post<AssessmentDetail>(`/assessments/${assessmentId}/close`);
  },

  // Student Test Session
  getAvailableAssessments: async (): Promise<AvailableAssessmentItem[]> => {
    return apiClient.get<AvailableAssessmentItem[]>('/assessments/available');
  },

  startAttempt: async (assessmentId: string): Promise<AttemptStartResponse> => {
    return apiClient.post<AttemptStartResponse>(`/assessments/${assessmentId}/attempts`);
  },

  saveResponse: async (attemptId: string, questionId: string, responsePayload: Record<string, any>): Promise<AssessmentResponseItem> => {
    return apiClient.put<AssessmentResponseItem>(`/assessments/attempts/${attemptId}/responses`, {
      question_id: questionId,
      response_payload: responsePayload,
    });
  },

  submitAttempt: async (attemptId: string): Promise<AttemptDetail> => {
    return apiClient.post<AttemptDetail>(`/assessments/attempts/${attemptId}/submit`);
  },

  // Faculty Evaluation Workspace
  listSubmissions: async (assessmentId: string): Promise<AttemptDetail[]> => {
    return apiClient.get<AttemptDetail[]>(`/assessments/${assessmentId}/submissions`);
  },

  evaluateSubmission: async (attemptId: string, payload: BatchEvaluationPayload): Promise<AttemptDetail> => {
    return apiClient.post<AttemptDetail>(`/assessments/submissions/${attemptId}/evaluate`, payload);
  },

  releaseVerifiedResult: async (attemptId: string, payload: ReleaseResultPayload): Promise<AttemptDetail> => {
    return apiClient.post<AttemptDetail>(`/assessments/submissions/${attemptId}/release-result`, payload);
  },

  // Analytics & Engagement Telemetry
  getEngagementSummary: async (assessmentId: string): Promise<LearningEngagementSummary> => {
    return apiClient.get<LearningEngagementSummary>(`/assessments/${assessmentId}/engagement-summary`);
  },

  getAssessmentAnalytics: async (assessmentId: string): Promise<AssessmentAnalyticsResponse> => {
    return apiClient.get<AssessmentAnalyticsResponse>(`/assessments/${assessmentId}/analytics`);
  },

  recordEngagementEvent: async (payload: {
    event_type: LearningEngagementEventType;
    assessment_id?: string;
    attempt_id?: string;
    event_metadata?: Record<string, any>;
  }): Promise<void> => {
    await apiClient.post('/assessments/engagement/events', payload);
  },
};
