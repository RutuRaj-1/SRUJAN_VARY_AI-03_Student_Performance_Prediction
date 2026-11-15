import React from 'react';
import { ModuleSpecView } from '@/components/shared/module-spec-view';

export const CareerReadinessPage: React.FC = () => {
  return (
    <ModuleSpecView
      id="07"
      name="Industry & Placement Readiness Intelligence"
      phase="Phase 08 / 11"
      tagline="Role Competency Benchmarking, Practical Proof & Gap Radar"
      description="Evaluates student preparedness against actual industry job profiles (e.g. Backend Engineer, Data Analyst, Cloud DevOps). Verifies practical competencies through coding benchmarks, GitHub repository analysis, and project evidence."
      responsibilities={[
        'Curate standardized industry role competencies and prerequisite technical benchmarks.',
        'Facilitate student target role selection and career tracking objectives.',
        'Conduct practical hands-on assessments (system design, algorithmic code, database schemas).',
        'Analyze external verifiable engineering evidence (e.g. GitHub repos, commit patterns, project code).',
        'Produce multi-dimensional placement readiness radars with concrete bridge plans for identified skill gaps.',
      ]}
      dataInputs={[
        'Industry Role Competency Library (Target Roles: SDE, Data Engineer, Frontend, DevOps)',
        'Module 04: Calibrated Foundational Topic Mastery',
        'Verifiable GitHub Profiles & Engineering Repositories',
        'Practical Benchmark Attempts',
      ]}
      dataOutputs={[
        'Role-Wise Placement Readiness Index',
        'Competency Gap Radar Matrices',
        'GitHub Evidence Verification Badges',
        'Industry Bridge Learning Pathways',
      ]}
      intelligenceType="Output 3/3: Career Readiness Intelligence (Decoupled from Semester Marks)"
      backendRoute="/api/v1/career"
    />
  );
};
