import { apiClient } from '@/lib/api-client';

export interface DataFreshnessInfo {
  last_updated_at?: string | null;
  source_module: string;
  freshness_status: 'FRESH' | 'RECENT' | 'STALE' | 'NOT_AVAILABLE';
  is_snapshot: boolean;
  details?: string | null;
}

export interface StudentProfileHeader {
  id: string;
  full_name: string;
  enrollment_number: string;
  program_name: string;
  department: string;
  current_semester: number;
  institution_name: string;
  academic_status: string;
}

export interface StudentAcademicPerformanceCard {
  average_marks?: number | null;
  attendance_rate?: number | null;
  total_records: number;
  verified_records_count: number;
  pending_records_count: number;
  enrolled_subjects_count: number;
  freshness: DataFreshnessInfo;
}

export interface StudentMasterySummaryCard {
  topics_assessed_count: number;
  topics_demonstrated_count: number;
  topics_developing_count: number;
  topics_insufficient_evidence_count: number;
  clo_attainment_pct?: number | null;
  active_learning_gaps_count: number;
  freshness: DataFreshnessInfo;
}

export interface StudentRiskSummaryCard {
  has_prediction: boolean;
  risk_classification?: string | null;
  risk_probability?: number | null;
  prediction_horizon?: string | null;
  primary_adverse_factors: string[];
  protective_factors: string[];
  prediction_timestamp?: string | null;
  model_version?: string | null;
  disclaimer: string;
  freshness: DataFreshnessInfo;
}

export interface StudentInterventionSummaryCard {
  active_plans_count: number;
  pending_actions_count: number;
  completed_actions_count: number;
  latest_plan_title?: string | null;
  faculty_mentor_name?: string | null;
  freshness: DataFreshnessInfo;
}

export interface StudentCareerSummaryCard {
  analyzed_roles_count: number;
  target_role_title?: string | null;
  core_coverage_pct?: number | null;
  practical_coverage_pct?: number | null;
  alignment_status?: string | null;
  verified_projects_count: number;
  pending_projects_count: number;
  active_skill_gaps_count: number;
  freshness: DataFreshnessInfo;
}

export interface StudentOverviewResponse {
  student_profile: StudentProfileHeader;
  academic_performance: StudentAcademicPerformanceCard;
  mastery_summary: StudentMasterySummaryCard;
  risk_summary: StudentRiskSummaryCard;
  intervention_summary: StudentInterventionSummaryCard;
  career_summary: StudentCareerSummaryCard;
  system_freshness: string;
}

export interface FacultySubjectItem {
  subject_id: string;
  code: string;
  name: string;
  semester: number;
  enrolled_students_count: number;
  average_attendance?: number | null;
  average_marks?: number | null;
}

export interface FacultyVerificationQueue {
  pending_academic_records: number;
  pending_interventions_review: number;
  pending_practical_projects: number;
}

export interface FacultyCohortRiskOverview {
  high_risk_students_count: number;
  moderate_risk_students_count: number;
  low_risk_students_count: number;
  learning_gaps_flagged_count: number;
  active_interventions_count: number;
}

export interface FacultyOverviewResponse {
  faculty_name: string;
  institution_name: string;
  department: string;
  assigned_subjects: FacultySubjectItem[];
  total_students_monitored: number;
  verification_queue: FacultyVerificationQueue;
  cohort_risk_overview: FacultyCohortRiskOverview;
  freshness: DataFreshnessInfo;
}

export interface InstitutionSummaryCounts {
  total_active_students: number;
  total_faculty: number;
  total_programs: number;
  total_subjects: number;
}

export interface InstitutionAcademicDataStatus {
  total_academic_records: number;
  verified_records_pct: number;
  data_quality_findings_count: number;
}

export interface InstitutionMasteryOverview {
  mastery_demonstrated_pct: number;
  mastery_developing_pct: number;
  insufficient_evidence_pct: number;
  total_evaluated_topics: number;
}

export interface InstitutionRiskDistribution {
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  unscreened_count: number;
}

export interface InstitutionInterventionMetrics {
  active_plans_count: number;
  completed_plans_count: number;
  pending_review_count: number;
}

export interface InstitutionCareerReadinessOverview {
  students_evaluated_count: number;
  ready_students_count: number;
  approaching_students_count: number;
  developing_students_count: number;
  verified_projects_total: number;
}

export interface InstitutionOverviewResponse {
  institution_id: string;
  institution_name: string;
  institution_code: string;
  summary_counts: InstitutionSummaryCounts;
  academic_data_status: InstitutionAcademicDataStatus;
  mastery_overview: InstitutionMasteryOverview;
  risk_distribution: InstitutionRiskDistribution;
  intervention_metrics: InstitutionInterventionMetrics;
  career_readiness_overview: InstitutionCareerReadinessOverview;
  freshness: DataFreshnessInfo;
}

export interface PlacementReadinessDistribution {
  ready_count: number;
  approaching_count: number;
  developing_count: number;
  emerging_or_unassessed_count: number;
}

export interface PlacementProjectVerificationSummary {
  verified_projects_count: number;
  pending_verification_count: number;
}

export interface SkillGapItem {
  competency_name: string;
  gap_type: string;
  affected_students_count: number;
}

export interface PlacementOverviewResponse {
  institution_name: string;
  active_role_profiles_count: number;
  total_evaluated_students: number;
  readiness_distribution: PlacementReadinessDistribution;
  project_verification_summary: PlacementProjectVerificationSummary;
  top_industry_skill_gaps: SkillGapItem[];
  freshness: DataFreshnessInfo;
}

export interface SuperAdminOverviewResponse {
  total_institutions: number;
  active_institutions: number;
  total_users: number;
  users_by_role: Record<string, number>;
  module_health_status: Record<string, string>;
  database_connectivity: string;
  database_latency_ms?: number | null;
  latest_migration: string;
  ai_service_configured: boolean;
  freshness: DataFreshnessInfo;
}

export const dashboardService = {
  // Student Endpoints
  getStudentOverview: async (studentId?: string): Promise<StudentOverviewResponse> => {
    const q = studentId ? `?student_id=${studentId}` : '';
    return apiClient.get<StudentOverviewResponse>(`/dashboard/student/overview${q}`);
  },

  getStudentAcademicSummary: async (studentId?: string): Promise<StudentAcademicPerformanceCard> => {
    const q = studentId ? `?student_id=${studentId}` : '';
    return apiClient.get<StudentAcademicPerformanceCard>(`/dashboard/student/academic-summary${q}`);
  },

  getStudentMasterySummary: async (studentId?: string): Promise<StudentMasterySummaryCard> => {
    const q = studentId ? `?student_id=${studentId}` : '';
    return apiClient.get<StudentMasterySummaryCard>(`/dashboard/student/mastery-summary${q}`);
  },

  getStudentRiskSummary: async (studentId?: string): Promise<StudentRiskSummaryCard> => {
    const q = studentId ? `?student_id=${studentId}` : '';
    return apiClient.get<StudentRiskSummaryCard>(`/dashboard/student/risk-summary${q}`);
  },

  getStudentInterventionSummary: async (studentId?: string): Promise<StudentInterventionSummaryCard> => {
    const q = studentId ? `?student_id=${studentId}` : '';
    return apiClient.get<StudentInterventionSummaryCard>(`/dashboard/student/intervention-summary${q}`);
  },

  getStudentCareerSummary: async (studentId?: string): Promise<StudentCareerSummaryCard> => {
    const q = studentId ? `?student_id=${studentId}` : '';
    return apiClient.get<StudentCareerSummaryCard>(`/dashboard/student/career-summary${q}`);
  },

  // Faculty Endpoints
  getFacultyOverview: async (subjectId?: string): Promise<FacultyOverviewResponse> => {
    const q = subjectId ? `?subject_id=${subjectId}` : '';
    return apiClient.get<FacultyOverviewResponse>(`/dashboard/faculty/overview${q}`);
  },

  // Institution Admin Endpoints
  getInstitutionOverview: async (institutionId?: string): Promise<InstitutionOverviewResponse> => {
    const q = institutionId ? `?institution_id=${institutionId}` : '';
    return apiClient.get<InstitutionOverviewResponse>(`/dashboard/institution/overview${q}`);
  },

  // Placement Officer Endpoints
  getPlacementOverview: async (): Promise<PlacementOverviewResponse> => {
    return apiClient.get<PlacementOverviewResponse>('/dashboard/placement/overview');
  },

  // Super Admin Endpoints
  getSuperAdminOverview: async (): Promise<SuperAdminOverviewResponse> => {
    return apiClient.get<SuperAdminOverviewResponse>('/dashboard/admin/overview');
  },
};
