import { apiClient } from '@/lib/api-client';

export type InterventionType =
  | 'TARGETED_REVISION'
  | 'PRACTICE_SET'
  | 'REMEDIAL_SESSION'
  | 'FACULTY_CONSULTATION'
  | 'PEER_STUDY_SESSION'
  | 'LAB_PRACTICE'
  | 'FORMATIVE_ASSESSMENT'
  | 'STRUCTURED_STUDY_PLAN'
  | 'LEARNING_RESOURCE'
  | 'EVIDENCE_COLLECTION';

export type InterventionPriority = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';

export type InterventionPlanStatus =
  | 'DRAFT'
  | 'PENDING_REVIEW'
  | 'APPROVED'
  | 'ACTIVE'
  | 'COMPLETED'
  | 'REJECTED'
  | 'CANCELLED'
  | 'EXPIRED';

export type InterventionActionStatus =
  | 'PROPOSED'
  | 'ASSIGNED'
  | 'IN_PROGRESS'
  | 'SUBMITTED'
  | 'VERIFIED'
  | 'DECLINED'
  | 'CANCELLED'
  | 'OVERDUE';

export interface InterventionTemplate {
  id: string;
  institution_id: string;
  subject_id?: string | null;
  template_code: string;
  template_name: string;
  intervention_type: InterventionType;
  description?: string | null;
  target_level: string;
  suggested_duration_hours: number;
  suggested_completion_days: number;
  recommended_actions_template: Record<string, any>[];
  required_resources: Record<string, any>[];
  expected_evidence_type?: string | null;
  requires_faculty_review: boolean;
  is_active: boolean;
  created_at: string;
}

export interface InterventionRecommendation {
  id: string;
  institution_id: string;
  student_id: string;
  student_name?: string | null;
  enrollment_number?: string | null;
  subject_id: string;
  subject_name?: string | null;
  subject_code?: string | null;
  topic_id?: string | null;
  topic_name?: string | null;
  learning_outcome_id?: string | null;
  risk_prediction_id?: string | null;
  learning_gap_id?: string | null;
  template_id?: string | null;
  recommendation_type: InterventionType;
  priority: InterventionPriority;
  rationale: string;
  source_evidence_summary: Record<string, any>;
  evidence_sufficiency: string;
  proposed_action_title: string;
  proposed_action_description: string;
  suggested_duration_days: number;
  status: string;
  scientific_disclaimer: string;
  created_at: string;
}

export interface InterventionAction {
  id: string;
  institution_id: string;
  plan_id: string;
  action_order: number;
  action_title: string;
  action_type: string;
  instructions: string;
  resource_references: Record<string, any>[];
  estimated_effort_hours: number;
  due_date?: string | null;
  action_status: InterventionActionStatus;
  student_completion_notes?: string | null;
  student_submission_url?: string | null;
  submitted_at?: string | null;
  faculty_feedback?: string | null;
  verified_by_faculty_id?: string | null;
  verified_at?: string | null;
  created_at: string;
}

export interface InterventionProgressEvent {
  id: string;
  institution_id: string;
  plan_id: string;
  action_id?: string | null;
  actor_profile_id?: string | null;
  actor_name?: string | null;
  event_type: string;
  previous_status?: string | null;
  new_status: string;
  event_notes?: string | null;
  event_metadata: Record<string, any>;
  created_at: string;
}

export interface AcademicInterventionPlan {
  id: string;
  institution_id: string;
  student_id: string;
  student_name?: string | null;
  enrollment_number?: string | null;
  subject_id: string;
  subject_name?: string | null;
  subject_code?: string | null;
  topic_id?: string | null;
  topic_name?: string | null;
  recommendation_id?: string | null;
  plan_title: string;
  learning_objective: string;
  plan_status: InterventionPlanStatus;
  assigned_faculty_id?: string | null;
  assigned_faculty_name?: string | null;
  reviewed_by_faculty_id?: string | null;
  reviewed_at?: string | null;
  faculty_review_notes?: string | null;
  start_date?: string | null;
  target_completion_date?: string | null;
  actual_completion_date?: string | null;
  expected_outcome_evidence?: string | null;
  scientific_disclaimer: string;
  created_at: string;
  actions: InterventionAction[];
  progress_events: InterventionProgressEvent[];
}

export interface InterventionOutcomeObservation {
  id: string;
  institution_id: string;
  plan_id: string;
  student_id: string;
  subject_id: string;
  topic_id?: string | null;
  baseline_mastery_percentage?: number | null;
  followup_score_obtained?: number | null;
  followup_maximum_marks?: number | null;
  followup_mastery_percentage?: number | null;
  observation_notes?: string | null;
  scientific_disclaimer: string;
  observed_at: string;
  created_at: string;
}

export interface InterventionFacultyDashboardResponse {
  total_plans: number;
  active_plans_count: number;
  draft_review_count: number;
  approved_assigned_count: number;
  completed_plans_count: number;
  overdue_actions_count: number;
  insufficient_evidence_recommendations_count: number;
  recent_plans: AcademicInterventionPlan[];
  active_recommendations: InterventionRecommendation[];
  scientific_disclaimer: string;
}

export interface InterventionStudentWorkspaceResponse {
  student_id: string;
  student_name: string;
  active_plans: AcademicInterventionPlan[];
  pending_actions_count: number;
  completed_actions_count: number;
  scientific_disclaimer: string;
}

export interface CreateInterventionPlanPayload {
  student_id: string;
  subject_id: string;
  topic_id?: string;
  learning_outcome_id?: string;
  recommendation_id?: string;
  plan_title: string;
  learning_objective: string;
  assigned_faculty_id?: string;
  target_completion_date?: string;
  expected_outcome_evidence?: string;
  initial_actions?: {
    action_title: string;
    action_type: InterventionType;
    instructions: string;
    resource_references?: Record<string, any>[];
    estimated_effort_hours: number;
    due_date?: string;
  }[];
}

export interface ReviewInterventionPlanPayload {
  decision: 'APPROVE' | 'REJECT';
  review_notes?: string;
  assigned_faculty_id?: string;
}

export interface UpdateActionStatusPayload {
  new_status: InterventionActionStatus;
  student_completion_notes?: string;
  student_submission_url?: string;
  faculty_feedback?: string;
}

export interface RecordOutcomePayload {
  baseline_mastery_percentage?: number;
  followup_assessment_id?: string;
  followup_score_obtained?: number;
  followup_maximum_marks?: number;
  followup_mastery_percentage?: number;
  observation_notes?: string;
}

export const interventionService = {
  // Templates
  getTemplates: async (subjectId?: string, interventionType?: string): Promise<InterventionTemplate[]> => {
    const params = new URLSearchParams();
    if (subjectId) params.append('subject_id', subjectId);
    if (interventionType) params.append('intervention_type', interventionType);
    const q = params.toString() ? `?${params.toString()}` : '';
    return apiClient.get<InterventionTemplate[]>(`/interventions/templates${q}`);
  },

  // Recommendations
  generateRecommendations: async (studentId: string, subjectId: string, topicId?: string): Promise<InterventionRecommendation[]> => {
    return apiClient.post<InterventionRecommendation[]>('/interventions/recommendations/generate', {
      student_id: studentId,
      subject_id: subjectId,
      topic_id: topicId,
    });
  },

  getRecommendations: async (studentId?: string, subjectId?: string, status?: string): Promise<InterventionRecommendation[]> => {
    const params = new URLSearchParams();
    if (studentId) params.append('student_id', studentId);
    if (subjectId) params.append('subject_id', subjectId);
    if (status) params.append('status', status);
    const q = params.toString() ? `?${params.toString()}` : '';
    return apiClient.get<InterventionRecommendation[]>(`/interventions/recommendations${q}`);
  },

  // Plans
  createPlan: async (payload: CreateInterventionPlanPayload): Promise<AcademicInterventionPlan> => {
    return apiClient.post<AcademicInterventionPlan>('/interventions/plans', payload);
  },

  getPlans: async (studentId?: string, subjectId?: string, status?: string): Promise<AcademicInterventionPlan[]> => {
    const params = new URLSearchParams();
    if (studentId) params.append('student_id', studentId);
    if (subjectId) params.append('subject_id', subjectId);
    if (status) params.append('status', status);
    const q = params.toString() ? `?${params.toString()}` : '';
    return apiClient.get<AcademicInterventionPlan[]>(`/interventions/plans${q}`);
  },

  getPlan: async (planId: string): Promise<AcademicInterventionPlan> => {
    return apiClient.get<AcademicInterventionPlan>(`/interventions/plans/${planId}`);
  },

  reviewPlan: async (planId: string, payload: ReviewInterventionPlanPayload): Promise<AcademicInterventionPlan> => {
    return apiClient.post<AcademicInterventionPlan>(`/interventions/plans/${planId}/review`, payload);
  },

  assignPlan: async (planId: string): Promise<AcademicInterventionPlan> => {
    return apiClient.post<AcademicInterventionPlan>(`/interventions/plans/${planId}/assign`);
  },

  // Actions
  updateActionStatus: async (actionId: string, payload: UpdateActionStatusPayload): Promise<InterventionAction> => {
    return apiClient.post<InterventionAction>(`/interventions/actions/${actionId}/status`, payload);
  },

  // Outcomes
  recordOutcome: async (planId: string, payload: RecordOutcomePayload): Promise<InterventionOutcomeObservation> => {
    return apiClient.post<InterventionOutcomeObservation>(`/interventions/plans/${planId}/outcomes`, payload);
  },

  getOutcomes: async (planId: string): Promise<InterventionOutcomeObservation[]> => {
    return apiClient.get<InterventionOutcomeObservation[]>(`/interventions/plans/${planId}/outcomes`);
  },

  // Dashboards
  getFacultyDashboard: async (subjectId?: string): Promise<InterventionFacultyDashboardResponse> => {
    const q = subjectId ? `?subject_id=${subjectId}` : '';
    return apiClient.get<InterventionFacultyDashboardResponse>(`/interventions/dashboard/faculty${q}`);
  },

  getStudentWorkspace: async (): Promise<InterventionStudentWorkspaceResponse> => {
    return apiClient.get<InterventionStudentWorkspaceResponse>('/interventions/dashboard/student');
  },
};
