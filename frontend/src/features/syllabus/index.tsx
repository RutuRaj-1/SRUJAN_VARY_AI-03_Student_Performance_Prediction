import React from 'react';
import { ModuleSpecView } from '@/components/shared/module-spec-view';

export const SyllabusPage: React.FC = () => {
  return (
    <ModuleSpecView
      id="02"
      name="AI Syllabus & Competency Intelligence"
      phase="Phase 03 / 11"
      tagline="Curriculum Extraction, Topic Hierarchy & Outcome Mapping"
      description="Transforms unstructured curriculum PDF documents into structured academic topic hierarchies, Bloom's taxonomy learning outcomes, prerequisite dependency graphs, and industry competency bridges."
      responsibilities={[
        'Process uploaded syllabus PDFs via PyMuPDF/pdfplumber.',
        'Extract units, topics, subtopics, and official learning outcomes with structured AI.',
        'Construct topic prerequisite dependency graphs across courses.',
        'Provide faculty review and approval workflows for verified curricula.',
        'Map institutional academic topics to standardized industry competency benchmarks.',
      ]}
      dataInputs={[
        'University Syllabus PDFs',
        'Course Accreditation Guidelines',
        'Industry Competency Benchmarks (O*NET / SFIA)',
      ]}
      dataOutputs={[
        'Course Topic Trees',
        'Unit Learning Outcomes (CLOs)',
        'Topic Dependency Graph',
        'Faculty-Approved Curriculum Schemas',
      ]}
      intelligenceType="Structured Curriculum AI & Dependency Graphs"
      backendRoute="/api/v1/syllabus"
    />
  );
};
