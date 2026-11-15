import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  syllabusService,
  CompetencyCategory,
  BloomTaxonomyLevel,
  IndustryMappingStatus,
} from '@/services/syllabus-service';
import { useAuth } from '@/context/auth-context';

export const SyllabusPage: React.FC = () => {
  const { profile } = useAuth();
  const queryClient = useQueryClient();

  // Active tab state
  const [activeTab, setActiveTab] = useState<'upload' | 'explorer' | 'competencies' | 'industry' | 'review'>('upload');

  // Selected subject & document state
  const [selectedSubjectId, setSelectedSubjectId] = useState<string>('');
  const [selectedDocId, setSelectedDocId] = useState<string>('');

  // Upload form state
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadSubjectName, setUploadSubjectName] = useState('Operating Systems');
  const [uploadSubjectCode, setUploadSubjectCode] = useState('CS401');
  const [uploadSemester, setUploadSemester] = useState(4);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);

  // Filter state for competencies
  const [competencyCategoryFilter, setCompetencyCategoryFilter] = useState<string>('ALL');

  // Review comment state
  const [reviewComment, setReviewComment] = useState('');
  const [editingUnitId, setEditingUnitId] = useState<string | null>(null);
  const [editUnitTitle, setEditUnitTitle] = useState('');
  const [editUnitHours, setEditUnitHours] = useState(9);

  // Queries
  const { data: subjects = [] } = useQuery({
    queryKey: ['syllabus', 'subjects'],
    queryFn: () => syllabusService.getSubjects(),
  });

  // Set default subject if available
  React.useEffect(() => {
    if (subjects.length > 0 && !selectedSubjectId) {
      setSelectedSubjectId(subjects[0].id);
    }
  }, [subjects, selectedSubjectId]);

  const { data: documents = [], isLoading: docsLoading } = useQuery({
    queryKey: ['syllabus', 'documents', selectedSubjectId],
    queryFn: () => syllabusService.getDocuments(selectedSubjectId || undefined),
  });

  React.useEffect(() => {
    if (documents.length > 0 && !selectedDocId) {
      setSelectedDocId(documents[0].id);
    }
  }, [documents, selectedDocId]);

  const { data: selectedDocDetail, isLoading: docDetailLoading } = useQuery({
    queryKey: ['syllabus', 'document-detail', selectedDocId],
    queryFn: () => syllabusService.getDocumentDetail(selectedDocId),
    enabled: !!selectedDocId,
  });

  const { data: competencies = [], isLoading: compLoading } = useQuery({
    queryKey: ['syllabus', 'competencies', selectedSubjectId],
    queryFn: () => syllabusService.getSubjectCompetencies(selectedSubjectId),
    enabled: !!selectedSubjectId,
  });

  const { data: gapSummaries = [], isLoading: gapLoading } = useQuery({
    queryKey: ['syllabus', 'gap-analysis', selectedSubjectId],
    queryFn: () => syllabusService.getSubjectGapAnalysis(selectedSubjectId),
    enabled: !!selectedSubjectId,
  });

  const { data: reviewHistory = [], isLoading: histLoading } = useQuery({
    queryKey: ['syllabus', 'history', selectedDocId],
    queryFn: () => syllabusService.getDocumentHistory(selectedDocId),
    enabled: !!selectedDocId,
  });

  // Mutations
  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (!uploadFile) throw new Error('Please select a syllabus document file.');
      let targetSubjectId = selectedSubjectId;

      // Create subject if no subjects exist yet
      if (!targetSubjectId) {
        const programs = await syllabusService.getPrograms();
        let progId = programs[0]?.id;
        if (!progId) {
          const newProg = await syllabusService.createProgram({
            name: 'B.Tech Computer Science & Engineering',
            code: 'BTECH-CSE',
            degree_type: 'Bachelor of Technology',
            duration_years: 4,
            institution_id: profile?.institution_id || undefined,
          });
          progId = newProg.id;
        }

        const newSubj = await syllabusService.createSubject({
          name: uploadSubjectName,
          code: uploadSubjectCode,
          semester: uploadSemester,
          academic_year: '2024-2025',
          regulation_version: 'R22',
          institution_id: profile?.institution_id || undefined,
          program_id: progId,
        });
        targetSubjectId = newSubj.id;
        setSelectedSubjectId(targetSubjectId);
      }

      return syllabusService.uploadDocument(uploadFile, targetSubjectId, profile?.institution_id || undefined);
    },
    onSuccess: (newDoc) => {
      setUploadSuccess(`Uploaded '${newDoc.file_name}' successfully.`);
      setUploadError(null);
      setUploadFile(null);
      setSelectedDocId(newDoc.id);
      queryClient.invalidateQueries({ queryKey: ['syllabus'] });
    },
    onError: (err: unknown) => {
      const msg = err instanceof Error ? err.message : 'Upload failed.';
      setUploadError(msg);
      setUploadSuccess(null);
    },
  });

  const processMutation = useMutation({
    mutationFn: (docId: string) => syllabusService.processDocument(docId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['syllabus'] });
      setActiveTab('explorer');
    },
  });

  const reviewMutation = useMutation({
    mutationFn: ({ docId, action, comment }: { docId: string; action: string; comment: string }) =>
      syllabusService.reviewDocument(docId, action, comment),
    onSuccess: () => {
      setReviewComment('');
      queryClient.invalidateQueries({ queryKey: ['syllabus'] });
    },
  });

  const updateUnitMutation = useMutation({
    mutationFn: ({ unitId, title, hours }: { unitId: string; title: string; hours: number }) =>
      syllabusService.updateUnit(unitId, { title, estimated_hours: hours }),
    onSuccess: () => {
      setEditingUnitId(null);
      queryClient.invalidateQueries({ queryKey: ['syllabus'] });
    },
  });

  const activeSubject = subjects.find((s) => s.id === selectedSubjectId);

  const filteredCompetencies = competencies.filter((c) => {
    if (competencyCategoryFilter === 'ALL') return true;
    return c.category === competencyCategoryFilter;
  });

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="border-b border-slate-200 pb-5">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <span className="inline-flex items-center rounded-md bg-indigo-50 px-2.5 py-1 text-xs font-semibold text-indigo-700 ring-1 ring-inset ring-indigo-700/10">
                Module 02
              </span>
              <span className="inline-flex items-center rounded-md bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700">
                Phase 03 / 11
              </span>
              <span className="text-xs text-slate-500 font-mono">
                {profile?.institution_id ? `Institution ID: ${profile.institution_id.slice(0, 8)}...` : 'System Mode'}
              </span>
            </div>
            <h1 className="mt-2 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
              AI Syllabus & Competency Intelligence Engine
            </h1>
            <p className="mt-1 text-sm text-slate-600">
              Transform unstructured university curriculum documents into verified competency hierarchies, Bloom's learning outcomes, and explainable industry alignment frameworks.
            </p>
          </div>

          {/* Subject Switcher dropdown */}
          {subjects.length > 0 && (
            <div className="flex items-center gap-2 bg-white p-2 rounded-lg border border-slate-200 shadow-sm">
              <label htmlFor="subject-select" className="text-xs font-semibold text-slate-600 uppercase">Subject:</label>
              <select
                id="subject-select"
                value={selectedSubjectId}
                onChange={(e) => {
                  setSelectedSubjectId(e.target.value);
                  setSelectedDocId('');
                }}
                className="text-sm font-medium text-slate-900 border-none bg-transparent focus:ring-0 cursor-pointer"
              >
                {subjects.map((subj) => (
                  <option key={subj.id} value={subj.id}>
                    {subj.code} — {subj.name}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Navigation Tabs */}
        <div className="mt-6 flex border-b border-slate-200 gap-6 text-sm font-medium">
          <button
            onClick={() => setActiveTab('upload')}
            className={`pb-3 border-b-2 transition-colors ${
              activeTab === 'upload'
                ? 'border-indigo-600 text-indigo-600 font-semibold'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            1. Document Upload & Ingestion
          </button>
          <button
            onClick={() => setActiveTab('explorer')}
            className={`pb-3 border-b-2 transition-colors ${
              activeTab === 'explorer'
                ? 'border-indigo-600 text-indigo-600 font-semibold'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            2. Hierarchical Syllabus Explorer ({selectedDocDetail?.units?.length || 0} Units)
          </button>
          <button
            onClick={() => setActiveTab('competencies')}
            className={`pb-3 border-b-2 transition-colors ${
              activeTab === 'competencies'
                ? 'border-indigo-600 text-indigo-600 font-semibold'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            3. Competency Taxonomy ({competencies.length})
          </button>
          <button
            onClick={() => setActiveTab('industry')}
            className={`pb-3 border-b-2 transition-colors ${
              activeTab === 'industry'
                ? 'border-indigo-600 text-indigo-600 font-semibold'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            4. Industry Alignment & Gap Matrix ({gapSummaries.length} Roles)
          </button>
          <button
            onClick={() => setActiveTab('review')}
            className={`pb-3 border-b-2 transition-colors ${
              activeTab === 'review'
                ? 'border-indigo-600 text-indigo-600 font-semibold'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            5. Faculty Review & Audit History ({reviewHistory.length})
          </button>
        </div>
      </div>

      {/* TAB 1: Document Upload & Ingestion */}
      {activeTab === 'upload' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Upload Box */}
            <div className="md:col-span-2 bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
              <h2 className="text-lg font-bold text-slate-900 mb-2">Upload Syllabus Document</h2>
              <p className="text-xs text-slate-500 mb-4">
                Supported formats: PDF, DOCX, TXT. Documents are saved securely in institutional storage before extraction.
              </p>

              {uploadError && (
                <div className="mb-4 rounded-lg bg-red-50 p-3 text-xs text-red-700 border border-red-200">
                  {uploadError}
                </div>
              )}
              {uploadSuccess && (
                <div className="mb-4 rounded-lg bg-emerald-50 p-3 text-xs text-emerald-700 border border-emerald-200">
                  {uploadSuccess}
                </div>
              )}

              <div className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Subject Name</label>
                    <input
                      type="text"
                      value={uploadSubjectName}
                      onChange={(e) => setUploadSubjectName(e.target.value)}
                      placeholder="e.g. Operating Systems"
                      className="w-full text-xs rounded-md border border-slate-300 p-2 focus:ring-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Subject Code</label>
                    <input
                      type="text"
                      value={uploadSubjectCode}
                      onChange={(e) => setUploadSubjectCode(e.target.value)}
                      placeholder="e.g. CS401"
                      className="w-full text-xs rounded-md border border-slate-300 p-2 focus:ring-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Semester</label>
                    <input
                      type="number"
                      min={1}
                      max={10}
                      value={uploadSemester}
                      onChange={(e) => setUploadSemester(parseInt(e.target.value) || 1)}
                      className="w-full text-xs rounded-md border border-slate-300 p-2 focus:ring-indigo-500"
                    />
                  </div>
                </div>

                <div className="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center hover:border-indigo-400 transition-colors">
                  <input
                    type="file"
                    id="syllabus-file"
                    accept=".pdf,.docx,.txt"
                    onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                    className="hidden"
                  />
                  <label htmlFor="syllabus-file" className="cursor-pointer flex flex-col items-center">
                    <svg className="w-10 h-10 text-slate-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <span className="text-sm font-semibold text-indigo-600 hover:text-indigo-500">
                      Click to choose syllabus file
                    </span>
                    <span className="text-xs text-slate-500 mt-1">or drag and drop (Max 25MB)</span>
                    {uploadFile && (
                      <span className="mt-3 inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                        📄 {uploadFile.name} ({(uploadFile.size / 1024).toFixed(1)} KB)
                      </span>
                    )}
                  </label>
                </div>

                <div className="flex justify-end">
                  <button
                    disabled={!uploadFile || uploadMutation.isPending}
                    onClick={() => uploadMutation.mutate()}
                    className="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-5 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50"
                  >
                    {uploadMutation.isPending ? 'Uploading...' : 'Upload Document'}
                  </button>
                </div>
              </div>
            </div>

            {/* Ingestion Info Panel */}
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-6">
              <h3 className="text-sm font-bold text-slate-900 mb-3">AI Processing Pipeline</h3>
              <ol className="space-y-3 text-xs text-slate-600">
                <li className="flex items-start gap-2">
                  <span className="flex-shrink-0 w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-[10px]">1</span>
                  <span><strong>Extraction:</strong> Clean layout parsing via PyMuPDF/text extraction.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="flex-shrink-0 w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-[10px]">2</span>
                  <span><strong>AI Structuring:</strong> Modular units, estimated hours, topics, and Bloom's CLOs.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="flex-shrink-0 w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-[10px]">3</span>
                  <span><strong>Competency Taxonomy:</strong> 5-category classification with depth (1-5) and evidence quotes.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="flex-shrink-0 w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-[10px]">4</span>
                  <span><strong>Industry Bridge:</strong> Matching against reference SDE, Data, AI, and DevOps profiles.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="flex-shrink-0 w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-[10px]">5</span>
                  <span><strong>Faculty Verification:</strong> Review, inline modifications, and signed approval.</span>
                </li>
              </ol>
            </div>
          </div>

          {/* Uploaded Documents List */}
          <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
            <div className="p-4 border-b border-slate-200 flex justify-between items-center">
              <h3 className="text-sm font-bold text-slate-900">
                Uploaded Documents for {activeSubject?.name || 'All Subjects'}
              </h3>
              <span className="text-xs text-slate-500">{documents.length} Document(s)</span>
            </div>
            {docsLoading ? (
              <div className="p-8 text-center text-xs text-slate-500">Loading documents...</div>
            ) : documents.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-500">No syllabus documents uploaded yet.</div>
            ) : (
              <div className="divide-y divide-slate-100">
                {documents.map((doc) => (
                  <div key={doc.id} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-xs text-slate-900">{doc.file_name}</span>
                        <StatusBadge status={doc.status} />
                      </div>
                      <div className="mt-1 flex items-center gap-4 text-[11px] text-slate-500">
                        <span>Size: {(doc.file_size_bytes / 1024).toFixed(1)} KB</span>
                        <span>Uploaded: {new Date(doc.created_at).toLocaleDateString()}</span>
                        {doc.extraction_metadata && (
                          <span>Pages: {String(doc.extraction_metadata['page_count'] || 1)}</span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {doc.status === 'UPLOADED' || doc.status === 'FAILED' ? (
                        <button
                          disabled={processMutation.isPending}
                          onClick={() => processMutation.mutate(doc.id)}
                          className="px-3 py-1.5 text-xs font-semibold rounded-md bg-indigo-600 text-white hover:bg-indigo-500 disabled:opacity-50"
                        >
                          {processMutation.isPending ? 'Processing...' : 'Run Extraction & AI Structuring'}
                        </button>
                      ) : (
                        <button
                          onClick={() => {
                            setSelectedDocId(doc.id);
                            setActiveTab('explorer');
                          }}
                          className="px-3 py-1.5 text-xs font-semibold rounded-md bg-slate-100 text-slate-700 hover:bg-slate-200"
                        >
                          View Extracted Structure →
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: Hierarchical Syllabus Explorer */}
      {activeTab === 'explorer' && (
        <div className="space-y-6">
          {docDetailLoading ? (
            <div className="p-12 text-center text-xs text-slate-500 bg-white border border-slate-200 rounded-xl">
              Loading structured curriculum hierarchy...
            </div>
          ) : !selectedDocDetail || !selectedDocDetail.units || selectedDocDetail.units.length === 0 ? (
            <div className="p-12 text-center text-xs text-slate-500 bg-white border border-slate-200 rounded-xl">
              <p className="font-semibold text-slate-700 mb-1">No extracted units available for this document.</p>
              <p>Run document extraction in the Upload tab first.</p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex justify-between items-center bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <div>
                  <h2 className="text-base font-bold text-slate-900">
                    {activeSubject?.name || 'Syllabus Hierarchy'} ({selectedDocDetail.units.length} Units)
                  </h2>
                  <p className="text-xs text-slate-500">
                    Document Status: <StatusBadge status={selectedDocDetail.status} />
                  </p>
                </div>
                <div className="text-right text-xs text-slate-500">
                  Total Curriculum Hours: {selectedDocDetail.units.reduce((acc, u) => acc + u.estimated_hours, 0)} Hrs
                </div>
              </div>

              {/* Units Accordion Tree */}
              <div className="space-y-4">
                {selectedDocDetail.units.map((unit) => (
                  <div key={unit.id} className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
                    <div className="bg-slate-50 p-4 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-indigo-100 text-indigo-800">
                            Unit {unit.unit_number}
                          </span>
                          <h3 className="text-sm font-bold text-slate-900">{unit.title}</h3>
                        </div>
                        {unit.description && (
                          <p className="text-xs text-slate-600 mt-1">{unit.description}</p>
                        )}
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-xs font-semibold text-slate-600 bg-white px-2.5 py-1 rounded border border-slate-200">
                          ⏱️ {unit.estimated_hours} Hours
                        </span>
                        <button
                          onClick={() => {
                            setEditingUnitId(unit.id);
                            setEditUnitTitle(unit.title);
                            setEditUnitHours(unit.estimated_hours);
                          }}
                          className="text-xs text-indigo-600 hover:text-indigo-800 font-medium"
                        >
                          Edit Unit
                        </button>
                      </div>
                    </div>

                    {/* Inline Unit Edit Modal/Form */}
                    {editingUnitId === unit.id && (
                      <div className="p-4 bg-indigo-50/50 border-b border-indigo-100 flex flex-col sm:flex-row gap-3 items-end">
                        <div className="flex-1">
                          <label className="block text-[11px] font-bold text-slate-700 mb-1">Unit Title</label>
                          <input
                            type="text"
                            value={editUnitTitle}
                            onChange={(e) => setEditUnitTitle(e.target.value)}
                            className="w-full text-xs rounded border border-slate-300 p-1.5 bg-white"
                          />
                        </div>
                        <div className="w-24">
                          <label className="block text-[11px] font-bold text-slate-700 mb-1">Hours</label>
                          <input
                            type="number"
                            value={editUnitHours}
                            onChange={(e) => setEditUnitHours(parseInt(e.target.value) || 1)}
                            className="w-full text-xs rounded border border-slate-300 p-1.5 bg-white"
                          />
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={() =>
                              updateUnitMutation.mutate({
                                unitId: unit.id,
                                title: editUnitTitle,
                                hours: editUnitHours,
                              })
                            }
                            className="px-3 py-1.5 bg-indigo-600 text-white rounded text-xs font-semibold hover:bg-indigo-500"
                          >
                            Save
                          </button>
                          <button
                            onClick={() => setEditingUnitId(null)}
                            className="px-3 py-1.5 bg-slate-200 text-slate-700 rounded text-xs hover:bg-slate-300"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Topics Tree */}
                    <div className="p-4 space-y-3">
                      <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                        Topics & Subtopics ({unit.topics.length})
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {unit.topics.map((topic, idx) => (
                          <div key={topic.id} className="p-3 rounded-lg border border-slate-100 bg-slate-50/60">
                            <div className="flex items-start gap-2">
                              <span className="text-[10px] font-mono text-slate-400 mt-0.5">#{idx + 1}</span>
                              <div className="flex-1">
                                <span className="text-xs font-semibold text-slate-900">{topic.topic_name}</span>
                                {topic.subtopics && topic.subtopics.length > 0 && (
                                  <div className="mt-2 flex flex-wrap gap-1">
                                    {topic.subtopics.map((sub, sIdx) => (
                                      <span
                                        key={sIdx}
                                        className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] bg-white border border-slate-200 text-slate-600"
                                      >
                                        • {sub}
                                      </span>
                                    ))}
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>

                      {/* Learning Outcomes */}
                      {unit.learning_outcomes && unit.learning_outcomes.length > 0 && (
                        <div className="mt-4 pt-3 border-t border-slate-100">
                          <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                            Associated Learning Outcomes
                          </h4>
                          <div className="space-y-1.5">
                            {unit.learning_outcomes.map((lo) => (
                              <div key={lo.id} className="flex items-center gap-2 text-xs">
                                <span className="font-mono font-bold text-indigo-700 text-[11px]">{lo.outcome_code}:</span>
                                <span className="text-slate-700">{lo.description}</span>
                                <BloomBadge level={lo.bloom_level} />
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: Competency Taxonomy */}
      {activeTab === 'competencies' && (
        <div className="space-y-6">
          {/* Category Filter Pills */}
          <div className="flex flex-wrap gap-2">
            {['ALL', 'THEORETICAL', 'PROGRAMMING', 'TOOLS_TECHNOLOGIES', 'ANALYTICAL', 'PRACTICAL'].map((cat) => (
              <button
                key={cat}
                onClick={() => setCompetencyCategoryFilter(cat)}
                className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
                  competencyCategoryFilter === cat
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                {cat.replace('_', ' ')}
              </button>
            ))}
          </div>

          {compLoading ? (
            <div className="p-12 text-center text-xs text-slate-500 bg-white border border-slate-200 rounded-xl">
              Loading extracted competencies...
            </div>
          ) : filteredCompetencies.length === 0 ? (
            <div className="p-12 text-center text-xs text-slate-500 bg-white border border-slate-200 rounded-xl">
              No competencies found for category '{competencyCategoryFilter}'.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredCompetencies.map((comp) => (
                <div key={comp.id} className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <CategoryBadge category={comp.category} />
                      <span className="text-[10px] font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                        Depth: {comp.depth_level} / 5
                      </span>
                    </div>

                    <h3 className="text-sm font-bold text-slate-900 mb-1">{comp.title}</h3>
                    <p className="text-xs text-slate-600 line-clamp-3 mb-3">{comp.description}</p>
                  </div>

                  <div>
                    {comp.syllabus_evidence && (
                      <div className="p-2.5 rounded bg-slate-50 border border-slate-100 text-[11px] text-slate-600 italic mb-3">
                        <span className="font-semibold text-slate-700 not-italic">Evidence: </span>
                        {comp.syllabus_evidence}
                      </div>
                    )}

                    <div className="flex items-center justify-between text-xs pt-2 border-t border-slate-100">
                      <BloomBadge level={comp.bloom_level} />
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                          comp.is_verified ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                        }`}
                      >
                        {comp.is_verified ? '✓ VERIFIED' : 'PENDING APPROVAL'}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 4: Industry Alignment & Gap Matrix */}
      {activeTab === 'industry' && (
        <div className="space-y-6">
          {gapLoading ? (
            <div className="p-12 text-center text-xs text-slate-500 bg-white border border-slate-200 rounded-xl">
              Computing industry role gap analyses...
            </div>
          ) : gapSummaries.length === 0 ? (
            <div className="p-12 text-center text-xs text-slate-500 bg-white border border-slate-200 rounded-xl">
              No gap analyses computed. Please process a syllabus document first.
            </div>
          ) : (
            <div className="space-y-6">
              {gapSummaries.map((summary) => (
                <div key={summary.role_id} className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
                  <div className="p-5 border-b border-slate-200 bg-slate-50 flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                      <h3 className="text-base font-bold text-slate-900">{summary.role_title}</h3>
                      <p className="text-xs text-slate-500">
                        Evaluated across {summary.total_industry_requirements} core industry requirements
                      </p>
                    </div>

                    <div className="flex items-center gap-6">
                      <div className="text-right">
                        <span className="text-xl font-extrabold text-indigo-600">{summary.coverage_percentage}%</span>
                        <span className="block text-[10px] uppercase font-bold text-slate-400">Curriculum Coverage</span>
                      </div>
                      <div className="flex gap-2 text-xs">
                        <span className="px-2 py-1 rounded bg-emerald-100 text-emerald-800 font-bold">
                          {summary.direct_match_count} Direct
                        </span>
                        <span className="px-2 py-1 rounded bg-amber-100 text-amber-800 font-bold">
                          {summary.partial_match_count} Partial
                        </span>
                        <span className="px-2 py-1 rounded bg-rose-100 text-rose-800 font-bold">
                          {summary.missing_count} Gaps
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Gaps Breakdown Table */}
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-slate-200 text-xs">
                      <thead className="bg-slate-100/70 text-slate-700 font-semibold">
                        <tr>
                          <th className="px-4 py-3 text-left">Industry Requirement</th>
                          <th className="px-4 py-3 text-left">Alignment Status</th>
                          <th className="px-4 py-3 text-left">Academic Competency Match</th>
                          <th className="px-4 py-3 text-left">Explainable Rationale</th>
                          <th className="px-4 py-3 text-left">Curriculum Recommendation</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {summary.gaps.map((gap) => (
                          <tr key={gap.id} className="hover:bg-slate-50">
                            <td className="px-4 py-3 font-semibold text-slate-900 whitespace-nowrap">
                              {gap.industry_competency_name}
                              <span className="block text-[10px] text-slate-400 font-normal">
                                Depth {gap.required_depth} • {gap.importance}
                              </span>
                            </td>
                            <td className="px-4 py-3 whitespace-nowrap">
                              <MappingBadge status={gap.status} />
                            </td>
                            <td className="px-4 py-3 text-slate-700">
                              {gap.academic_competency_name || <span className="text-slate-400 italic">None</span>}
                            </td>
                            <td className="px-4 py-3 text-slate-600 max-w-xs">{gap.rationale}</td>
                            <td className="px-4 py-3 text-slate-600 max-w-xs">
                              {gap.recommendation || <span className="text-slate-400">—</span>}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 5: Faculty Review & Audit History */}
      {activeTab === 'review' && (
        <div className="space-y-6">
          {/* Action Approval Box */}
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <h2 className="text-base font-bold text-slate-900 mb-2">Faculty Curriculum Verification</h2>
            <p className="text-xs text-slate-500 mb-4">
              Review extracted units, outcomes, and competencies. Approving this document verifies the underlying competencies and enables downstream student assessment calibration and academic risk prediction.
            </p>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Faculty Comments / Approval Notes
                </label>
                <textarea
                  rows={3}
                  value={reviewComment}
                  onChange={(e) => setReviewComment(e.target.value)}
                  placeholder="e.g. Verified unit hours and aligned process scheduling outcomes against ABET criteria."
                  className="w-full text-xs rounded-md border border-slate-300 p-2.5 focus:ring-indigo-500"
                />
              </div>

              <div className="flex gap-3">
                <button
                  disabled={reviewMutation.isPending || !selectedDocId}
                  onClick={() =>
                    reviewMutation.mutate({
                      docId: selectedDocId,
                      action: 'APPROVED',
                      comment: reviewComment || 'Faculty approved curriculum structure',
                    })
                  }
                  className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-xs font-bold hover:bg-emerald-500 disabled:opacity-50"
                >
                  ✓ Approve Curriculum
                </button>
                <button
                  disabled={reviewMutation.isPending || !selectedDocId}
                  onClick={() =>
                    reviewMutation.mutate({
                      docId: selectedDocId,
                      action: 'REJECTED',
                      comment: reviewComment || 'Faculty requested curriculum revision',
                    })
                  }
                  className="px-4 py-2 bg-rose-600 text-white rounded-lg text-xs font-bold hover:bg-rose-500 disabled:opacity-50"
                >
                  ✕ Reject / Request Re-Extraction
                </button>
              </div>
            </div>
          </div>

          {/* Audit History Log */}
          <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
            <div className="p-4 border-b border-slate-200 flex justify-between items-center">
              <h3 className="text-sm font-bold text-slate-900">Curriculum Modification Audit History</h3>
              <span className="text-xs text-slate-500">{reviewHistory.length} Audit Entry(ies)</span>
            </div>

            {histLoading ? (
              <div className="p-8 text-center text-xs text-slate-500">Loading audit history...</div>
            ) : reviewHistory.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-500">No modification records found for this document.</div>
            ) : (
              <div className="divide-y divide-slate-100">
                {reviewHistory.map((hist) => (
                  <div key={hist.id} className="p-4 flex flex-col sm:flex-row sm:items-start justify-between gap-3 text-xs">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-900">{hist.action}</span>
                        <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-[10px]">
                          {hist.entity_type}
                        </span>
                        <span className="text-slate-500 text-[11px]">by {hist.reviewer_name || 'System'}</span>
                      </div>
                      {hist.comments && (
                        <p className="mt-1 text-slate-600 italic font-sans text-xs">"{hist.comments}"</p>
                      )}
                      {hist.previous_value && hist.new_value && (
                        <div className="mt-2 text-[10px] font-mono bg-slate-50 p-2 rounded border border-slate-100 text-slate-600">
                          <div>Before: {JSON.stringify(hist.previous_value)}</div>
                          <div className="text-indigo-600">After: {JSON.stringify(hist.new_value)}</div>
                        </div>
                      )}
                    </div>
                    <span className="text-[11px] text-slate-400 whitespace-nowrap">
                      {new Date(hist.created_at).toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// UI Micro-Components

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    UPLOADED: 'bg-slate-100 text-slate-700',
    PROCESSING: 'bg-indigo-100 text-indigo-700 animate-pulse',
    EXTRACTED: 'bg-blue-100 text-blue-700',
    REVIEW_REQUIRED: 'bg-amber-100 text-amber-800',
    APPROVED: 'bg-emerald-100 text-emerald-800',
    REJECTED: 'bg-rose-100 text-rose-800',
    FAILED: 'bg-red-100 text-red-800',
  };
  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${styles[status] || 'bg-slate-100 text-slate-700'}`}>
      {status}
    </span>
  );
}

function BloomBadge({ level }: { level: BloomTaxonomyLevel | string }) {
  const styles: Record<string, string> = {
    REMEMBER: 'bg-sky-50 text-sky-700 border-sky-200',
    UNDERSTAND: 'bg-blue-50 text-blue-700 border-blue-200',
    APPLY: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    ANALYZE: 'bg-purple-50 text-purple-700 border-purple-200',
    EVALUATE: 'bg-amber-50 text-amber-700 border-amber-200',
    CREATE: 'bg-rose-50 text-rose-700 border-rose-200',
  };
  return (
    <span className={`px-1.5 py-0.5 rounded border text-[10px] font-bold ${styles[level] || 'bg-slate-50 text-slate-700'}`}>
      Bloom: {level}
    </span>
  );
}

function CategoryBadge({ category }: { category: CompetencyCategory | string }) {
  const styles: Record<string, string> = {
    THEORETICAL: 'bg-blue-100 text-blue-800',
    PROGRAMMING: 'bg-emerald-100 text-emerald-800',
    TOOLS_TECHNOLOGIES: 'bg-indigo-100 text-indigo-800',
    ANALYTICAL: 'bg-purple-100 text-purple-800',
    PRACTICAL: 'bg-orange-100 text-orange-800',
  };
  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${styles[category] || 'bg-slate-100 text-slate-800'}`}>
      {category.replace('_', ' ')}
    </span>
  );
}

function MappingBadge({ status }: { status: IndustryMappingStatus | string }) {
  const styles: Record<string, string> = {
    DIRECT: 'bg-emerald-100 text-emerald-800 font-bold',
    PARTIAL: 'bg-amber-100 text-amber-800 font-bold',
    MISSING: 'bg-rose-100 text-rose-800 font-bold',
    OUTDATED: 'bg-slate-200 text-slate-800 font-bold',
  };
  return (
    <span className={`px-2 py-0.5 rounded text-[10px] ${styles[status] || 'bg-slate-100 text-slate-700'}`}>
      {status}
    </span>
  );
}
