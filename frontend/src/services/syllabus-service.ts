import { apiClient } from '@/lib/api-client';

export type BloomTaxonomyLevel = 'REMEMBER' | 'UNDERSTAND' | 'APPLY' | 'ANALYZE' | 'EVALUATE' | 'CREATE';
export type CompetencyCategory = 'THEORETICAL' | 'PROGRAMMING' | 'TOOLS_TECHNOLOGIES' | 'ANALYTICAL' | 'PRACTICAL';
export type IndustryMappingStatus = 'DIRECT' | 'PARTIAL' | 'MISSING' | 'OUTDATED';
export type IndustryImportance = 'HIGH' | 'MEDIUM' | 'LOW';
export type DocumentStatus = 'UPLOADED' | 'PROCESSING' | 'EXTRACTED' | 'REVIEW_REQUIRED' | 'APPROVED' | 'REJECTED' | 'FAILED';

export interface AcademicProgram {
  id: string;
  institution_id: string;
  name: string;
  code: string;
  degree_type: string;
  duration_years: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AcademicSubject {
  id: string;
  institution_id: string;
  program_id: string;
  name: string;
  code: string;
  semester: number;
  academic_year: string;
  regulation_version: string;
  credits: number;
  total_hours: number;
  description?: string;
  prerequisites?: string[];
  created_at: string;
  updated_at: string;
}

export interface SyllabusTopic {
  id: string;
  unit_id: string;
  topic_name: string;
  subtopics: string[];
  order_index: number;
  created_at: string;
}

export interface LearningOutcome {
  id: string;
  subject_id: string;
  unit_id?: string;
  outcome_code: string;
  description: string;
  bloom_level: BloomTaxonomyLevel;
  created_at: string;
}

export interface SyllabusUnit {
  id: string;
  document_id: string;
  subject_id: string;
  unit_number: number;
  title: string;
  estimated_hours: number;
  description?: string;
  topics: SyllabusTopic[];
  learning_outcomes: LearningOutcome[];
  created_at: string;
}

export interface SyllabusDocument {
  id: string;
  institution_id: string;
  subject_id?: string;
  uploaded_by?: string;
  file_name: string;
  file_size_bytes: number;
  mime_type: string;
  storage_path: string;
  status: DocumentStatus;
  raw_text?: string;
  extraction_metadata?: Record<string, unknown>;
  units?: SyllabusUnit[];
  created_at: string;
  updated_at: string;
}

export interface Competency {
  id: string;
  institution_id?: string;
  title: string;
  description: string;
  category: CompetencyCategory;
  bloom_level: BloomTaxonomyLevel;
  depth_level: number;
  syllabus_evidence?: string;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface IndustryCompetencyRequirement {
  id: string;
  role_id: string;
  competency_name: string;
  category: CompetencyCategory;
  required_depth: number;
  importance: IndustryImportance;
  description?: string;
  created_at: string;
}

export interface IndustryRoleProfile {
  id: string;
  role_title: string;
  role_family: string;
  description: string;
  experience_tier: string;
  requirements: IndustryCompetencyRequirement[];
  created_at: string;
}

export interface CurriculumGapAnalysis {
  id: string;
  subject_id: string;
  role_id: string;
  role_title?: string;
  industry_competency_id: string;
  industry_competency_name?: string;
  category?: CompetencyCategory;
  required_depth?: number;
  importance?: IndustryImportance;
  academic_competency_id?: string;
  academic_competency_name?: string;
  status: IndustryMappingStatus;
  rationale: string;
  evidence?: string;
  recommendation?: string;
  analyzed_at: string;
}

export interface GapAnalysisSummary {
  subject_id: string;
  role_id: string;
  role_title: string;
  total_industry_requirements: number;
  direct_match_count: number;
  partial_match_count: number;
  missing_count: number;
  outdated_count: number;
  coverage_percentage: number;
  gaps: CurriculumGapAnalysis[];
}

export interface SyllabusReviewHistory {
  id: string;
  document_id: string;
  reviewed_by?: string;
  reviewer_name?: string;
  action: string;
  entity_type: string;
  entity_id: string;
  previous_value?: Record<string, unknown>;
  new_value?: Record<string, unknown>;
  comments?: string;
  created_at: string;
}

export const syllabusService = {
  // Programs
  getPrograms: async (institutionId?: string): Promise<AcademicProgram[]> => {
    const q = institutionId ? `?institution_id=${institutionId}` : '';
    return apiClient.get<AcademicProgram[]>(`/syllabus/programs${q}`);
  },

  createProgram: async (data: Partial<AcademicProgram>): Promise<AcademicProgram> => {
    return apiClient.post<AcademicProgram>('/syllabus/programs', data);
  },

  // Subjects
  getSubjects: async (institutionId?: string, programId?: string): Promise<AcademicSubject[]> => {
    const params = new URLSearchParams();
    if (institutionId) params.append('institution_id', institutionId);
    if (programId) params.append('program_id', programId);
    const q = params.toString() ? `?${params.toString()}` : '';
    return apiClient.get<AcademicSubject[]>(`/syllabus/subjects${q}`);
  },

  createSubject: async (data: Partial<AcademicSubject>): Promise<AcademicSubject> => {
    return apiClient.post<AcademicSubject>('/syllabus/subjects', data);
  },

  getSubjectDetail: async (subjectId: string): Promise<AcademicSubject> => {
    return apiClient.get<AcademicSubject>(`/syllabus/subjects/${subjectId}`);
  },

  // Documents
  uploadDocument: async (file: File, subjectId?: string, institutionId?: string): Promise<SyllabusDocument> => {
    const formData = new FormData();
    formData.append('file', file);
    if (subjectId) formData.append('subject_id', subjectId);
    if (institutionId) formData.append('institution_id', institutionId);
    return apiClient.post<SyllabusDocument>('/syllabus/upload', formData);
  },

  processDocument: async (documentId: string): Promise<SyllabusDocument> => {
    return apiClient.post<SyllabusDocument>(`/syllabus/documents/${documentId}/process`);
  },

  getDocuments: async (subjectId?: string): Promise<SyllabusDocument[]> => {
    const q = subjectId ? `?subject_id=${subjectId}` : '';
    return apiClient.get<SyllabusDocument[]>(`/syllabus/documents${q}`);
  },

  getDocumentDetail: async (documentId: string): Promise<SyllabusDocument> => {
    return apiClient.get<SyllabusDocument>(`/syllabus/documents/${documentId}`);
  },

  // Structure & Competencies
  getSubjectStructure: async (subjectId: string): Promise<SyllabusUnit[]> => {
    return apiClient.get<SyllabusUnit[]>(`/syllabus/subjects/${subjectId}/structure`);
  },

  getSubjectCompetencies: async (subjectId: string): Promise<Competency[]> => {
    return apiClient.get<Competency[]>(`/syllabus/subjects/${subjectId}/competencies`);
  },

  // Industry Roles & Gap Analysis
  getIndustryRoles: async (): Promise<IndustryRoleProfile[]> => {
    return apiClient.get<IndustryRoleProfile[]>('/syllabus/industry-roles');
  },

  getSubjectGapAnalysis: async (subjectId: string): Promise<GapAnalysisSummary[]> => {
    return apiClient.get<GapAnalysisSummary[]>(`/syllabus/subjects/${subjectId}/gap-analysis`);
  },

  // Faculty Review & Modification
  reviewDocument: async (documentId: string, action: string, comments?: string): Promise<SyllabusDocument> => {
    return apiClient.post<SyllabusDocument>(`/syllabus/documents/${documentId}/review`, { action, comments });
  },

  getDocumentHistory: async (documentId: string): Promise<SyllabusReviewHistory[]> => {
    return apiClient.get<SyllabusReviewHistory[]>(`/syllabus/documents/${documentId}/history`);
  },

  updateUnit: async (unitId: string, data: { title?: string; estimated_hours?: number; description?: string }): Promise<SyllabusUnit> => {
    return apiClient.patch<SyllabusUnit>(`/syllabus/units/${unitId}`, data);
  },

  updateTopic: async (topicId: string, data: { topic_name?: string; subtopics?: string[] }): Promise<SyllabusTopic> => {
    return apiClient.patch<SyllabusTopic>(`/syllabus/topics/${topicId}`, data);
  },
};
