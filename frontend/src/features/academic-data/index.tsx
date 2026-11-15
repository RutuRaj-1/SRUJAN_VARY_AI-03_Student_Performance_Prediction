import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  academicDataService,
  AssessmentType,
  ImportCategory,
  DataQualitySeverity,
} from '@/services/academic-data-service';
import { syllabusService } from '@/services/syllabus-service';
import { useAuth } from '@/context/auth-context';

export const AcademicDataPage: React.FC = () => {
  const { profile } = useAuth();
  const queryClient = useQueryClient();

  // Navigation tab state
  const [activeTab, setActiveTab] = useState<'overview' | 'students' | 'assessments' | 'attendance' | 'imports' | 'quality'>('overview');

  // Selected student for detailed profile view
  const [selectedStudentId, setSelectedStudentId] = useState<string | null>(null);

  // Student directory filters & search
  const [studentSearch, setStudentSearch] = useState('');
  const [semesterFilter, setSemesterFilter] = useState<number | undefined>(undefined);

  // Form states
  const [showCreateStudentModal, setShowCreateStudentModal] = useState(false);
  const [newEnrNum, setNewEnrNum] = useState('');
  const [newFirstName, setNewFirstName] = useState('');
  const [newLastName, setNewLastName] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [newDept, setNewDept] = useState('Computer Science & Engineering');
  const [newSemester, setNewSemester] = useState(4);
  const [newProgramId, setNewProgramId] = useState('');

  // Assessment form states
  const [showCreateAsmtModal, setShowCreateAsmtModal] = useState(false);
  const [asmtSubjectId, setAsmtSubjectId] = useState('');
  const [asmtName, setAsmtName] = useState('');
  const [asmtType, setAsmtType] = useState<AssessmentType>('INTERNAL_TEST');
  const [asmtMaxMarks, setAsmtMaxMarks] = useState(50);
  const [asmtPassingMarks, setAsmtPassingMarks] = useState(20);
  const [asmtYear, setAsmtYear] = useState('2024-2025');
  const [asmtSemester, setAsmtSemester] = useState(4);

  // Record Marks states
  const [recordMarksStudentId, setRecordMarksStudentId] = useState('');
  const [recordMarksAsmtId, setRecordMarksAsmtId] = useState('');
  const [recordMarksValue, setRecordMarksValue] = useState<number | ''>('');
  const [recordMarksStatus, setRecordMarksStatus] = useState('PASSED');
  const [recordMarksRemarks, setRecordMarksRemarks] = useState('');

  // Record Attendance states
  const [attStudentId, setAttStudentId] = useState('');
  const [attSubjectId, setAttSubjectId] = useState('');
  const [attDate, setAttDate] = useState(new Date().toISOString().split('T')[0]);
  const [attSessionName, setAttSessionName] = useState('Lecture 01');
  const [attStatus, setAttStatus] = useState<'PRESENT' | 'ABSENT' | 'LATE' | 'EXCUSED' | 'NOT_RECORDED'>('PRESENT');

  // Import form states
  const [importFile, setImportFile] = useState<File | null>(null);
  const [importCategory, setImportCategory] = useState<ImportCategory>('STUDENTS');
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);

  // Correction Modal state
  const [correctionRecordId, setCorrectionRecordId] = useState<string | null>(null);
  const [correctionMarks, setCorrectionMarks] = useState<number>(0);
  const [correctionReason, setCorrectionReason] = useState('');

  // Queries
  const { data: overview, isLoading: overviewLoading } = useQuery({
    queryKey: ['academic', 'overview'],
    queryFn: () => academicDataService.getOverview(),
  });

  const { data: students = [], isLoading: studentsLoading } = useQuery({
    queryKey: ['academic', 'students', studentSearch, semesterFilter],
    queryFn: () => academicDataService.getStudents({ search: studentSearch || undefined, semester: semesterFilter }),
  });

  const { data: programs = [] } = useQuery({
    queryKey: ['syllabus', 'programs'],
    queryFn: () => syllabusService.getPrograms(),
  });

  const { data: subjects = [] } = useQuery({
    queryKey: ['syllabus', 'subjects'],
    queryFn: () => syllabusService.getSubjects(),
  });

  const { data: assessments = [], isLoading: asmtLoading } = useQuery({
    queryKey: ['academic', 'assessments'],
    queryFn: () => academicDataService.getAssessments(),
  });

  const { data: selectedStudent, isLoading: studentDetailLoading } = useQuery({
    queryKey: ['academic', 'student-detail', selectedStudentId],
    queryFn: () => academicDataService.getStudentDetail(selectedStudentId!),
    enabled: !!selectedStudentId,
  });

  const { data: studentEnrollments = [] } = useQuery({
    queryKey: ['academic', 'student-enrollments', selectedStudentId],
    queryFn: () => academicDataService.getStudentEnrollments(selectedStudentId!),
    enabled: !!selectedStudentId,
  });

  const { data: studentPerformance = [] } = useQuery({
    queryKey: ['academic', 'student-performance', selectedStudentId],
    queryFn: () => academicDataService.getStudentPerformance(selectedStudentId!),
    enabled: !!selectedStudentId,
  });

  const { data: studentAttendance = [] } = useQuery({
    queryKey: ['academic', 'student-attendance', selectedStudentId],
    queryFn: () => academicDataService.getStudentAttendance(selectedStudentId!),
    enabled: !!selectedStudentId,
  });

  const { data: importJobs = [], isLoading: importsLoading } = useQuery({
    queryKey: ['academic', 'imports'],
    queryFn: () => academicDataService.getImports(),
  });

  const { data: activeImportJob } = useQuery({
    queryKey: ['academic', 'import-job', selectedJobId],
    queryFn: () => academicDataService.getImportJob(selectedJobId!),
    enabled: !!selectedJobId,
  });

  const { data: importErrors = [] } = useQuery({
    queryKey: ['academic', 'import-errors', selectedJobId],
    queryFn: () => academicDataService.getImportErrors(selectedJobId!),
    enabled: !!selectedJobId,
  });

  const { data: qualityFindings = [], isLoading: qualityLoading } = useQuery({
    queryKey: ['academic', 'quality'],
    queryFn: () => academicDataService.getQualityFindings(),
  });

  // Mutations
  const createStudentMutation = useMutation({
    mutationFn: async () => {
      let targetProgId = newProgramId;
      if (!targetProgId && programs.length > 0) targetProgId = programs[0].id;
      if (!targetProgId) {
        const newProg = await syllabusService.createProgram({
          name: 'B.Tech Computer Science & Engineering',
          code: 'BTECH-CSE',
          degree_type: 'Bachelor of Technology',
          duration_years: 4,
          institution_id: profile?.institution_id || undefined,
        });
        targetProgId = newProg.id;
      }

      return academicDataService.createStudent({
        institution_id: profile?.institution_id || undefined,
        program_id: targetProgId,
        enrollment_number: newEnrNum,
        first_name: newFirstName,
        last_name: newLastName,
        email: newEmail || undefined,
        department: newDept,
        admission_year: 2022,
        current_semester: newSemester,
        academic_status: 'ENROLLED',
      });
    },
    onSuccess: () => {
      setShowCreateStudentModal(false);
      setNewEnrNum('');
      setNewFirstName('');
      setNewLastName('');
      setNewEmail('');
      queryClient.invalidateQueries({ queryKey: ['academic'] });
    },
  });

  const createAsmtMutation = useMutation({
    mutationFn: () =>
      academicDataService.createAssessment({
        institution_id: profile?.institution_id || undefined,
        subject_id: asmtSubjectId || subjects[0]?.id,
        assessment_name: asmtName,
        assessment_type: asmtType,
        maximum_marks: asmtMaxMarks,
        passing_marks: asmtPassingMarks,
        academic_year: asmtYear,
        semester: asmtSemester,
      }),
    onSuccess: () => {
      setShowCreateAsmtModal(false);
      setAsmtName('');
      queryClient.invalidateQueries({ queryKey: ['academic', 'assessments'] });
      queryClient.invalidateQueries({ queryKey: ['academic', 'overview'] });
    },
  });

  const recordPerformanceMutation = useMutation({
    mutationFn: () =>
      academicDataService.recordPerformance({
        institution_id: profile?.institution_id || undefined,
        student_id: recordMarksStudentId || students[0]?.id,
        assessment_id: recordMarksAsmtId || assessments[0]?.id,
        marks_obtained: recordMarksValue === '' ? null : Number(recordMarksValue),
        result_status: recordMarksStatus as any,
        remarks: recordMarksRemarks || undefined,
      }),
    onSuccess: () => {
      setRecordMarksValue('');
      setRecordMarksRemarks('');
      queryClient.invalidateQueries({ queryKey: ['academic'] });
    },
  });

  const recordAttendanceMutation = useMutation({
    mutationFn: () =>
      academicDataService.recordAttendance({
        institution_id: profile?.institution_id || undefined,
        student_id: attStudentId || students[0]?.id,
        subject_id: attSubjectId || subjects[0]?.id,
        academic_year: '2024-2025',
        semester: 4,
        attendance_date: new Date(attDate).toISOString(),
        session_name: attSessionName,
        attendance_status: attStatus,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['academic'] });
    },
  });

  const uploadImportMutation = useMutation({
    mutationFn: () => {
      if (!importFile) throw new Error('Please select a CSV or XLSX file.');
      return academicDataService.uploadImport(importFile, importCategory, profile?.institution_id || undefined);
    },
    onSuccess: (job) => {
      setImportFile(null);
      setSelectedJobId(job.id);
      queryClient.invalidateQueries({ queryKey: ['academic', 'imports'] });
    },
  });

  const confirmImportMutation = useMutation({
    mutationFn: (jobId: string) => academicDataService.confirmImport(jobId, true),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['academic'] });
    },
  });

  const scanQualityMutation = useMutation({
    mutationFn: () => academicDataService.scanDataQuality(profile?.institution_id || undefined),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['academic', 'quality'] });
      queryClient.invalidateQueries({ queryKey: ['academic', 'overview'] });
    },
  });

  const resolveFindingMutation = useMutation({
    mutationFn: (findingId: string) => academicDataService.resolveFinding(findingId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['academic', 'quality'] });
    },
  });

  const verifyRecordMutation = useMutation({
    mutationFn: ({ recordId, action }: { recordId: string; action: string }) =>
      academicDataService.verifyRecord(recordId, action, 'Verified by authorized faculty.'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['academic'] });
    },
  });

  const correctRecordMutation = useMutation({
    mutationFn: ({ recordId, marks, reason }: { recordId: string; marks: number; reason: string }) =>
      academicDataService.correctRecord(recordId, { marks_obtained: marks, reason }),
    onSuccess: () => {
      setCorrectionRecordId(null);
      setCorrectionReason('');
      queryClient.invalidateQueries({ queryKey: ['academic'] });
    },
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-slate-200 pb-5">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <span className="inline-flex items-center rounded-md bg-blue-50 px-2.5 py-1 text-xs font-semibold text-blue-700 ring-1 ring-inset ring-blue-700/10">
                Module 03
              </span>
              <span className="inline-flex items-center rounded-md bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-700">
                Phase 04 / 11
              </span>
              <span className="text-xs text-slate-500 font-mono">
                {profile?.institution_id ? `Institution: ${profile.institution_id.slice(0, 8)}...` : 'System Mode'}
              </span>
            </div>
            <h1 className="mt-2 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
              Academic Data Intelligence Hub
            </h1>
            <p className="mt-1 text-sm text-slate-600">
              Trusted, evidence-based academic data foundation. Collecting, importing, validating, managing, and auditing institutional student records.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => scanQualityMutation.mutate()}
              disabled={scanQualityMutation.isPending}
              className="inline-flex items-center gap-1.5 rounded-lg bg-white border border-slate-300 px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 shadow-sm disabled:opacity-50"
            >
              🔍 {scanQualityMutation.isPending ? 'Scanning Quality...' : 'Run Data Quality Scan'}
            </button>
            <button
              onClick={() => setShowCreateStudentModal(true)}
              className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3.5 py-2 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500"
            >
              + New Student Profile
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="mt-6 flex border-b border-slate-200 gap-6 text-sm font-medium overflow-x-auto">
          {[
            { id: 'overview', label: '1. Academic Overview' },
            { id: 'students', label: `2. Student Directory (${students.length})` },
            { id: 'assessments', label: `3. Assessments & Marks (${assessments.length})` },
            { id: 'attendance', label: '4. Attendance Ledgers' },
            { id: 'imports', label: `5. Import Center (${importJobs.length})` },
            { id: 'quality', label: `6. Data Quality Intelligence (${qualityFindings.length})` },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => {
                setActiveTab(tab.id as any);
                if (tab.id !== 'students') setSelectedStudentId(null);
              }}
              className={`pb-3 border-b-2 whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'border-indigo-600 text-indigo-600 font-semibold'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* TAB 1: Academic Overview */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {overviewLoading ? (
            <div className="p-12 text-center text-xs text-slate-500 bg-white border border-slate-200 rounded-xl">
              Loading academic data metrics from live database...
            </div>
          ) : (
            <>
              {/* Stat Cards Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <MetricCard title="Total Students" value={overview?.total_students || 0} icon="👨‍🎓" note="Institution-scoped profiles" />
                <MetricCard title="Active Enrollments" value={overview?.active_enrollments || 0} icon="📚" note="Course registrations" />
                <MetricCard title="Assessments Configured" value={overview?.total_assessments || 0} icon="📝" note="Exams, tests & labs" />
                <MetricCard title="Performance Records" value={overview?.performance_records_count || 0} icon="📊" note="Evaluated marks" />
                <MetricCard title="Attendance Records" value={overview?.attendance_records_count || 0} icon="📅" note="Tracked sessions" />
                <MetricCard
                  title="Pending Verifications"
                  value={overview?.pending_verifications_count || 0}
                  icon="⏳"
                  note="Faculty review required"
                  highlight={Boolean(overview?.pending_verifications_count && overview.pending_verifications_count > 0)}
                />
                <MetricCard
                  title="Quality Findings"
                  value={overview?.data_quality_issues_count || 0}
                  icon="⚠️"
                  note="Data integrity alerts"
                  warning={Boolean(overview?.data_quality_issues_count && overview.data_quality_issues_count > 0)}
                />
                <MetricCard title="Import Batches" value={overview?.total_import_jobs || 0} icon="📁" note="Processed spreadsheets" />
              </div>

              {/* Data Integrity Principles Callout */}
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 text-xs text-slate-600 space-y-2">
                <h3 className="text-sm font-bold text-slate-900">Evidence Provenance & Academic Integrity Core Principles</h3>
                <p>
                  • <strong>Missing Data vs. Poor Performance:</strong> MASTERY never converts missing marks or unrecorded attendance into zero scores.
                </p>
                <p>
                  • <strong>Verified vs. Unverified State:</strong> Imported records remain in <code className="bg-white px-1 rounded text-slate-800">IMPORTED</code> state until validated and signed off by authorized faculty.
                </p>
                <p>
                  • <strong>Audit Immutability:</strong> Any alteration to a verified academic record enforces an explicit reason and permanent snapshot in <code className="bg-white px-1 rounded text-slate-800">academic_record_audits</code>.
                </p>
              </div>
            </>
          )}
        </div>
      )}

      {/* TAB 2: Student Directory & Detailed Academic Profile */}
      {activeTab === 'students' && (
        <div className="space-y-6">
          {selectedStudentId && studentDetailLoading && (
            <div className="p-8 text-center text-slate-500 bg-white rounded-xl border border-slate-200">
              Loading student academic profile...
            </div>
          )}
          {selectedStudentId && selectedStudent && !studentDetailLoading ? (
            /* Student Detailed View */
            <div className="space-y-6">
              <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
                  <div>
                    <button
                      onClick={() => setSelectedStudentId(null)}
                      className="text-xs text-indigo-600 hover:text-indigo-800 font-semibold mb-2 inline-flex items-center gap-1"
                    >
                      ← Back to Student Directory
                    </button>
                    <h2 className="text-xl font-bold text-slate-900">
                      {selectedStudent.first_name} {selectedStudent.last_name}
                    </h2>
                    <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 mt-1">
                      <span className="font-mono font-semibold text-slate-800">Enrollment: {selectedStudent.enrollment_number}</span>
                      <span>•</span>
                      <span>Department: {selectedStudent.department}</span>
                      <span>•</span>
                      <span>Semester: {selectedStudent.current_semester}</span>
                      <span>•</span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">
                        {selectedStudent.academic_status}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Subsections: Enrollments, Performance Records, Attendance */}
                <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Subject Enrollments */}
                  <div className="border border-slate-200 rounded-xl p-4 bg-slate-50/50">
                    <h3 className="text-xs font-bold uppercase text-slate-700 tracking-wider mb-3">
                      Enrolled Courses ({studentEnrollments.length})
                    </h3>
                    {studentEnrollments.length === 0 ? (
                      <p className="text-xs text-slate-500 italic">No course enrollments found.</p>
                    ) : (
                      <div className="space-y-2">
                        {studentEnrollments.map((enr) => (
                          <div key={enr.id} className="p-3 bg-white rounded-lg border border-slate-200 flex justify-between items-center text-xs">
                            <div>
                              <span className="font-bold text-slate-900">{enr.subject_code}</span>
                              <span className="block text-slate-600 text-[11px]">Academic Year {enr.academic_year} • Sem {enr.semester}</span>
                            </div>
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-800">
                              {enr.enrollment_status}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Attendance History */}
                  <div className="border border-slate-200 rounded-xl p-4 bg-slate-50/50">
                    <h3 className="text-xs font-bold uppercase text-slate-700 tracking-wider mb-3">
                      Attendance Ledgers ({studentAttendance.length})
                    </h3>
                    {studentAttendance.length === 0 ? (
                      <p className="text-xs text-slate-500 italic">No attendance records logged.</p>
                    ) : (
                      <div className="space-y-2 max-h-60 overflow-y-auto">
                        {studentAttendance.map((att) => (
                          <div key={att.id} className="p-2.5 bg-white rounded-lg border border-slate-200 flex justify-between items-center text-xs">
                            <div>
                              <span className="font-semibold text-slate-900">{new Date(att.attendance_date).toLocaleDateString()}</span>
                              <span className="block text-slate-500 text-[11px]">{att.session_name}</span>
                            </div>
                            <AttendanceBadge status={att.attendance_status} />
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {/* Academic Marks & Performance Table */}
                <div className="mt-6 border border-slate-200 rounded-xl overflow-hidden">
                  <div className="p-4 bg-slate-50 border-b border-slate-200 flex justify-between items-center">
                    <h3 className="text-xs font-bold uppercase text-slate-700 tracking-wider">
                      Academic Assessments & Marks Ledger ({studentPerformance.length})
                    </h3>
                  </div>
                  {studentPerformance.length === 0 ? (
                    <div className="p-8 text-center text-xs text-slate-500 italic">
                      No assessment marks recorded for this student.
                    </div>
                  ) : (
                    <table className="min-w-full divide-y divide-slate-200 text-xs">
                      <thead className="bg-slate-100/70 text-slate-700 font-semibold">
                        <tr>
                          <th className="px-4 py-3 text-left">Assessment</th>
                          <th className="px-4 py-3 text-left">Marks Obtained</th>
                          <th className="px-4 py-3 text-left">Max Marks</th>
                          <th className="px-4 py-3 text-left">Result Status</th>
                          <th className="px-4 py-3 text-left">Verification Status</th>
                          <th className="px-4 py-3 text-right">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 bg-white">
                        {studentPerformance.map((rec) => (
                          <tr key={rec.id} className="hover:bg-slate-50">
                            <td className="px-4 py-3 font-semibold text-slate-900">{rec.assessment_name || 'Assessment'}</td>
                            <td className="px-4 py-3 font-mono font-bold text-indigo-700">
                              {rec.marks_obtained !== null ? rec.marks_obtained : <span className="text-slate-400">—</span>}
                            </td>
                            <td className="px-4 py-3 text-slate-600">{rec.maximum_marks_snapshot}</td>
                            <td className="px-4 py-3">
                              <ResultBadge status={rec.result_status} />
                            </td>
                            <td className="px-4 py-3">
                              <VerificationBadge status={rec.verification_status} />
                            </td>
                            <td className="px-4 py-3 text-right space-x-2">
                              {rec.verification_status !== 'VERIFIED' && (
                                <button
                                  onClick={() => verifyRecordMutation.mutate({ recordId: rec.id, action: 'VERIFY' })}
                                  className="text-xs text-emerald-600 hover:text-emerald-800 font-semibold"
                                >
                                  Verify
                                </button>
                              )}
                              <button
                                onClick={() => {
                                  setCorrectionRecordId(rec.id);
                                  setCorrectionMarks(rec.marks_obtained || 0);
                                }}
                                className="text-xs text-indigo-600 hover:text-indigo-800 font-semibold"
                              >
                                Correct
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              </div>
            </div>
          ) : (
            /* Student Directory Table */
            <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
              <div className="p-4 border-b border-slate-200 flex flex-col sm:flex-row gap-4 justify-between items-center">
                <div className="w-full sm:w-80">
                  <input
                    type="text"
                    value={studentSearch}
                    onChange={(e) => setStudentSearch(e.target.value)}
                    placeholder="Search by enrollment, name, or email..."
                    className="w-full text-xs rounded-lg border border-slate-300 p-2 focus:ring-indigo-500"
                  />
                </div>
                <div className="flex items-center gap-2">
                  <label htmlFor="semester-filter" className="text-xs text-slate-600 font-semibold">Semester:</label>
                  <select
                    id="semester-filter"
                    value={semesterFilter || ''}
                    onChange={(e) => setSemesterFilter(e.target.value ? parseInt(e.target.value) : undefined)}
                    className="text-xs rounded-lg border border-slate-300 p-1.5 focus:ring-indigo-500"
                  >
                    <option value="">All Semesters</option>
                    {[1, 2, 3, 4, 5, 6, 7, 8].map((s) => (
                      <option key={s} value={s}>Semester {s}</option>
                    ))}
                  </select>
                </div>
              </div>

              {studentsLoading ? (
                <div className="p-12 text-center text-xs text-slate-500">Loading student profiles...</div>
              ) : students.length === 0 ? (
                <div className="p-12 text-center text-xs text-slate-500">
                  <p className="font-semibold text-slate-700">No student profiles found.</p>
                  <p className="mt-1">Add student profiles manually or use the Academic Import Center.</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-slate-200 text-xs">
                    <thead className="bg-slate-100/70 text-slate-700 font-semibold">
                      <tr>
                        <th className="px-4 py-3 text-left">Enrollment No.</th>
                        <th className="px-4 py-3 text-left">Student Name</th>
                        <th className="px-4 py-3 text-left">Department</th>
                        <th className="px-4 py-3 text-left">Semester</th>
                        <th className="px-4 py-3 text-left">Status</th>
                        <th className="px-4 py-3 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {students.map((stud) => (
                        <tr key={stud.id} className="hover:bg-slate-50">
                          <td className="px-4 py-3 font-mono font-bold text-slate-900">{stud.enrollment_number}</td>
                          <td className="px-4 py-3 font-semibold text-slate-800">
                            {stud.first_name} {stud.last_name}
                            {stud.email && <span className="block text-[11px] text-slate-400 font-normal">{stud.email}</span>}
                          </td>
                          <td className="px-4 py-3 text-slate-600">{stud.department}</td>
                          <td className="px-4 py-3 text-slate-600">Sem {stud.current_semester}</td>
                          <td className="px-4 py-3">
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">
                              {stud.academic_status}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-right">
                            <button
                              onClick={() => setSelectedStudentId(stud.id)}
                              className="text-xs text-indigo-600 hover:text-indigo-800 font-semibold"
                            >
                              View Academic Profile →
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* TAB 3: Assessments & Marks Workspace */}
      {activeTab === 'assessments' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Record Marks Form */}
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
              <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-2">Record Student Marks</h3>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Select Student</label>
                <select
                  value={recordMarksStudentId}
                  onChange={(e) => setRecordMarksStudentId(e.target.value)}
                  className="w-full text-xs rounded-lg border border-slate-300 p-2"
                >
                  {students.map((s) => (
                    <option key={s.id} value={s.id}>{s.enrollment_number} — {s.first_name} {s.last_name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Select Assessment</label>
                <select
                  value={recordMarksAsmtId}
                  onChange={(e) => setRecordMarksAsmtId(e.target.value)}
                  className="w-full text-xs rounded-lg border border-slate-300 p-2"
                >
                  {assessments.map((a) => (
                    <option key={a.id} value={a.id}>{a.assessment_name} (Max: {a.maximum_marks})</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Marks Obtained</label>
                  <input
                    type="number"
                    step="0.5"
                    value={recordMarksValue}
                    onChange={(e) => setRecordMarksValue(e.target.value === '' ? '' : Number(e.target.value))}
                    placeholder="e.g. 42.5"
                    className="w-full text-xs rounded-lg border border-slate-300 p-2"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Result Status</label>
                  <select
                    value={recordMarksStatus}
                    onChange={(e) => setRecordMarksStatus(e.target.value)}
                    className="w-full text-xs rounded-lg border border-slate-300 p-2"
                  >
                    <option value="PASSED">PASSED</option>
                    <option value="FAILED">FAILED</option>
                    <option value="ABSENT">ABSENT</option>
                    <option value="NOT_SUBMITTED">NOT SUBMITTED</option>
                    <option value="EXEMPTED">EXEMPTED</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Remarks (Optional)</label>
                <input
                  type="text"
                  value={recordMarksRemarks}
                  onChange={(e) => setRecordMarksRemarks(e.target.value)}
                  placeholder="e.g. Completed with extra credit"
                  className="w-full text-xs rounded-lg border border-slate-300 p-2"
                />
              </div>

              <button
                onClick={() => recordPerformanceMutation.mutate()}
                disabled={recordPerformanceMutation.isPending || !students.length || !assessments.length}
                className="w-full py-2 bg-indigo-600 text-white rounded-lg text-xs font-bold hover:bg-indigo-500 disabled:opacity-50"
              >
                {recordPerformanceMutation.isPending ? 'Saving...' : 'Save Performance Record'}
              </button>
            </div>

            {/* Configured Assessments List */}
            <div className="md:col-span-2 bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
              <div className="flex justify-between items-center border-b border-slate-100 pb-2">
                <h3 className="text-sm font-bold text-slate-900">Configured Assessments ({assessments.length})</h3>
                <button
                  onClick={() => setShowCreateAsmtModal(true)}
                  className="text-xs font-semibold text-indigo-600 hover:text-indigo-800"
                >
                  + Add Assessment
                </button>
              </div>

              {asmtLoading ? (
                <div className="p-8 text-center text-xs text-slate-500">Loading assessments...</div>
              ) : assessments.length === 0 ? (
                <div className="p-8 text-center text-xs text-slate-500">No assessments defined yet.</div>
              ) : (
                <div className="divide-y divide-slate-100">
                  {assessments.map((asmt) => (
                    <div key={asmt.id} className="py-3 flex justify-between items-center text-xs">
                      <div>
                        <span className="font-bold text-slate-900">{asmt.assessment_name}</span>
                        <div className="flex items-center gap-3 text-slate-500 text-[11px] mt-0.5">
                          <span className="font-mono bg-slate-100 px-1.5 py-0.5 rounded">{asmt.assessment_type}</span>
                          <span>Year: {asmt.academic_year} (Sem {asmt.semester})</span>
                          <span>Max: {asmt.maximum_marks} pts</span>
                        </div>
                      </div>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-800">
                        {asmt.status}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: Attendance Ledgers */}
      {activeTab === 'attendance' && (
        <div className="space-y-6">
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm max-w-xl">
            <h3 className="text-sm font-bold text-slate-900 mb-4">Log Student Attendance Session</h3>
            <div className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Student</label>
                <select
                  value={attStudentId}
                  onChange={(e) => setAttStudentId(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 p-2"
                >
                  {students.map((s) => (
                    <option key={s.id} value={s.id}>{s.enrollment_number} — {s.first_name} {s.last_name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Subject</label>
                <select
                  value={attSubjectId}
                  onChange={(e) => setAttSubjectId(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 p-2"
                >
                  {subjects.map((sub) => (
                    <option key={sub.id} value={sub.id}>{sub.code} — {sub.name}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Date</label>
                  <input
                    type="date"
                    value={attDate}
                    onChange={(e) => setAttDate(e.target.value)}
                    className="w-full rounded-lg border border-slate-300 p-2"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Session Label</label>
                  <input
                    type="text"
                    value={attSessionName}
                    onChange={(e) => setAttSessionName(e.target.value)}
                    placeholder="e.g. Lecture 08"
                    className="w-full rounded-lg border border-slate-300 p-2"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Attendance Status</label>
                <select
                  value={attStatus}
                  onChange={(e) => setAttStatus(e.target.value as any)}
                  className="w-full rounded-lg border border-slate-300 p-2"
                >
                  <option value="PRESENT">PRESENT</option>
                  <option value="ABSENT">ABSENT</option>
                  <option value="LATE">LATE</option>
                  <option value="EXCUSED">EXCUSED</option>
                  <option value="NOT_RECORDED">NOT RECORDED</option>
                </select>
              </div>

              <button
                onClick={() => recordAttendanceMutation.mutate()}
                disabled={recordAttendanceMutation.isPending || !students.length || !subjects.length}
                className="w-full py-2 bg-indigo-600 text-white rounded-lg font-bold hover:bg-indigo-500 disabled:opacity-50"
              >
                {recordAttendanceMutation.isPending ? 'Logging...' : 'Save Attendance'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* TAB 5: Academic Import Center */}
      {activeTab === 'imports' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Upload File Form */}
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
              <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-2">Upload Spreadsheet</h3>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Import Category</label>
                <select
                  value={importCategory}
                  onChange={(e) => setImportCategory(e.target.value as any)}
                  className="w-full text-xs rounded-lg border border-slate-300 p-2"
                >
                  <option value="STUDENTS">Student Academic Profiles</option>
                  <option value="PERFORMANCE">Student Assessment Results</option>
                  <option value="ATTENDANCE">Attendance Records</option>
                </select>
              </div>

              <div className="border-2 border-dashed border-slate-300 rounded-xl p-6 text-center hover:border-indigo-400 transition-colors">
                <input
                  type="file"
                  id="academic-file"
                  accept=".csv,.xlsx"
                  onChange={(e) => setImportFile(e.target.files?.[0] || null)}
                  className="hidden"
                />
                <label htmlFor="academic-file" className="cursor-pointer flex flex-col items-center">
                  <span className="text-xs font-semibold text-indigo-600 hover:text-indigo-500">
                    Choose CSV or XLSX file
                  </span>
                  <span className="text-[11px] text-slate-500 mt-1">Up to 15MB</span>
                  {importFile && (
                    <span className="mt-2 inline-flex items-center px-2 py-0.5 rounded text-[10px] bg-indigo-50 text-indigo-700 font-mono">
                      📄 {importFile.name}
                    </span>
                  )}
                </label>
              </div>

              <button
                onClick={() => uploadImportMutation.mutate()}
                disabled={!importFile || uploadImportMutation.isPending}
                className="w-full py-2 bg-indigo-600 text-white rounded-lg text-xs font-bold hover:bg-indigo-500 disabled:opacity-50"
              >
                {uploadImportMutation.isPending ? 'Validating...' : 'Upload & Generate Preview'}
              </button>
            </div>

            {/* Import Jobs History */}
            <div className="md:col-span-2 bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
              <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-2">Recent Import Jobs</h3>
              {importsLoading ? (
                <div className="p-8 text-center text-xs text-slate-500">Loading import history...</div>
              ) : importJobs.length === 0 ? (
                <div className="p-8 text-center text-xs text-slate-500">No import jobs executed yet.</div>
              ) : (
                <div className="divide-y divide-slate-100">
                  {importJobs.map((job) => (
                    <div key={job.id} className="py-3 flex justify-between items-center text-xs">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-slate-900">{job.file_name}</span>
                          <span className="font-mono text-[10px] bg-slate-100 px-1.5 py-0.5 rounded">{job.import_category}</span>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            job.status === 'COMPLETED' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                          }`}>
                            {job.status}
                          </span>
                        </div>
                        <div className="flex items-center gap-4 text-[11px] text-slate-500 mt-1">
                          <span>Total: {job.total_rows}</span>
                          <span className="text-emerald-600 font-semibold">Valid: {job.valid_rows}</span>
                          {job.invalid_rows > 0 && <span className="text-rose-600 font-semibold">Invalid: {job.invalid_rows}</span>}
                          {job.duplicate_rows > 0 && <span className="text-amber-600 font-semibold">Duplicates: {job.duplicate_rows}</span>}
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        {job.status === 'PREVIEW_READY' && (
                          <button
                            onClick={() => confirmImportMutation.mutate(job.id)}
                            disabled={confirmImportMutation.isPending}
                            className="px-3 py-1 bg-emerald-600 text-white rounded text-xs font-semibold hover:bg-emerald-500"
                          >
                            Confirm Import
                          </button>
                        )}
                        <button
                          onClick={() => setSelectedJobId(job.id)}
                          className="px-3 py-1 bg-slate-100 text-slate-700 rounded text-xs hover:bg-slate-200"
                        >
                          View Details
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Job Preview & Errors Drawer */}
          {selectedJobId && activeImportJob && (
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
              <div className="flex justify-between items-center border-b border-slate-100 pb-3">
                <div>
                  <h4 className="text-sm font-bold text-slate-900">
                    Preview Data: {activeImportJob.file_name} ({activeImportJob.import_category})
                  </h4>
                  <p className="text-xs text-slate-500">Showing first rows parsed from spreadsheet</p>
                </div>
                {activeImportJob.status === 'PREVIEW_READY' && (
                  <button
                    onClick={() => confirmImportMutation.mutate(activeImportJob.id)}
                    className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-xs font-bold hover:bg-emerald-500"
                  >
                    Confirm & Execute Import ({activeImportJob.valid_rows} Valid Rows)
                  </button>
                )}
              </div>

              {importErrors.length > 0 && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700">
                  <span className="font-bold">Errors Detected ({importErrors.length}):</span>
                  <ul className="list-disc list-inside mt-1 space-y-0.5">
                    {importErrors.slice(0, 5).map((e) => (
                      <li key={e.id}>Row {e.row_number}: {e.error_message}</li>
                    ))}
                  </ul>
                </div>
              )}

              {activeImportJob.preview_data && activeImportJob.preview_data.length > 0 && (
                <div className="overflow-x-auto max-h-60">
                  <table className="min-w-full divide-y divide-slate-200 text-xs">
                    <thead className="bg-slate-100 text-slate-700 font-semibold">
                      <tr>
                        {Object.keys(activeImportJob.preview_data[0] || {}).map((col) => (
                          <th key={col} className="px-3 py-2 text-left uppercase text-[10px]">{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {activeImportJob.preview_data.map((row, rIdx) => (
                        <tr key={rIdx} className="hover:bg-slate-50">
                          {Object.values(row).map((val: any, cIdx) => (
                            <td key={cIdx} className="px-3 py-2 text-slate-800 font-mono text-[11px] whitespace-nowrap">
                              {String(val || '—')}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* TAB 6: Data Quality Intelligence */}
      {activeTab === 'quality' && (
        <div className="space-y-6">
          <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
            <div className="p-4 border-b border-slate-200 flex justify-between items-center">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Deterministic Data Quality Findings</h3>
                <p className="text-xs text-slate-500">Automated audit findings for boundary violations, missing references, and duplicate records.</p>
              </div>
              <button
                onClick={() => scanQualityMutation.mutate()}
                disabled={scanQualityMutation.isPending}
                className="px-3 py-1.5 bg-indigo-600 text-white rounded text-xs font-semibold hover:bg-indigo-500"
              >
                {scanQualityMutation.isPending ? 'Scanning...' : 'Re-scan Integrity'}
              </button>
            </div>

            {qualityLoading ? (
              <div className="p-12 text-center text-xs text-slate-500">Scanning data quality findings...</div>
            ) : qualityFindings.length === 0 ? (
              <div className="p-12 text-center text-xs text-slate-500">
                <span className="text-emerald-600 font-bold text-sm block mb-1">✓ No Data Integrity Violations Detected</span>
                All student profiles, marks boundaries, and attendance records satisfy strict consistency rules.
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {qualityFindings.map((finding) => (
                  <div key={finding.id} className="p-4 flex flex-col sm:flex-row sm:items-start justify-between gap-4 text-xs">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <SeverityBadge severity={finding.severity} />
                        <span className="font-mono font-bold text-slate-900">{finding.rule_identifier}</span>
                        <span className="bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded text-[10px]">{finding.entity_type}</span>
                      </div>
                      <p className="text-slate-800 font-medium">{finding.description}</p>
                      {finding.recommended_action && (
                        <p className="text-slate-500 text-[11px] mt-1">💡 Action: {finding.recommended_action}</p>
                      )}
                    </div>
                    {finding.resolution_status === 'OPEN' ? (
                      <button
                        onClick={() => resolveFindingMutation.mutate(finding.id)}
                        className="px-3 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-xs font-semibold whitespace-nowrap"
                      >
                        Mark Resolved
                      </button>
                    ) : (
                      <span className="text-emerald-700 font-bold text-xs whitespace-nowrap">✓ Resolved</span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Modal: Create Student Profile */}
      {showCreateStudentModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-xl space-y-4">
            <h3 className="text-base font-bold text-slate-900">Add Student Academic Profile</h3>
            <div className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Enrollment Number</label>
                <input
                  type="text"
                  value={newEnrNum}
                  onChange={(e) => setNewEnrNum(e.target.value)}
                  placeholder="e.g. 2022-CSE-045"
                  className="w-full rounded border border-slate-300 p-2"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">First Name</label>
                  <input
                    type="text"
                    value={newFirstName}
                    onChange={(e) => setNewFirstName(e.target.value)}
                    placeholder="e.g. Neha"
                    className="w-full rounded border border-slate-300 p-2"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Last Name</label>
                  <input
                    type="text"
                    value={newLastName}
                    onChange={(e) => setNewLastName(e.target.value)}
                    placeholder="e.g. Sharma"
                    className="w-full rounded border border-slate-300 p-2"
                  />
                </div>
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Institutional Email</label>
                <input
                  type="email"
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  placeholder="e.g. neha.sharma@ait.edu"
                  className="w-full rounded border border-slate-300 p-2"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Department</label>
                  <input
                    type="text"
                    value={newDept}
                    onChange={(e) => setNewDept(e.target.value)}
                    className="w-full rounded border border-slate-300 p-2"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Semester</label>
                  <input
                    type="number"
                    min={1}
                    max={10}
                    value={newSemester}
                    onChange={(e) => setNewSemester(parseInt(e.target.value) || 1)}
                    className="w-full rounded border border-slate-300 p-2"
                  />
                </div>
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Academic Program</label>
                <select
                  value={newProgramId}
                  onChange={(e) => setNewProgramId(e.target.value)}
                  className="w-full rounded border border-slate-300 p-2"
                >
                  <option value="">Auto-assign Default Program</option>
                  {programs.map((p) => (
                    <option key={p.id} value={p.id}>{p.code} — {p.name}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
              <button
                onClick={() => setShowCreateStudentModal(false)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={() => createStudentMutation.mutate()}
                disabled={!newEnrNum || !newFirstName || !newLastName || createStudentMutation.isPending}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold disabled:opacity-50"
              >
                {createStudentMutation.isPending ? 'Saving...' : 'Create Student'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Create Assessment */}
      {showCreateAsmtModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-xl space-y-4">
            <h3 className="text-base font-bold text-slate-900">Define Academic Assessment</h3>
            <div className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Subject</label>
                <select
                  value={asmtSubjectId}
                  onChange={(e) => setAsmtSubjectId(e.target.value)}
                  className="w-full rounded border border-slate-300 p-2"
                >
                  {subjects.map((s) => (
                    <option key={s.id} value={s.id}>{s.code} — {s.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Assessment Name</label>
                <input
                  type="text"
                  value={asmtName}
                  onChange={(e) => setAsmtName(e.target.value)}
                  placeholder="e.g. Internal Test 1"
                  className="w-full rounded border border-slate-300 p-2"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Assessment Type</label>
                  <select
                    value={asmtType}
                    onChange={(e) => setAsmtType(e.target.value as any)}
                    className="w-full rounded border border-slate-300 p-2"
                  >
                    <option value="INTERNAL_TEST">INTERNAL TEST</option>
                    <option value="MID_TERM">MID TERM</option>
                    <option value="END_TERM">END TERM</option>
                    <option value="ASSIGNMENT">ASSIGNMENT</option>
                    <option value="QUIZ">QUIZ</option>
                    <option value="PRACTICAL">PRACTICAL</option>
                    <option value="LAB">LAB</option>
                    <option value="PROJECT">PROJECT</option>
                  </select>
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Maximum Marks</label>
                  <input
                    type="number"
                    value={asmtMaxMarks}
                    onChange={(e) => setAsmtMaxMarks(Number(e.target.value))}
                    className="w-full rounded border border-slate-300 p-2"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Passing Marks</label>
                  <input
                    type="number"
                    value={asmtPassingMarks}
                    onChange={(e) => setAsmtPassingMarks(Number(e.target.value))}
                    className="w-full rounded border border-slate-300 p-2"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Academic Year</label>
                  <input
                    type="text"
                    value={asmtYear}
                    onChange={(e) => setAsmtYear(e.target.value)}
                    placeholder="2024-2025"
                    className="w-full rounded border border-slate-300 p-2"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Semester</label>
                  <input
                    type="number"
                    min={1}
                    max={10}
                    value={asmtSemester}
                    onChange={(e) => setAsmtSemester(parseInt(e.target.value) || 1)}
                    className="w-full rounded border border-slate-300 p-2"
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
              <button
                onClick={() => setShowCreateAsmtModal(false)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={() => createAsmtMutation.mutate()}
                disabled={!asmtName || createAsmtMutation.isPending}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold disabled:opacity-50"
              >
                {createAsmtMutation.isPending ? 'Saving...' : 'Create Assessment'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Audited Record Correction */}
      {correctionRecordId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-xl space-y-4">
            <h3 className="text-base font-bold text-slate-900">Audited Record Mark Correction</h3>
            <p className="text-xs text-slate-500">
              Modifying an existing academic performance entry creates an immutable audit trail entry recording the actor and reason.
            </p>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Corrected Marks</label>
                <input
                  type="number"
                  step="0.5"
                  value={correctionMarks}
                  onChange={(e) => setCorrectionMarks(Number(e.target.value))}
                  className="w-full rounded border border-slate-300 p-2"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Substantive Reason / Authority</label>
                <textarea
                  rows={3}
                  value={correctionReason}
                  onChange={(e) => setCorrectionReason(e.target.value)}
                  placeholder="e.g. Faculty re-evaluation authorized by departmental committee."
                  className="w-full rounded border border-slate-300 p-2"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
              <button
                onClick={() => setCorrectionRecordId(null)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={() =>
                  correctRecordMutation.mutate({
                    recordId: correctionRecordId,
                    marks: correctionMarks,
                    reason: correctionReason,
                  })
                }
                disabled={!correctionReason || correctionReason.length < 5 || correctRecordMutation.isPending}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold disabled:opacity-50"
              >
                {correctRecordMutation.isPending ? 'Saving...' : 'Apply Audited Correction'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// UI Micro-Components

function MetricCard({
  title,
  value,
  icon,
  note,
  highlight,
  warning,
}: {
  title: string;
  value: number;
  icon: string;
  note: string;
  highlight?: boolean;
  warning?: boolean;
}) {
  return (
    <div
      className={`p-4 rounded-xl border shadow-sm ${
        warning
          ? 'bg-amber-50/50 border-amber-200'
          : highlight
          ? 'bg-indigo-50/50 border-indigo-200'
          : 'bg-white border-slate-200'
      }`}
    >
      <div className="flex items-center justify-between text-slate-500 mb-1">
        <span className="text-xs font-bold uppercase tracking-wider">{title}</span>
        <span className="text-base">{icon}</span>
      </div>
      <div className="text-2xl font-black text-slate-900">{value}</div>
      <div className="text-[11px] text-slate-500 mt-0.5">{note}</div>
    </div>
  );
}

function AttendanceBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    PRESENT: 'bg-emerald-100 text-emerald-800',
    ABSENT: 'bg-rose-100 text-rose-800',
    LATE: 'bg-amber-100 text-amber-800',
    EXCUSED: 'bg-blue-100 text-blue-800',
    NOT_RECORDED: 'bg-slate-100 text-slate-600',
  };
  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${styles[status] || 'bg-slate-100 text-slate-700'}`}>
      {status}
    </span>
  );
}

function ResultBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    PASSED: 'bg-emerald-100 text-emerald-800',
    FAILED: 'bg-rose-100 text-rose-800',
    ABSENT: 'bg-purple-100 text-purple-800',
    NOT_SUBMITTED: 'bg-slate-200 text-slate-700',
    EXEMPTED: 'bg-sky-100 text-sky-800',
  };
  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${styles[status] || 'bg-slate-100 text-slate-700'}`}>
      {status}
    </span>
  );
}

function VerificationBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    VERIFIED: 'bg-emerald-100 text-emerald-800 font-bold',
    IMPORTED: 'bg-blue-50 text-blue-700',
    REVIEW_REQUIRED: 'bg-amber-100 text-amber-800 font-bold',
    REJECTED: 'bg-rose-100 text-rose-800 font-bold',
    CORRECTION_REQUIRED: 'bg-purple-100 text-purple-800 font-bold',
  };
  return (
    <span className={`px-2 py-0.5 rounded text-[10px] ${styles[status] || 'bg-slate-100 text-slate-700'}`}>
      {status.replace('_', ' ')}
    </span>
  );
}

function SeverityBadge({ severity }: { severity: DataQualitySeverity | string }) {
  const styles: Record<string, string> = {
    CRITICAL: 'bg-rose-600 text-white font-black',
    ERROR: 'bg-rose-100 text-rose-800 font-bold',
    WARNING: 'bg-amber-100 text-amber-800 font-bold',
    INFO: 'bg-blue-100 text-blue-800',
  };
  return (
    <span className={`px-1.5 py-0.5 rounded text-[10px] ${styles[severity] || 'bg-slate-100 text-slate-700'}`}>
      {severity}
    </span>
  );
}
