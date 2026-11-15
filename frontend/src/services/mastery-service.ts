import { apiClient } from '@/lib/api-client';

export type EvidenceSufficiencyLevel = 'INSUFFICIENT' | 'LIMITED' | 'MODERATE' | 'STRONG';
export type ConfidenceCategory = 'LOW' | 'MEDIUM' | 'HIGH';
export type MasteryStatus = 'MASTERED' | 'PROGRESSING' | 'NEEDS_ATTENTION' | 'INSUFFICIENT_EVIDENCE';
export type AttainmentStatus = 'ATTAINED' | 'PARTIALLY_ATTAINED' | 'NOT_ATTAINED' | 'INSUFFICIENT_EVIDENCE';
export type LearningGapType =
  | 'LOW_DEMONSTRATED_PERFORMANCE'
  | 'INCONSISTENT_PERFORMANCE'
  | 'INSUFFICIENT_EVIDENCE'
  | 'MISSING_ASSESSMENT_COVERAGE'
  | 'INCOMPLETE_EVALUATION'
  | 'UNAPPROVED_MAPPING'
  | 'CURRICULUM_VERSION_MISMATCH';

export interface MasteryAnalyzeRequest {
  subject_id: string;
  student_id?: string | null;
  academic_year?: string;
  semester?: number;
  calculation_version?: string;
  include_practice_tests?: boolean;
}

export interface MasteryJobResponse {
  id: string;
  institution_id: string;
  subject_id: string;
  student_id?: string | null;
  academic_year: string;
  semester: number;
  curriculum_version?: string | null;
  calculation_version: string;
  status: string;
  total_evidence_examined: number;
  eligible_evidence_count: number;
  excluded_evidence_count: number;
  started_at?: string | null;
  completed_at?: string | null;
  error_summary?: string | null;
  created_at: string;
}

export interface TopicMasteryDetailResponse {
  id: string;
  topic_id: string;
  topic_name: string;
  unit_number?: number | null;
  unit_title?: string | null;
  eligible_question_count: number;
  eligible_attempt_count: number;
  marks_obtained: number;
  maximum_marks: number;
  mastery_percentage?: number | null;
  evidence_sufficiency: EvidenceSufficiencyLevel;
  confidence_category: ConfidenceCategory;
  mastery_status: MasteryStatus;
  calculation_version: string;
  calculated_at: string;
  plain_explanation: string;
}

export interface LearningOutcomeAttainmentDetailResponse {
  id: string;
  learning_outcome_id: string;
  outcome_code: string;
  description: string;
  bloom_level: string;
  eligible_question_count: number;
  mapped_marks: number;
  marks_obtained: number;
  attainment_percentage?: number | null;
  evidence_sufficiency: EvidenceSufficiencyLevel;
  confidence_category: ConfidenceCategory;
  attainment_status: AttainmentStatus;
  calculation_version: string;
  calculated_at: string;
}

export interface LearningGapFindingResponse {
  id: string;
  subject_id: string;
  topic_id?: string | null;
  topic_name?: string | null;
  learning_outcome_id?: string | null;
  outcome_code?: string | null;
  finding_type: LearningGapType;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
  evidence_summary: string;
  supporting_evidence_refs?: Record<string, any>;
  recommended_review_action?: string | null;
  status: string;
  created_at: string;
}

export interface MasteryEvidenceItemResponse {
  id: string;
  source_entity_type: string;
  source_entity_id: string;
  assessment_id?: string | null;
  assessment_name?: string | null;
  question_id?: string | null;
  question_text?: string | null;
  marks_obtained: number;
  maximum_marks: number;
  eligibility_status: string;
  exclusion_reason?: string | null;
  mapping_status: string;
  evaluation_status: string;
  verification_status?: string | null;
  bloom_level?: string | null;
  is_practice_assessment: boolean;
  evidence_timestamp: string;
}

export interface StudentMasteryProfileResponse {
  student_id: string;
  student_name: string;
  enrollment_number: string;
  subject_id: string;
  subject_name: string;
  subject_code: string;
  overall_mastery_percentage?: number | null;
  total_topics_analyzed: number;
  mastered_topics_count: number;
  progressing_topics_count: number;
  needs_attention_topics_count: number;
  insufficient_evidence_topics_count: number;
  topic_results: TopicMasteryDetailResponse[];
  outcome_results: LearningOutcomeAttainmentDetailResponse[];
  learning_gaps: LearningGapFindingResponse[];
  cognitive_breakdown: Record<string, { questions_assessed: number; marks_obtained: number; maximum_marks: number; percentage?: number | null }>;
  competency_breakdown: Record<string, { items: number; marks_obtained: number; maximum_marks: number; percentage?: number | null }>;
  evidence_sufficiency_summary: Record<string, number>;
  scientific_disclaimer: string;
}

export interface PerformanceTrendPoint {
  timestamp: string;
  assessment_name: string;
  topic_id?: string | null;
  topic_name?: string | null;
  percentage: number;
  evidence_type: string;
  is_official: boolean;
}

export interface StudentPerformanceTrendResponse {
  student_id: string;
  subject_id: string;
  timeline: PerformanceTrendPoint[];
  trend_direction: string;
  observation_count: number;
  scientific_disclaimer: string;
}

export interface CohortMasterySummaryResponse {
  subject_id: string;
  subject_name: string;
  subject_code: string;
  total_students_enrolled: number;
  students_analyzed: number;
  topic_aggregates: {
    topic_id: string;
    topic_name: string;
    assessed_candidates_count: number;
    average_mastery_percentage?: number | null;
    has_sufficient_evidence: boolean;
  }[];
  outcome_aggregates: Record<string, any>[];
  curriculum_coverage_percentage: number;
  scientific_disclaimer: string;
}

export const masteryService = {
  triggerAnalysis: async (payload: MasteryAnalyzeRequest): Promise<MasteryJobResponse> => {
    return apiClient.post<MasteryJobResponse>('/mastery/analyze', payload);
  },

  listJobs: async (subjectId?: string): Promise<MasteryJobResponse[]> => {
    const q = subjectId ? `?subject_id=${subjectId}` : '';
    return apiClient.get<MasteryJobResponse[]>(`/mastery/jobs${q}`);
  },

  getJobDetail: async (jobId: string): Promise<MasteryJobResponse> => {
    return apiClient.get<MasteryJobResponse>(`/mastery/jobs/${jobId}`);
  },

  getStudentMasteryProfile: async (studentId: string, subjectId: string): Promise<StudentMasteryProfileResponse> => {
    return apiClient.get<StudentMasteryProfileResponse>(`/mastery/students/${studentId}?subject_id=${subjectId}`);
  },

  getStudentPerformanceTrends: async (studentId: string, subjectId: string): Promise<StudentPerformanceTrendResponse> => {
    return apiClient.get<StudentPerformanceTrendResponse>(`/mastery/students/${studentId}/trends?subject_id=${subjectId}`);
  },

  listStudentGaps: async (studentId: string, subjectId?: string): Promise<LearningGapFindingResponse[]> => {
    const q = subjectId ? `?subject_id=${subjectId}` : '';
    return apiClient.get<LearningGapFindingResponse[]>(`/mastery/students/${studentId}/gaps${q}`);
  },

  getCohortSummary: async (subjectId: string): Promise<CohortMasterySummaryResponse> => {
    return apiClient.get<CohortMasterySummaryResponse>(`/mastery/cohort/${subjectId}/summary`);
  },

  inspectContributingEvidence: async (resultId: string): Promise<MasteryEvidenceItemResponse[]> => {
    return apiClient.get<MasteryEvidenceItemResponse[]>(`/mastery/results/${resultId}/evidence`);
  },

  inspectExcludedEvidence: async (resultId: string): Promise<MasteryEvidenceItemResponse[]> => {
    return apiClient.get<MasteryEvidenceItemResponse[]>(`/mastery/results/${resultId}/excluded-evidence`);
  },
};
