import React, { createContext, useContext, useState } from 'react';
import { UserRole } from '@/types/auth';
import {
  DemoScenarioId,
  DemoScenarioMeta,
  DemoStudent,
  DemoFaculty,
  DemoSubject,
  DemoSyllabusTopic,
  DemoCLO,
  DemoAssessment,
  DemoAssessmentAttempt,
  DemoTopicMastery,
  DemoStudentRiskProfile,
  DemoInterventionPlan,
  DemoCareerRoleProfile,
  DemoStudentCareerAlignment,
  DemoDashboardOverview,
} from './demo-types';
import {
  DEMO_SCENARIOS,
  DEMO_INSTITUTION,
  DEMO_FACULTY,
  DEMO_STUDENTS,
  DEMO_SUBJECTS,
  DEMO_CLOS,
  DEMO_TOPICS,
  DEMO_ASSESSMENTS,
  DEMO_SCENARIO_ATTEMPTS,
  DEMO_SCENARIO_MASTERY,
  DEMO_SCENARIO_RISK,
  DEMO_SCENARIO_INTERVENTIONS,
  DEMO_CAREER_ROLES,
  DEMO_SCENARIO_CAREER,
  DEMO_DASHBOARD_DATA,
} from './demo-data';

interface DemoContextType {
  isDemoMode: boolean;
  setIsDemoMode: (val: boolean) => void;
  activeScenario: DemoScenarioId;
  setActiveScenario: (scenario: DemoScenarioId) => void;
  activeRole: UserRole;
  setActiveRole: (role: UserRole) => void;
  scenarioMeta: DemoScenarioMeta;

  // Selected student & scenario data
  currentStudent: DemoStudent;
  currentAttempts: DemoAssessmentAttempt[];
  currentMastery: DemoTopicMastery[];
  currentRisk: DemoStudentRiskProfile;
  currentInterventions: DemoInterventionPlan[];
  currentCareer: DemoStudentCareerAlignment;

  // Global collections
  institution: typeof DEMO_INSTITUTION;
  students: DemoStudent[];
  faculty: DemoFaculty[];
  subjects: DemoSubject[];
  clos: DemoCLO[];
  topics: DemoSyllabusTopic[];
  assessments: DemoAssessment[];
  careerRoles: DemoCareerRoleProfile[];
  dashboardData: DemoDashboardOverview;

  // Mutators for interactive local demonstration
  approveInterventionPlan: (planId: string) => void;
  completeActionItem: (planId: string, itemIndex: number) => void;
  submitAssessmentAttempt: (assessmentId: string, marks: number) => void;
}

const DemoContext = createContext<DemoContextType | undefined>(undefined);

export const DemoProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Always default to demo mode true for rich presentation unless explicitly toggled
  const [isDemoMode, setIsDemoMode] = useState<boolean>(() => {
    const saved = localStorage.getItem('mastery_demo_mode');
    return saved !== null ? saved === 'true' : true;
  });

  const [activeScenario, setActiveScenarioState] = useState<DemoScenarioId>(() => {
    const saved = localStorage.getItem('mastery_demo_scenario');
    return (saved as DemoScenarioId) || 'A';
  });

  const [activeRole, setActiveRoleState] = useState<UserRole>(() => {
    const saved = localStorage.getItem('mastery_demo_role');
    return (saved as UserRole) || 'FACULTY';
  });

  // Local state for interactive actions in demo mode
  const [interventionsState, setInterventionsState] = useState(DEMO_SCENARIO_INTERVENTIONS);
  const [attemptsState, setAttemptsState] = useState(DEMO_SCENARIO_ATTEMPTS);

  const setActiveScenario = (scenario: DemoScenarioId) => {
    setActiveScenarioState(scenario);
    localStorage.setItem('mastery_demo_scenario', scenario);
  };

  const setActiveRole = (role: UserRole) => {
    setActiveRoleState(role);
    localStorage.setItem('mastery_demo_role', role);
  };

  const handleSetDemoMode = (val: boolean) => {
    setIsDemoMode(val);
    localStorage.setItem('mastery_demo_mode', String(val));
  };

  // Derive current student based on scenario
  const scenarioStudentIdMap: Record<DemoScenarioId, string> = {
    A: 'stu-004',
    B: 'stu-011',
    C: 'stu-019',
    D: 'stu-024',
  };

  const currentStudent =
    DEMO_STUDENTS.find((s) => s.id === scenarioStudentIdMap[activeScenario]) ||
    DEMO_STUDENTS[0];

  const currentAttempts = attemptsState[activeScenario] || [];
  const currentMastery = DEMO_SCENARIO_MASTERY[activeScenario] || [];
  const currentRisk = DEMO_SCENARIO_RISK[activeScenario] || DEMO_SCENARIO_RISK.A;
  const currentInterventions = interventionsState[activeScenario] || [];
  const currentCareer = DEMO_SCENARIO_CAREER[activeScenario] || DEMO_SCENARIO_CAREER.A;
  const scenarioMeta = DEMO_SCENARIOS[activeScenario] || DEMO_SCENARIOS.A;

  // Interactive local demo handlers
  const approveInterventionPlan = (planId: string) => {
    setInterventionsState((prev) => {
      const updated = { ...prev };
      const currentList = updated[activeScenario] ? [...updated[activeScenario]] : [];
      const planIdx = currentList.findIndex((p) => p.id === planId);
      if (planIdx !== -1) {
        currentList[planIdx] = {
          ...currentList[planIdx],
          lifecycle_status: 'APPROVED',
          observational_note: `Approved by faculty on ${new Date().toISOString().split('T')[0]}. Verification logged.`,
        };
        updated[activeScenario] = currentList;
      }
      return updated;
    });
  };

  const completeActionItem = (planId: string, itemIndex: number) => {
    setInterventionsState((prev) => {
      const updated = { ...prev };
      const currentList = updated[activeScenario] ? [...updated[activeScenario]] : [];
      const planIdx = currentList.findIndex((p) => p.id === planId);
      if (planIdx !== -1) {
        const plan = { ...currentList[planIdx] };
        const items = [...plan.action_items];
        if (items[itemIndex]) {
          items[itemIndex] = {
            ...items[itemIndex],
            completed: !items[itemIndex].completed,
            evidence_submitted: !items[itemIndex].completed
              ? `Demonstrated in lab on ${new Date().toISOString().split('T')[0]}`
              : undefined,
          };
          plan.action_items = items;
          currentList[planIdx] = plan;
          updated[activeScenario] = currentList;
        }
      }
      return updated;
    });
  };

  const submitAssessmentAttempt = (assessmentId: string, marks: number) => {
    setAttemptsState((prev) => {
      const updated = { ...prev };
      const currentList = updated[activeScenario] ? [...updated[activeScenario]] : [];
      const existingIdx = currentList.findIndex((a) => a.assessment_id === assessmentId);
      const newAttempt: DemoAssessmentAttempt = {
        assessment_id: assessmentId,
        student_id: currentStudent.id,
        marks_obtained: marks,
        status: 'EVALUATED',
        bloom_distribution: [
          { level: 'Apply (L3)', marks: marks * 0.6, max: 30 },
          { level: 'Analyze (L4)', marks: marks * 0.4, max: 20 },
        ],
        engagement_telemetry: {
          focus_time_minutes: 45.0,
          tab_blur_count: 0,
          interaction_events: 85,
          device_type: 'Evaluator Workstation (Demo)',
        },
      };
      if (existingIdx !== -1) {
        currentList[existingIdx] = newAttempt;
      } else {
        currentList.push(newAttempt);
      }
      updated[activeScenario] = currentList;
      return updated;
    });
  };

  return (
    <DemoContext.Provider
      value={{
        isDemoMode,
        setIsDemoMode: handleSetDemoMode,
        activeScenario,
        setActiveScenario,
        activeRole,
        setActiveRole,
        scenarioMeta,
        currentStudent,
        currentAttempts,
        currentMastery,
        currentRisk,
        currentInterventions,
        currentCareer,
        institution: DEMO_INSTITUTION,
        students: DEMO_STUDENTS,
        faculty: DEMO_FACULTY,
        subjects: DEMO_SUBJECTS,
        clos: DEMO_CLOS,
        topics: DEMO_TOPICS,
        assessments: DEMO_ASSESSMENTS,
        careerRoles: DEMO_CAREER_ROLES,
        dashboardData: DEMO_DASHBOARD_DATA,
        approveInterventionPlan,
        completeActionItem,
        submitAssessmentAttempt,
      }}
    >
      {children}
    </DemoContext.Provider>
  );
};

export const useDemo = (): DemoContextType => {
  const context = useContext(DemoContext);
  if (!context) {
    throw new Error('useDemo must be used within a DemoProvider');
  }
  return context;
};
