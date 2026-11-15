import React from 'react';
import { ModuleSpecView } from '@/components/shared/module-spec-view';

export const MasteryPage: React.FC = () => {
  return (
    <ModuleSpecView
      id="04"
      name="Evidence Calibration & Student Mastery Analytics"
      phase="Phase 05 / 11"
      tagline="Demonstrated Topic Mastery, Heatmaps & Evidence Triangulation"
      description="Calibrates student understanding by synthesizing formal internal marks with independent assessment demonstrations. Computes topic-level mastery scores, detects evidence discrepancies, and maintains evidence provenance."
      responsibilities={[
        'Calculate demonstrated topic mastery percentages decoupled from institutional marks.',
        'Track evidence provenance and confidence weights across evaluation sources.',
        'Detect evidence mismatches (e.g. high internal mark but failing independent coding/conceptual probe).',
        'Render student and cohort topic mastery heatmaps against unit outcomes.',
        'Calculate curriculum assessment coverage and empirical confidence indices.',
      ]}
      dataInputs={[
        'Module 01: Academic Records & Internal Marks',
        'Module 03: Independent Assessment Attempts',
        'Module 02: Topic Dependency Structures',
      ]}
      dataOutputs={[
        'Topic-Level Mastery Percentages',
        'Evidence Calibration Matrices',
        'Discrepancy Alerts (Grade Inflation / Hidden Gaps)',
        'Mastery Heatmaps & Coverage Graphs',
      ]}
      intelligenceType="Output 2/3: Learning Mastery Analytics (Decoupled from Risk & Placement)"
      backendRoute="/api/v1/mastery"
    />
  );
};
