export type DemoScenarioId = 'A' | 'B' | 'C' | 'D';

export interface DemoScenarioMeta {
  id: DemoScenarioId;
  name: string;
  studentName: string;
  enrollmentNumber: string;
  department: string;
  semester: number;
  badgeLabel: string;
  badgeVariant: 'success' | 'warning' | 'error' | 'outline' | 'info';
  summary: string;
  keyObservation: string;
}

export interface DemoStudent {
  id: string;
  enrollment_number: string;
  first_name: string;
  last_name: string;
  email: string;
  department: string;
  admission_year: number;
  current_semester: number;
  academic_status: 'ENROLLED' | 'PROBATION' | 'GRADUATED' | 'LEAVE';
  cgpa: number;
  attendance_rate: number;
  scenario_id?: DemoScenarioId;
}

export interface DemoFaculty {
  id: string;
  name: string;
  title: string;
  department: string;
  specialization: string;
  email: string;
}

export interface DemoSubject {
  id: string;
  code: string;
  name: string;
  credits: number;
  semester: number;
  department: string;
  instructor_id: string;
  description: string;
}

export interface DemoSyllabusTopic {
  id: string;
  unit_number: number;
  unit_title: string;
  topic_name: string;
  bloom_level: string;
  competency_code: string;
  competency_name: string;
  hours: number;
}

export interface DemoCLO {
  id: string;
  code: string;
  description: string;
  target_attainment: number;
  current_attainment: number;
  status: 'ATTAINED' | 'IN_PROGRESS' | 'NEEDS_REMEDIATION';
}

export interface DemoAssessment {
  id: string;
  title: string;
  subject_code: string;
  type: 'INTERNAL_TEST' | 'QUIZ' | 'MIDTERM' | 'LAB_PRACTICAL';
  max_marks: number;
  passing_marks: number;
  date: string;
  total_questions: number;
}

export interface DemoAssessmentAttempt {
  assessment_id: string;
  student_id: string;
  marks_obtained: number | null;
  status: 'EVALUATED' | 'EXCUSED' | 'ABSENT' | 'SUBMITTED';
  bloom_distribution: { level: string; marks: number; max: number }[];
  engagement_telemetry: {
    focus_time_minutes: number;
    tab_blur_count: number;
    interaction_events: number;
    device_type: string;
  };
}

export interface DemoTopicMastery {
  topic_name: string;
  subject_code: string;
  unit: number;
  mastery_state: 'MASTERED' | 'PROGRESSING' | 'NEEDS_ATTENTION' | 'INSUFFICIENT_EVIDENCE';
  score_percentage: number | null;
  evidence_count: number;
  last_evaluated: string;
}

export interface DemoRiskFactor {
  factor_name: string;
  category: 'ADVERSE' | 'PROTECTIVE';
  impact_weight: number; // 0.0 to 1.0
  evidence_summary: string;
}

export interface DemoStudentRiskProfile {
  student_id: string;
  risk_classification: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL' | 'INSUFFICIENT_EVIDENCE';
  risk_probability: number | null;
  prediction_cutoff: string;
  target_semester: string;
  model_type: 'LOGISTIC_REGRESSION' | 'EXPERT_DETERMINISTIC_RULES' | 'INSUFFICIENT_EVIDENCE_GATE';
  adverse_factors: DemoRiskFactor[];
  protective_factors: DemoRiskFactor[];
  explainable_summary: string;
  recommended_actions: string[];
}

export interface DemoInterventionPlan {
  id: string;
  student_id: string;
  title: string;
  subject_code: string;
  reason: string;
  lifecycle_status: 'DRAFT' | 'PENDING_REVIEW' | 'APPROVED' | 'ACTIVE' | 'COMPLETED' | 'CANCELLED';
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  faculty_advisor: string;
  created_at: string;
  target_completion: string;
  action_items: {
    title: string;
    description: string;
    completed: boolean;
    evidence_submitted?: string;
  }[];
  observational_note: string;
}

export interface DemoCareerRoleProfile {
  id: string;
  role_title: string;
  industry_demand: 'VERY_HIGH' | 'HIGH' | 'MODERATE';
  description: string;
  required_competencies: {
    name: string;
    bloom_depth: string;
    weight: number;
  }[];
}

export interface DemoStudentCareerAlignment {
  student_id: string;
  role_id: string;
  role_title: string;
  core_competency_coverage: number; // percentage
  practical_project_coverage: number; // percentage
  alignment_status: 'STRONGLY_ALIGNED' | 'DEVELOPING' | 'SIGNIFICANT_GAPS' | 'INSUFFICIENT_EVIDENCE';
  verified_projects: {
    title: string;
    repository_url: string;
    verified_by_faculty: boolean;
    demonstrated_competencies: string[];
  }[];
  skill_gaps: {
    competency: string;
    gap_tier: 'CORE_FOUNDATION' | 'PRACTICAL_APPLICATION' | 'ADVANCED_SYNTHESIS';
    recommendation: string;
  }[];
}

export interface DemoDashboardOverview {
  total_students: number;
  sufficient_evidence_count: number;
  insufficient_evidence_count: number;
  active_interventions_count: number;
  overall_outcome_attainment_pct: number;
  risk_distribution: {
    low: number;
    moderate: number;
    high: number;
    critical: number;
    insufficient: number;
  };
  mastery_distribution: {
    mastered: number;
    progressing: number;
    needs_attention: number;
    insufficient: number;
  };
  recent_activity: {
    id: string;
    timestamp: string;
    type: 'VERIFICATION' | 'ASSESSMENT' | 'INTERVENTION' | 'RISK_FLAG';
    description: string;
  }[];
}
