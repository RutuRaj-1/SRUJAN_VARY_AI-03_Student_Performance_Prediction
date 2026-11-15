import React from 'react';
import { useDemo } from '@/demo/demo-context';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';
import {
  Compass,
  Layers,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Play,
  ExternalLink,
  BookOpen,
  Award,
  Briefcase,
  Database,
  Lock,
} from 'lucide-react';
import { DEMO_SCENARIOS } from '@/demo/demo-data';

export const DemoGuidePage: React.FC = () => {
  const { activeScenario, setActiveScenario } = useDemo();

  const walkthroughSteps = [
    {
      step: 1,
      title: 'Public Product Website & Problem Narrative',
      route: '/',
      icon: ExternalLink,
      narration:
        'Explain why traditional percentages and end-term exams fail to detect topic gaps early. Highlight the 6 structural limitations.',
      action: 'Showcase the Hero, Problem breakdown, and 7-Step Solution Pipeline.',
    },
    {
      step: 2,
      title: 'Unified Multi-Persona Dashboard',
      route: '/app/dashboard',
      icon: Layers,
      narration:
        'Show how institution leaders, faculty, and students each receive tailored intelligence. Contrast aggregate cohort health with individual progress.',
      action: 'Toggle between Student, Faculty, and Institution perspectives in the top banner.',
    },
    {
      step: 3,
      title: 'Module 01: Academic Data Intelligence Hub',
      route: '/app/academic-data',
      icon: Database,
      narration:
        'Demonstrate that reliable intelligence starts with verifiable data. Review verified vs unverified marks and the automated quality scanner.',
      action: 'Inspect the Student Directory and Data Quality findings.',
    },
    {
      step: 4,
      title: 'Module 02: AI Syllabus & Competency Intelligence',
      route: '/app/syllabus',
      icon: BookOpen,
      narration:
        'Show automated extraction of Course Learning Outcomes (CLOs), units, and Bloom taxonomy levels from official course curriculum documents.',
      action: 'Expand Unit 1 & Unit 3 in Advanced Algorithms (CS601).',
    },
    {
      step: 5,
      title: 'Module 03: Assessment Engine & Observational Telemetry',
      route: '/app/assessments',
      icon: CheckCircle2,
      narration:
        'Assessments generate granular evidence items mapped to Bloom levels. Observable interaction telemetry respects privacy with zero invasive surveillance.',
      action: 'Inspect Midterm evaluation breakdown for Scenario A vs Scenario C.',
    },
    {
      step: 6,
      title: 'Module 04: Learning Mastery & Performance Analytics',
      route: '/app/mastery',
      icon: Award,
      narration:
        'Explain that missing assessments are never scored as zero. Contrast Scenario C (Rohan: Dynamic Programming gap) with Scenario D (Ananya: Insufficient Evidence).',
      action: 'Review the Topic Mastery grid and Course Learning Outcome attainments.',
    },
    {
      step: 7,
      title: 'Module 05: Academic Risk Prediction Engine',
      route: '/app/risk',
      icon: AlertTriangle,
      narration:
        'Explain time-bounded feature engineering that prevents leakage. Review adverse factors (declining trajectory, low attendance) driving Rohan\'s 78% risk.',
      action: 'Inspect the Explainable Factor Breakdown and Dataset Readiness Gate.',
    },
    {
      step: 8,
      title: 'Module 06: Personalized Academic Intervention',
      route: '/app/interventions',
      icon: BookOpen,
      narration:
        'Turn risk signals into structured action. Faculty advisors review recommendations, customize milestones, and monitor student recovery.',
      action: 'Simulate approving an intervention or marking a laboratory milestone complete.',
    },
    {
      step: 9,
      title: 'Module 07: Career Readiness & Skill Gap Analysis',
      route: '/app/career-readiness',
      icon: Briefcase,
      narration:
        'Align demonstrated academic and practical competencies with market roles. Emphasize separate academic vs practical project verification.',
      action: 'Inspect the 5-Tier Skill Gap analysis for Full-Stack and AI Engineer roles.',
    },
    {
      step: 10,
      title: 'Digital Trust & Placement Officer Privacy Firewall',
      route: '/app/risk',
      icon: Lock,
      narration:
        'Switch perspective to Placement Officer and demonstrate that academic risk is strictly locked out. Protects students from recruitment bias.',
      action: 'Click "Placement" in the Role Switcher and observe the Privacy Firewall.',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="border-b border-[#DCE6E2] pb-5">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Badge variant="brand" className="text-[11px] font-mono">
                PITCH & DEMO GUIDE
              </Badge>
              <Badge variant="outline" className="text-[11px]">
                SRUJAN 2026
              </Badge>
            </div>
            <h1 className="mt-2 text-2xl font-bold tracking-tight text-[#172825] sm:text-3xl font-sans">
              Interactive Platform Demonstration Guide
            </h1>
            <p className="mt-1 text-sm text-[#40524E] max-w-2xl">
              Follow this structured 10-step walkthrough to evaluate the entire MASTERY platform from the public landing page through all seven evidence-based intelligence modules.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link to="/app/dashboard">
              <Button variant="primary" size="md" className="gap-2">
                <Play className="h-4 w-4" />
                <span>Launch Interactive Demo</span>
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Synthetic Scenario Selector Cards */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-[#172825] flex items-center gap-2">
            <Layers className="h-4 w-4 text-[#237277]" />
            <span>Select a Synthetic Student Scenario for Testing:</span>
          </h2>
          <span className="text-xs text-[#687A75]">Synchronized across all 7 modules</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Object.values(DEMO_SCENARIOS).map((scenario) => {
            const isSelected = activeScenario === scenario.id;
            return (
              <div
                key={scenario.id}
                onClick={() => setActiveScenario(scenario.id)}
                className={`p-4 rounded-[6px] border cursor-pointer transition-all ${
                  isSelected
                    ? 'bg-[#EEF8F7] border-[#237277] shadow-sm ring-1 ring-[#237277]'
                    : 'bg-white border-[#DCE6E2] hover:border-[#BDCEC8]'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <Badge variant={scenario.badgeVariant}>{scenario.badgeLabel}</Badge>
                  <span className="font-mono text-xs text-[#687A75]">{scenario.enrollmentNumber}</span>
                </div>
                <div className="font-bold text-sm text-[#172825]">{scenario.studentName}</div>
                <p className="text-xs text-[#40524E] mt-1 line-clamp-2 leading-relaxed">
                  {scenario.summary}
                </p>
                <div className="mt-3 pt-2 border-t border-[#DCE6E2] flex items-center justify-between text-[11px]">
                  <span className="text-[#687A75]">Sem {scenario.semester} · CSE</span>
                  <span className={`font-semibold ${isSelected ? 'text-[#237277]' : 'text-slate-400'}`}>
                    {isSelected ? '✓ Active Scenario' : 'Click to Select'}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Step-by-Step Walkthrough Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Compass className="h-5 w-5 text-[#237277]" />
            <CardTitle>Recommended 10-Step Evaluation Journey</CardTitle>
          </div>
          <Badge variant="outline" className="font-mono text-xs">
            3-Min / 7-Min / 12-Min Scripts Ready
          </Badge>
        </CardHeader>
        <CardContent className="p-0">
          <div className="divide-y divide-[#DCE6E2]">
            {walkthroughSteps.map((step) => {
              const Icon = step.icon;
              return (
                <div key={step.step} className="p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 hover:bg-[#F7FAF9] transition-colors">
                  <div className="flex items-start gap-4 flex-1">
                    <div className="h-8 w-8 rounded-[4px] bg-[#EEF8F7] border border-[#BDCEC8] text-[#123E40] font-bold text-sm flex items-center justify-center shrink-0">
                      <Icon className="h-4 w-4 text-[#237277]" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-bold text-sm text-[#172825]">{step.title}</h3>
                        <span className="text-[10px] font-mono text-[#687A75] bg-slate-100 px-1.5 py-0.5 rounded">
                          {step.route}
                        </span>
                      </div>
                      <p className="text-xs text-[#40524E] mt-1 leading-relaxed">
                        <strong className="text-[#172825]">Speaking Prompt:</strong> "{step.narration}"
                      </p>
                      <p className="text-xs text-[#237277] mt-0.5">
                        <strong className="text-[#123E40]">Recommended Action:</strong> {step.action}
                      </p>
                    </div>
                  </div>

                  <Link to={step.route} className="shrink-0">
                    <Button variant="outline" size="sm" className="gap-1.5 text-xs">
                      <span>Jump to Screen</span>
                      <ArrowRight className="h-3 w-3" />
                    </Button>
                  </Link>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Ethical Charter Box */}
      <div className="p-4 rounded-[6px] bg-[#EEF8F7] border border-[#BDCEC8] flex items-start gap-3">
        <ShieldCheck className="h-5 w-5 text-[#237277] shrink-0 mt-0.5" />
        <div className="text-xs text-[#123E40] leading-relaxed">
          <strong>Digital Trust & Ethical AI Charter:</strong> All synthetic data rendered during this demonstration is isolated in browser memory and does not write to external production databases. Academic risk metrics are intended exclusively for supportive faculty advising, and are permanently firewalled from campus placement recruiters to prevent algorithmic bias.
        </div>
      </div>
    </div>
  );
};
