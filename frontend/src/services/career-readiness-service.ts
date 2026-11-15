import { apiClient } from '@/lib/api-client';

export type CompetencyEvidenceState =
  | 'DEMONSTRATED'
  | 'DEVELOPING'
  | 'NOT_YET_DEMONSTRATED'
  | 'NOT_ASSESSED'
  | 'INSUFFICIENT_EVIDENCE'
  | 'REVIEW_REQUIRED';

export type CompetencyEvidenceType =
  | 'THEORETICAL_ASSESSMENT'
  | 'PRACTICAL_ASSESSMENT'
  | 'TOPIC_MASTERY'
  | 'PROJECT_DEMONSTRATION'
  | 'FACULTY_VERIFICATION'
  | 'CURRICULUM_COVERAGE';

export type CareerAlignmentStatus =
  | 'STRONG_EVIDENCE_ALIGNMENT'
  | 'PARTIAL_EVIDENCE_ALIGNMENT'
  | 'LIMITED_EVIDENCE_ALIGNMENT'
  | 'INSUFFICIENT_EVIDENCE';

export type CareerSkillGapType =
  | 'DEMONSTRATED_GAP'
  | 'EVIDENCE_GAP'
  | 'CURRICULUM_GAP'
  | 'PRACTICAL_EVIDENCE_GAP'
  | 'MAPPING_GAP';

export type CareerGapSeverity = 'CRITICAL' | 'HIGH' | 'MODERATE' | 'LOW';

export type ProjectVerificationStatus = 'PENDING_REVIEW' | 'VERIFIED' | 'REJECTED';

export interface IndustryCompetencyRequirement {
  id: string;
  role_id: string;
  competency_name: string;
  category: string;
  required_depth: number;
  importance: string;
  description?: string | null;
  competency_id?: string | null;
  mapping_status: string;
  source_reference?: string | null;
  rationale?: string | null;
  created_at: string;
}

export interface IndustryRoleProfile {
  id: string;
  institution_id?: string | null;
  role_title: string;
  role_family: string;
  description: string;
  experience_tier: string;
  version: string;
  is_active: boolean;
  review_status: string;
  created_at: string;
  updated_at: string;
  requirements: IndustryCompetencyRequirement[];
}

export interface StudentProjectEvidence {
  id: string;
  institution_id: string;
  student_id: string;
  title: string;
  description: string;
  technology_stack: string[];
  repository_url?: string | null;
  portfolio_url?: string | null;
  documentation_url?: string | null;
  demonstrated_competencies: string[];
  verification_status: ProjectVerificationStatus;
  reviewer_id?: string | null;
  reviewed_at?: string | null;
  verification_notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface StudentCompetencyEvidence {
  id: string;
  institution_id: string;
  student_id: string;
  competency_id?: string | null;
  competency_name: string;
  category: string;
  evidence_type: CompetencyEvidenceType;
  source_entity_type: string;
  source_entity_id?: string | null;
  evidence_state: CompetencyEvidenceState;
  score_or_metric?: number | null;
  evidence_summary: string;
  provenance_details?: Record<string, any>;
  verified_by?: string | null;
  verified_at?: string | null;
  is_eligible: boolean;
  exclusion_reason?: string | null;
  created_at: string;
  updated_at: string;
}

export interface CareerSkillGapFinding {
  id: string;
  analysis_id: string;
  institution_id: string;
  student_id: string;
  role_id: string;
  requirement_id?: string | null;
  competency_name: string;
  importance: string;
  gap_type: CareerSkillGapType;
  current_evidence_state: CompetencyEvidenceState;
  gap_severity: CareerGapSeverity;
  rationale: string;
  suggested_action: string;
  evidence_needed: string;
  related_subject_id?: string | null;
  related_learning_outcome_id?: string | null;
  status: string;
  created_at: string;
}

export interface CareerDevelopmentRecommendation {
  id: string;
  analysis_id?: string | null;
  gap_id?: string | null;
  institution_id: string;
  student_id: string;
  role_id: string;
  title: string;
  target_competency: string;
  recommendation_type: string;
  priority: string;
  status: string;
  action_plan: string;
  expected_evidence: string;
  estimated_duration_days: number;
  academic_intervention_plan_id?: string | null;
  student_notes?: string | null;
  reviewer_feedback?: string | null;
  created_at: string;
  updated_at: string;
}

export interface CareerReadinessAnalysis {
  id: string;
  institution_id: string;
  student_id: string;
  role_id: string;
  role_title?: string | null;
  alignment_status: CareerAlignmentStatus;
  total_requirements_count: number;
  demonstrated_count: number;
  developing_count: number;
  insufficient_evidence_count: number;
  not_assessed_count: number;
  review_required_count: number;
  core_competency_coverage: number;
  practical_evidence_coverage: number;
  faculty_reviewed_count: number;
  summary_rationale: string;
  disclaimer: string;
  analysis_version: string;
  created_at: string;
  gap_findings: CareerSkillGapFinding[];
  recommendations: CareerDevelopmentRecommendation[];
}

export interface RoleComparisonItem {
  role_id: string;
  role_title: string;
  alignment_status: CareerAlignmentStatus;
  total_requirements: number;
  demonstrated_count: number;
  developing_count: number;
  gap_count: number;
  core_coverage_pct: number;
  practical_coverage_pct: number;
}

export interface CareerReadinessComparisonResponse {
  student_id: string;
  compared_roles: RoleComparisonItem[];
  disclaimer: string;
}

export interface CareerDashboardOverview {
  student_id: string;
  enrolled_roles_count: number;
  latest_analysis?: CareerReadinessAnalysis | null;
  verified_projects_count: number;
  pending_projects_count: number;
  demonstrated_competencies_count: number;
  developing_competencies_count: number;
  active_gaps_count: number;
  active_recommendations_count: number;
  disclaimer: string;
}

export interface SubmitProjectPayload {
  title: string;
  description: string;
  technology_stack: string[];
  repository_url?: string;
  portfolio_url?: string;
  documentation_url?: string;
  demonstrated_competencies: string[];
  student_id?: string;
}

export interface ReviewProjectPayload {
  verification_status: ProjectVerificationStatus;
  verification_notes?: string;
}

export const careerReadinessService = {
  // Roles
  getRoles: async (includeInactive = false): Promise<IndustryRoleProfile[]> => {
    const q = includeInactive ? '?include_inactive=true' : '';
    return apiClient.get<IndustryRoleProfile[]>(`/career-readiness/roles${q}`);
  },

  getRole: async (roleId: string): Promise<IndustryRoleProfile> => {
    return apiClient.get<IndustryRoleProfile>(`/career-readiness/roles/${roleId}`);
  },

  // Projects
  getProjects: async (studentId?: string): Promise<StudentProjectEvidence[]> => {
    const q = studentId ? `?student_id=${studentId}` : '';
    return apiClient.get<StudentProjectEvidence[]>(`/career-readiness/projects${q}`);
  },

  submitProject: async (payload: SubmitProjectPayload): Promise<StudentProjectEvidence> => {
    return apiClient.post<StudentProjectEvidence>('/career-readiness/projects', payload);
  },

  updateProject: async (projectId: string, payload: Partial<SubmitProjectPayload>): Promise<StudentProjectEvidence> => {
    return apiClient.put<StudentProjectEvidence>(`/career-readiness/projects/${projectId}`, payload);
  },

  reviewProject: async (projectId: string, payload: ReviewProjectPayload): Promise<StudentProjectEvidence> => {
    return apiClient.post<StudentProjectEvidence>(`/career-readiness/projects/${projectId}/review`, payload);
  },

  // Evidence Ledger
  getEvidence: async (studentId?: string): Promise<StudentCompetencyEvidence[]> => {
    const q = studentId ? `?student_id=${studentId}` : '';
    return apiClient.get<StudentCompetencyEvidence[]>(`/career-readiness/evidence${q}`);
  },

  // Analysis & Comparison
  analyzeReadiness: async (payload: { role_id: string; student_id?: string; force_recalculate?: boolean }): Promise<CareerReadinessAnalysis> => {
    return apiClient.post<CareerReadinessAnalysis>('/career-readiness/analyze', payload);
  },

  compareRoles: async (studentId?: string, roleIds?: string[]): Promise<CareerReadinessComparisonResponse> => {
    const params = new URLSearchParams();
    if (studentId) params.append('student_id', studentId);
    if (roleIds) roleIds.forEach((id) => params.append('role_ids', id));
    const q = params.toString() ? `?${params.toString()}` : '';
    return apiClient.get<CareerReadinessComparisonResponse>(`/career-readiness/compare${q}`);
  },

  getOverview: async (studentId?: string): Promise<CareerDashboardOverview> => {
    const q = studentId ? `?student_id=${studentId}` : '';
    return apiClient.get<CareerDashboardOverview>(`/career-readiness/overview${q}`);
  },

  // Recommendations
  getRecommendations: async (studentId?: string, roleId?: string): Promise<CareerDevelopmentRecommendation[]> => {
    const params = new URLSearchParams();
    if (studentId) params.append('student_id', studentId);
    if (roleId) params.append('role_id', roleId);
    const q = params.toString() ? `?${params.toString()}` : '';
    return apiClient.get<CareerDevelopmentRecommendation[]>(`/career-readiness/recommendations${q}`);
  },

  updateRecommendation: async (
    recommendationId: string,
    payload: { status?: string; student_notes?: string; reviewer_feedback?: string }
  ): Promise<CareerDevelopmentRecommendation> => {
    return apiClient.patch<CareerDevelopmentRecommendation>(
      `/career-readiness/recommendations/${recommendationId}`,
      payload
    );
  },
};
