import { apiClient } from '@/lib/api-client';

export type RiskClassification = 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL' | 'INSUFFICIENT_EVIDENCE';
export type RiskModelType = 'LOGISTIC_REGRESSION' | 'DECISION_TREE' | 'DETERMINISTIC_RULES';
export type RiskModelStatus = 'DRAFT' | 'TRAINING' | 'TRAINED' | 'VALIDATED' | 'ACTIVE' | 'ARCHIVED' | 'FAILED';
export type EvidenceSufficiencyLevel = 'INSUFFICIENT' | 'LIMITED' | 'MODERATE' | 'STRONG';

export interface AcademicRiskTarget {
  id: string;
  institution_id: string;
  subject_id: string;
  target_code: string;
  target_name: string;
  outcome_definition: string;
  positive_label_definition: string;
  negative_label_definition: string;
  passing_threshold_percentage: number;
  prediction_horizon_weeks: number;
  is_institution_policy: boolean;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface RiskDatasetReadiness {
  institution_id: string;
  subject_id: string;
  target_id: string;
  target_code: string;
  passing_threshold_percentage: number;
  total_enrolled_students: number;
  eligible_labeled_samples: number;
  positive_class_count: number;
  negative_class_count: number;
  minority_class_ratio: number;
  is_dataset_ready_for_training: boolean;
  readiness_notes: string[];
  recommended_model_type: RiskModelType;
}

export interface RiskModelVersion {
  id: string;
  institution_id: string;
  target_id: string;
  version_tag: string;
  model_type: RiskModelType;
  algorithm_name: string;
  training_cutoff_date: string;
  training_sample_count: number;
  positive_sample_count: number;
  negative_sample_count: number;
  feature_names: string[];
  hyperparameters_json: Record<string, any>;
  parameters_json: Record<string, any>;
  is_active: boolean;
  model_status: RiskModelStatus;
  created_at: string;
}

export interface RiskPredictionExplanation {
  id: string;
  feature_name: string;
  feature_value: number;
  contribution_weight: number;
  explanation_text: string;
  source_evidence_reference: string;
  is_adverse_factor: boolean;
}

export interface AcademicRiskPrediction {
  id: string;
  institution_id: string;
  target_id: string;
  model_version_id: string;
  student_id: string;
  subject_id: string;
  cutoff_date: string;
  risk_score?: number | null;
  risk_classification: RiskClassification;
  evidence_sufficiency: EvidenceSufficiencyLevel;
  prediction_status: string;
  scientific_disclaimer: string;
  created_at: string;
  explanations: RiskPredictionExplanation[];
}

export interface StudentRiskProfile {
  student_id: string;
  student_name: string;
  enrollment_number: string;
  subject_id: string;
  subject_name: string;
  subject_code: string;
  active_prediction?: AcademicRiskPrediction | null;
  feature_snapshot?: Record<string, any> | null;
  historical_prediction_count: number;
  scientific_disclaimer: string;
}

export interface CohortStudentRiskEntry {
  student_id: string;
  student_name: string;
  enrollment_number: string;
  risk_classification: RiskClassification;
  risk_score?: number | null;
  evidence_sufficiency: EvidenceSufficiencyLevel;
  top_adverse_factor?: string | null;
  last_evaluated_at?: string | null;
}

export interface CohortRiskSummary {
  subject_id: string;
  subject_name: string;
  subject_code: string;
  target_id?: string | null;
  target_code?: string | null;
  total_enrolled: number;
  evaluated_count: number;
  critical_count: number;
  high_count: number;
  moderate_count: number;
  low_count: number;
  insufficient_evidence_count: number;
  students: CohortStudentRiskEntry[];
  scientific_disclaimer: string;
}

export interface CreateRiskTargetPayload {
  subject_id: string;
  target_code: string;
  target_name: string;
  outcome_definition: string;
  positive_label_definition?: string;
  negative_label_definition?: string;
  passing_threshold_percentage?: number;
  prediction_horizon_weeks?: number;
  is_institution_policy?: boolean;
}

export interface TrainModelPayload {
  target_id: string;
  model_type: RiskModelType;
  version_tag: string;
  hyperparameters?: Record<string, any>;
  cutoff_date?: string;
}

export interface GeneratePredictionsPayload {
  subject_id: string;
  target_id: string;
  model_version_id?: string;
  target_student_id?: string;
  cutoff_date?: string;
}

export const riskService = {
  // Targets
  getTargets: async (subjectId?: string): Promise<AcademicRiskTarget[]> => {
    const q = subjectId ? `?subject_id=${subjectId}` : '';
    return apiClient.get<AcademicRiskTarget[]>(`/risk/targets${q}`);
  },

  createTarget: async (payload: CreateRiskTargetPayload): Promise<AcademicRiskTarget> => {
    return apiClient.post<AcademicRiskTarget>('/risk/targets', payload);
  },

  // Dataset Readiness
  getReadiness: async (subjectId: string, targetId?: string): Promise<RiskDatasetReadiness> => {
    const params = new URLSearchParams({ subject_id: subjectId });
    if (targetId) params.append('target_id', targetId);
    return apiClient.get<RiskDatasetReadiness>(`/risk/readiness?${params.toString()}`);
  },

  // Models
  getModels: async (targetId?: string): Promise<RiskModelVersion[]> => {
    const q = targetId ? `?target_id=${targetId}` : '';
    return apiClient.get<RiskModelVersion[]>(`/risk/models${q}`);
  },

  trainModel: async (subjectId: string, payload: TrainModelPayload): Promise<RiskModelVersion> => {
    return apiClient.post<RiskModelVersion>(`/risk/models/train?subject_id=${subjectId}`, payload);
  },

  activateModel: async (modelVersionId: string): Promise<RiskModelVersion> => {
    return apiClient.post<RiskModelVersion>(`/risk/models/${modelVersionId}/activate`);
  },

  // Predictions
  generatePredictions: async (payload: GeneratePredictionsPayload): Promise<AcademicRiskPrediction[]> => {
    return apiClient.post<AcademicRiskPrediction[]>('/risk/predictions/generate', payload);
  },

  // Student Profile
  getStudentRiskProfile: async (
    studentId: string,
    subjectId: string,
    targetId?: string
  ): Promise<StudentRiskProfile> => {
    const q = targetId ? `?target_id=${targetId}` : '';
    return apiClient.get<StudentRiskProfile>(
      `/risk/students/${studentId}/subjects/${subjectId}/profile${q}`
    );
  },

  // Cohort Summary
  getCohortSummary: async (subjectId: string, targetId?: string): Promise<CohortRiskSummary> => {
    const q = targetId ? `?target_id=${targetId}` : '';
    return apiClient.get<CohortRiskSummary>(
      `/risk/cohort/subjects/${subjectId}/summary${q}`
    );
  },
};
