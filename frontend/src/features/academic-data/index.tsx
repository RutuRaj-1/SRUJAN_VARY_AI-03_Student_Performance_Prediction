import React from 'react';
import { ModuleSpecView } from '@/components/shared/module-spec-view';

export const AcademicDataPage: React.FC = () => {
  return (
    <ModuleSpecView
      id="01"
      name="Academic Data Intelligence Hub"
      phase="Phase 02 / 11"
      tagline="Institutional Records & Academic Evidence Provenance"
      description="The foundational ingestion and validation layer for institutional academic records. Ingests student profiles, attendance ledgers, internal semester marks, and assignment grades with complete source auditability."
      responsibilities={[
        'Maintain student academic identity and course enrollments.',
        'Track granular attendance records (lecture, lab, overall percentage).',
        'Ingest internal marks, class test results, and assignment submissions.',
        'Support CSV/Excel bulk academic import with schema verification and error isolation.',
        'Establish academic evidence timeline for continuous provenance tracking.',
      ]}
      dataInputs={[
        'Student Information Records',
        'Attendance Rosters',
        'Internal Exam Gradebooks',
        'Assignment Submission Metrics',
      ]}
      dataOutputs={[
        'Normalized Academic Profiles',
        'Validated Evidence Log',
        'Attendance Deficiency Flags',
        'Academic Timeline Data Points',
      ]}
      intelligenceType="Evidence Provenance & Academic Auditing"
      backendRoute="/api/v1/academic"
    />
  );
};
