import React from 'react';
import { ModuleSpecView } from '@/components/shared/module-spec-view';

export const AcademicRiskPage: React.FC = () => {
  return (
    <ModuleSpecView
      id="05"
      name="Explainable Academic Risk Prediction"
      phase="Phase 06 / 11"
      tagline="Early Warning Screening, Feature Engineering & Faculty Review"
      description="Screens students for academic difficulty early in the semester. Employs classical ML classifiers trained strictly on verified historical academic outcomes, paired with transparent feature attributions and faculty validation."
      responsibilities={[
        'Perform multi-factor risk screening combining attendance momentum, test drop-offs, and assessment lag.',
        'Extract standardized feature engineering pipelines across historical semesters.',
        'Deploy classical ML models (Logistic Regression / Random Forest) trained solely on validated institutional data.',
        'Generate explainable risk alerts detailing top contributory risk drivers for each flagged student.',
        'Enforce faculty review checkpoints to prevent automated stigmatization or unverified interventions.',
      ]}
      dataInputs={[
        'Module 01: Attendance Patterns & Internal Scores',
        'Module 04: Calibrated Mastery Scores & Assessment Lag',
        'Historical Cohort Outcome Records (Training Data)',
      ]}
      dataOutputs={[
        'Academic Risk Probability (Low / Moderate / Critical)',
        'Explainable Factor Attributions (e.g. 62% attendance drop in Unit 2)',
        'Faculty Risk Review Queue',
        'Proactive Intervention Triggers',
      ]}
      intelligenceType="Output 1/3: Academic Risk Intelligence (Isolated from Career Readiness)"
      backendRoute="/api/v1/risk"
    />
  );
};
