import React from 'react';
import { ModuleSpecView } from '@/components/shared/module-spec-view';

export const AssessmentPage: React.FC = () => {
  return (
    <ModuleSpecView
      id="03"
      name="Continuous Learning & Assessment Engine"
      phase="Phase 04 / 11"
      tagline="Multi-Modal Knowledge Probing & Practical Verification"
      description="Executes continuous, unit-wise evaluations combining AI-assisted question generation, faculty approvals, multi-choice concepts, deep descriptive explanations, and executable practical coding and SQL evaluations."
      responsibilities={[
        'Manage curriculum-aligned question banks across difficulty levels and Bloom taxonomy tiers.',
        'Support AI-assisted question generation with mandatory faculty verification checkpoints.',
        'Deliver secure MCQ, descriptive answer, and practical coding/SQL test sessions.',
        'Track granular student attempt telemetry (time per item, submission revisions).',
        'Generate objective evaluation scores with rubrics and execution sandbox tests.',
      ]}
      dataInputs={[
        'Approved Syllabus Topics & Outcomes',
        'Faculty Question Submissions',
        'Student Assessment Attempt Payloads',
      ]}
      dataOutputs={[
        'Evaluated Assessment Attempts',
        'Item Discrimination Metrics',
        'Practical Code Execution Outputs',
        'Assessment Attempt Timestamps',
      ]}
      intelligenceType="Adaptive Assessment & Multi-Modal Evaluation"
      backendRoute="/api/v1/assessments"
    />
  );
};
