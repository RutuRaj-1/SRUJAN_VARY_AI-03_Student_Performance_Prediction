import { apiClient } from '@/lib/api-client';

export type AssessmentType =
  | 'INTERNAL_TEST'
  | 'MID_TERM'
  | 'END_TERM'
  | 'ASSIGNMENT'
  | 'QUIZ'
  | 'PRACTICAL'
  | 'LAB'
  | 'PROJECT'
  | 'VIVA'
  | 'OTHER';

export type AssessmentResultStatus =
  | 'PASSED'
  | 'FAILED'
  | 'ABSENT'
  | 'NOT_SUBMITTED'
  | 'EXEMPTED'
  | 'PENDING';

export type AttendanceStatus = 'PRESENT' | 'ABSENT' | 'LATE' | 'EXCUSED' | 'NOT_RECORDED';

export type RecordVerificationStatus =
  | 'IMPORTED'
  | 'VALIDATION_REQUIRED'
  | 'REVIEW_REQUIRED'
  | 'VERIFIED'
  | 'REJECTED'
  | 'CORRECTION_REQUIRED';

export type DataQualitySeverity = 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';

export type ImportCategory = 'STUDENTS' | 'ENROLLMENTS' | 'ASSESSMENTS' | 'PERFORMANCE' | 'ATTENDANCE';

export type ImportJobStatus =
  | 'PENDING'
  | 'VALIDATING'
  | 'PREVIEW_READY'
  | 'IMPORTING'
  | 'COMPLETED'
  | 'FAILED'
  | 'CANCELLED';

export interface StudentAcademicProfile {
  id: string;
  institution_id: string;
  program_id: string;
  profile_id?: string | null;
  enrollment_number: string;
  admission_number?: string | null;
  first_name: string;
  last_name: string;
  email?: string | null;
  department: string;
  admission_year: number;
  current_semester: number;
  academic_status: string;
  program_name?: string | null;
  created_at: string;
  updated_at: string;
}

export interface StudentSubjectEnrollment {
  id: string;
  institution_id: string;
  student_id: string;
  subject_id: string;
  academic_year: string;
  semester: number;
  enrollment_status: string;
  student_name?: string | null;
  enrollment_number?: string | null;
  subject_code?: string | null;
  subject_name?: string | null;
  enrolled_at: string;
  created_at: string;
  updated_at: string;
}

export interface AcademicAssessment {
  id: string;
  institution_id: string;
  subject_id: string;
  subject_name?: string | null;
  subject_code?: string | null;
  academic_year: string;
  semester: number;
  assessment_name: string;
  assessment_type: AssessmentType;
  maximum_marks: number;
  passing_marks?: number | null;
  weightage_percentage?: number | null;
  assessment_date?: string | null;
  description?: string | null;
  status: string;
  created_by?: string | null;
  created_at: string;
  updated_at: string;
}

export interface StudentAssessmentRecord {
  id: string;
  institution_id: string;
  student_id: string;
  student_name?: string | null;
  enrollment_number?: string | null;
  assessment_id: string;
  assessment_name?: string | null;
  assessment_type?: AssessmentType | null;
  subject_id?: string | null;
  subject_code?: string | null;
  marks_obtained?: number | null;
  maximum_marks_snapshot: number;
  result_status: AssessmentResultStatus;
  source_type: string;
  verification_status: RecordVerificationStatus;
  recorded_by?: string | null;
  verified_by?: string | null;
  recorded_at: string;
  verified_at?: string | null;
  source_reference?: string | null;
  remarks?: string | null;
  created_at: string;
  updated_at: string;
}

export interface StudentAttendanceRecord {
  id: string;
  institution_id: string;
  student_id: string;
  student_name?: string | null;
  enrollment_number?: string | null;
  subject_id: string;
  subject_code?: string | null;
  subject_name?: string | null;
  academic_year: string;
  semester: number;
  attendance_date: string;
  session_name: string;
  attendance_status: AttendanceStatus;
  source_type: string;
  verification_status: RecordVerificationStatus;
  recorded_by?: string | null;
  verified_by?: string | null;
  source_reference?: string | null;
  created_at: string;
  updated_at: string;
}

export interface AcademicImportError {
  id: string;
  job_id: string;
  row_number: number;
  column_name?: string | null;
  raw_data?: Record<string, unknown> | null;
  error_code: string;
  error_message: string;
  created_at: string;
}

export interface AcademicImportJob {
  id: string;
  institution_id: string;
  uploaded_by?: string | null;
  file_name: string;
  file_size_bytes: number;
  mime_type: string;
  storage_path: string;
  import_category: ImportCategory;
  status: ImportJobStatus;
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  duplicate_rows: number;
  imported_rows: number;
  preview_data?: Array<Record<string, unknown>> | null;
  error_summary?: Record<string, unknown> | null;
  completed_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface AcademicDataQualityFinding {
  id: string;
  institution_id: string;
  rule_identifier: string;
  entity_type: string;
  entity_id: string;
  severity: DataQualitySeverity;
  description: string;
  source_record?: Record<string, unknown> | null;
  recommended_action?: string | null;
  resolution_status: string;
  resolved_by?: string | null;
  resolved_at?: string | null;
  created_at: string;
}

export interface AcademicRecordAudit {
  id: string;
  institution_id: string;
  entity_type: string;
  entity_id: string;
  actor_id?: string | null;
  actor_name?: string | null;
  action: string;
  before_state?: Record<string, unknown> | null;
  after_state?: Record<string, unknown> | null;
  reason?: string | null;
  created_at: string;
}

export interface AcademicDataOverview {
  total_students: number;
  active_enrollments: number;
  total_assessments: number;
  performance_records_count: number;
  attendance_records_count: number;
  pending_verifications_count: number;
  data_quality_issues_count: number;
  total_import_jobs: number;
}

export const academicDataService = {
  // Overview
  getOverview: async (institutionId?: string): Promise<AcademicDataOverview> => {
    const q = institutionId ? `?institution_id=${institutionId}` : '';
    return apiClient.get<AcademicDataOverview>(`/academic-data/overview${q}`);
  },

  // Students
  getStudents: async (params?: {
    program_id?: string;
    semester?: number;
    search?: string;
    institution_id?: string;
    skip?: number;
    limit?: number;
  }): Promise<StudentAcademicProfile[]> => {
    const sp = new URLSearchParams();
    if (params?.program_id) sp.append('program_id', params.program_id);
    if (params?.semester) sp.append('semester', params.semester.toString());
    if (params?.search) sp.append('search', params.search);
    if (params?.institution_id) sp.append('institution_id', params.institution_id);
    if (params?.skip) sp.append('skip', params.skip.toString());
    if (params?.limit) sp.append('limit', params.limit.toString());
    const q = sp.toString() ? `?${sp.toString()}` : '';
    return apiClient.get<StudentAcademicProfile[]>(`/academic-data/students${q}`);
  },

  getStudentDetail: async (studentId: string): Promise<StudentAcademicProfile> => {
    return apiClient.get<StudentAcademicProfile>(`/academic-data/students/${studentId}`);
  },

  createStudent: async (data: Partial<StudentAcademicProfile>): Promise<StudentAcademicProfile> => {
    return apiClient.post<StudentAcademicProfile>('/academic-data/students', data);
  },

  updateStudent: async (studentId: string, data: Partial<StudentAcademicProfile>): Promise<StudentAcademicProfile> => {
    return apiClient.patch<StudentAcademicProfile>(`/academic-data/students/${studentId}`, data);
  },

  // Enrollments
  enrollStudent: async (data: Partial<StudentSubjectEnrollment>): Promise<StudentSubjectEnrollment> => {
    return apiClient.post<StudentSubjectEnrollment>('/academic-data/enrollments', data);
  },

  getStudentEnrollments: async (studentId: string): Promise<StudentSubjectEnrollment[]> => {
    return apiClient.get<StudentSubjectEnrollment[]>(`/academic-data/students/${studentId}/enrollments`);
  },

  // Assessments
  getAssessments: async (params?: {
    subject_id?: string;
    academic_year?: string;
    semester?: number;
    institution_id?: string;
  }): Promise<AcademicAssessment[]> => {
    const sp = new URLSearchParams();
    if (params?.subject_id) sp.append('subject_id', params.subject_id);
    if (params?.academic_year) sp.append('academic_year', params.academic_year);
    if (params?.semester) sp.append('semester', params.semester.toString());
    if (params?.institution_id) sp.append('institution_id', params.institution_id);
    const q = sp.toString() ? `?${sp.toString()}` : '';
    return apiClient.get<AcademicAssessment[]>(`/academic-data/assessments${q}`);
  },

  createAssessment: async (data: Partial<AcademicAssessment>): Promise<AcademicAssessment> => {
    return apiClient.post<AcademicAssessment>('/academic-data/assessments', data);
  },

  // Performance Records
  recordPerformance: async (data: Partial<StudentAssessmentRecord>): Promise<StudentAssessmentRecord> => {
    return apiClient.post<StudentAssessmentRecord>('/academic-data/performance', data);
  },

  getStudentPerformance: async (studentId: string): Promise<StudentAssessmentRecord[]> => {
    return apiClient.get<StudentAssessmentRecord[]>(`/academic-data/students/${studentId}/performance`);
  },

  // Attendance
  recordAttendance: async (data: Partial<StudentAttendanceRecord>): Promise<StudentAttendanceRecord> => {
    return apiClient.post<StudentAttendanceRecord>('/academic-data/attendance', data);
  },

  getStudentAttendance: async (
    studentId: string,
    params?: { subject_id?: string; semester?: number }
  ): Promise<StudentAttendanceRecord[]> => {
    const sp = new URLSearchParams();
    if (params?.subject_id) sp.append('subject_id', params.subject_id);
    if (params?.semester) sp.append('semester', params.semester.toString());
    const q = sp.toString() ? `?${sp.toString()}` : '';
    return apiClient.get<StudentAttendanceRecord[]>(`/academic-data/students/${studentId}/attendance${q}`);
  },

  // Import Workflows
  uploadImport: async (file: File, category: ImportCategory, institutionId?: string): Promise<AcademicImportJob> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);
    if (institutionId) formData.append('institution_id', institutionId);
    return apiClient.post<AcademicImportJob>('/academic-data/imports', formData);
  },

  getImports: async (institutionId?: string): Promise<AcademicImportJob[]> => {
    const q = institutionId ? `?institution_id=${institutionId}` : '';
    return apiClient.get<AcademicImportJob[]>(`/academic-data/imports${q}`);
  },

  getImportJob: async (jobId: string): Promise<AcademicImportJob> => {
    return apiClient.get<AcademicImportJob>(`/academic-data/imports/${jobId}`);
  },

  confirmImport: async (jobId: string, allowPartial: boolean = true): Promise<AcademicImportJob> => {
    return apiClient.post<AcademicImportJob>(`/academic-data/imports/${jobId}/confirm`, {
      allow_partial: allowPartial,
    });
  },

  getImportErrors: async (jobId: string): Promise<AcademicImportError[]> => {
    return apiClient.get<AcademicImportError[]>(`/academic-data/imports/${jobId}/errors`);
  },

  // Quality Intelligence
  scanDataQuality: async (institutionId?: string): Promise<AcademicDataQualityFinding[]> => {
    const q = institutionId ? `?institution_id=${institutionId}` : '';
    return apiClient.post<AcademicDataQualityFinding[]>(`/academic-data/quality/scan${q}`);
  },

  getQualityFindings: async (params?: {
    severity?: string;
    entity_type?: string;
    institution_id?: string;
  }): Promise<AcademicDataQualityFinding[]> => {
    const sp = new URLSearchParams();
    if (params?.severity) sp.append('severity', params.severity);
    if (params?.entity_type) sp.append('entity_type', params.entity_type);
    if (params?.institution_id) sp.append('institution_id', params.institution_id);
    const q = sp.toString() ? `?${sp.toString()}` : '';
    return apiClient.get<AcademicDataQualityFinding[]>(`/academic-data/quality${q}`);
  },

  resolveFinding: async (findingId: string): Promise<AcademicDataQualityFinding> => {
    return apiClient.post<AcademicDataQualityFinding>(`/academic-data/quality/${findingId}/resolve`);
  },

  // Verification & Audit
  verifyRecord: async (recordId: string, action: string, reason?: string): Promise<StudentAssessmentRecord> => {
    return apiClient.post<StudentAssessmentRecord>(`/academic-data/records/${recordId}/verify`, { action, reason });
  },

  correctRecord: async (
    recordId: string,
    data: { marks_obtained?: number; result_status?: AssessmentResultStatus; reason: string }
  ): Promise<StudentAssessmentRecord> => {
    return apiClient.post<StudentAssessmentRecord>(`/academic-data/records/${recordId}/correction`, data);
  },

  getAudits: async (params?: {
    entity_id?: string;
    entity_type?: string;
    institution_id?: string;
  }): Promise<AcademicRecordAudit[]> => {
    const sp = new URLSearchParams();
    if (params?.entity_id) sp.append('entity_id', params.entity_id);
    if (params?.entity_type) sp.append('entity_type', params.entity_type);
    if (params?.institution_id) sp.append('institution_id', params.institution_id);
    const q = sp.toString() ? `?${sp.toString()}` : '';
    return apiClient.get<AcademicRecordAudit[]>(`/academic-data/audits${q}`);
  },
};
