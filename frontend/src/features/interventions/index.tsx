import React from 'react';
import { ModuleSpecView } from '@/components/shared/module-spec-view';

export const InterventionPage: React.FC = () => {
  return (
    <ModuleSpecView
      id="06"
      name="Personalized Intervention & Student Growth"
      phase="Phase 07 / 11"
      tagline="Remedial Roadmaps, Mentorship & Longitudinal Recovery Tracking"
      description="Closes the loop on academic risk by prescribing personalized, actionable learning roadmaps, AI-generated remedial micro-tasks, mentor/faculty oversight, and post-intervention reassessment tracking."
      responsibilities={[
        'Synthesize individualized academic growth and support plans tailored to specific weak topics.',
        'Generate personalized remedial activities (targeted readings, practice problems, micro-labs).',
        'Enforce faculty or mentor approval before plans are dispatched to students.',
        'Facilitate student-mentor check-ins and structured remedial task submission.',
        'Track longitudinal post-remedial recovery through targeted reassessment probes.',
      ]}
      dataInputs={[
        'Module 05: Flagged Academic Risk Profiles & Explainable Drivers',
        'Module 04: Specific Topic Deficiencies & Conceptual Gaps',
        'Faculty Mentorship Assignments',
      ]}
      dataOutputs={[
        'Personalized Growth Roadmaps',
        'Remedial Task Submissions',
        'Post-Intervention Mastery Delta',
        'Risk De-escalation Audit Trail',
      ]}
      intelligenceType="Prescriptive Learning Pathways & Growth Monitoring"
      backendRoute="/api/v1/interventions"
    />
  );
};
