import React from 'react';
import { Link } from 'react-router-dom';
import {
  AlertTriangle,
  ArrowRight,
  Database,
  FileQuestion,
  Clock,
  Briefcase,
  XCircle,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

export const ProblemPage: React.FC = () => {
  const problems = [
    {
      num: '01',
      title: 'Academic Records Are Fragmented Across Silos',
      icon: Database,
      summary:
        'Attendance registries, laboratory journals, and examination mark sheets live in disconnected software files and spreadsheets.',
      conventional:
        'Faculty and administrators see isolated snapshot records. A student with declining attendance cannot be easily correlated with declining quiz scores across semesters.',
      consequence:
        'Institutions lack a unified longitudinal evidence ledger, preventing early academic intervention.',
    },
    {
      num: '02',
      title: 'Overall Marks Conceal Critical Topic-Level Gaps',
      icon: FileQuestion,
      summary:
        'Conventional academic reporting collapses multidimensional learning into a single composite percentage or GPA score.',
      conventional:
        'A student who scores 65% in Data Structures is marked as "Passing". The number completely conceals that they scored 90% on basic memory arrays but 20% on dynamic programming and graph algorithms.',
      consequence:
        'Students progress to higher-level courses with fatal conceptual blind spots that compound over time.',
    },
    {
      num: '03',
      title: 'Academic Difficulty is Detected Far Too Late',
      icon: Clock,
      summary:
        'Universities identify academic distress only after end-semester examination results are published.',
      conventional:
        'Warning notices are issued post-facto. By the time a student receives failing marks, the academic term has concluded and remediation opportunities have closed.',
      consequence:
        'Students enter academic probation or drop out because warning signals were not time-bounded before critical cutoff deadlines.',
    },
    {
      num: '04',
      title: 'Academic Learning Disconnects from Industry Competencies',
      icon: Briefcase,
      summary:
        'Course learning outcomes outlined in syllabi are not mapped to verifiable industry role requirements.',
      conventional:
        'Graduating students present high GPAs but lack verified evidence proving they can architect distributed databases, debug multithreaded systems, or deploy machine learning models.',
      consequence:
        'Graduates struggle during recruitment, and placement cells cannot identify specific role-aligned skill deficits before campus placement seasons.',
    },
  ];

  return (
    <div className="py-16 md:py-24">
      <div className="max-w-7xl mx-auto px-6">
        {/* Page Header */}
        <div className="max-w-3xl mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-[3px] bg-[#EEF8F7] text-[#123E40] text-xs font-semibold font-mono border border-[#BDCEC8] mb-4">
            <AlertTriangle className="h-3.5 w-3.5 text-[#237277]" />
            <span>Problem Formulation · AI-03</span>
          </div>

          <h1 className="text-3xl md:text-5xl font-bold tracking-tight text-[#172825] font-sans leading-tight">
            Traditional academic metrics tell only part of the story.
          </h1>

          <p className="mt-4 text-base md:text-lg text-[#40524E] leading-relaxed">
            Higher education institutions evaluate student performance using attendance percentages, internal test scores, and end-semester grades. While these records are historical facts, they are structural failure points for proactive pedagogy.
          </p>
        </div>

        {/* 4 Structural Problem Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
          {problems.map((prob) => {
            const Icon = prob.icon;
            return (
              <Card key={prob.num} className="border-[#DCE6E2] shadow-subtle flex flex-col justify-between">
                <CardHeader className="pb-4 border-b border-[#DCE6E2] bg-[#F7FAF9]">
                  <div className="flex items-center justify-between w-full">
                    <span className="font-mono text-xs font-bold px-2 py-0.5 rounded-[2px] bg-white text-[#237277] border border-[#BDCEC8]">
                      CHALLENGE {prob.num}
                    </span>
                    <Icon className="h-5 w-5 text-[#237277]" />
                  </div>
                  <CardTitle className="text-base font-bold text-[#172825] mt-3">
                    {prob.title}
                  </CardTitle>
                </CardHeader>

                <CardContent className="pt-5 space-y-4 text-xs">
                  <p className="text-[#172825] font-medium leading-relaxed">
                    {prob.summary}
                  </p>

                  <div className="space-y-3 pt-3 border-t border-[#DCE6E2]">
                    <div className="flex items-start gap-2.5 bg-rose-50/70 p-3 rounded-[4px] border border-rose-200">
                      <XCircle className="h-4 w-4 text-rose-600 shrink-0 mt-0.5" />
                      <div>
                        <strong className="text-rose-900 block font-semibold mb-0.5">Conventional Reality:</strong>
                        <span className="text-rose-800 leading-relaxed">{prob.conventional}</span>
                      </div>
                    </div>

                    <div className="flex items-start gap-2.5 bg-[#EEF8F7] p-3 rounded-[4px] border border-[#BDCEC8]">
                      <AlertTriangle className="h-4 w-4 text-[#237277] shrink-0 mt-0.5" />
                      <div>
                        <strong className="text-[#123E40] block font-semibold mb-0.5">Systemic Consequence:</strong>
                        <span className="text-[#40524E] leading-relaxed">{prob.consequence}</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Comparison Callout: Marks vs Mastery */}
        <div className="p-8 rounded-[6px] bg-[#123E40] text-white border border-[#18575A] shadow-card">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
            <div>
              <span className="text-xs font-mono font-bold text-[#D9F0EE] uppercase tracking-wider block mb-2">
                Conceptual Contrast
              </span>
              <h2 className="text-2xl md:text-3xl font-bold font-sans">
                Marks Measure History. <br />
                Mastery Drives Intervention.
              </h2>
              <p className="text-xs md:text-sm text-slate-300 mt-3 leading-relaxed">
                MASTERY moves institutional reporting beyond numerical grades. By parsing course syllabi into granular cognitive units, mapping assessment questions to Bloom's taxonomy, and applying time-bounded early risk screening, institutions can identify difficulty before failure occurs.
              </p>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3.5 rounded-[4px] bg-[#0C2D2F] border border-[#18575A]">
                <div className="text-[#BDCEC8] font-mono text-[10px] font-bold uppercase">Legacy System</div>
                <div className="text-white font-bold mt-1">Student Score: 62% in Semester 4 Operating Systems</div>
                <div className="text-slate-400 mt-0.5">Outcome: Passed with Grade C. No action taken. Student subsequently fails advanced cloud engineering in Semester 6.</div>
              </div>

              <div className="p-3.5 rounded-[4px] bg-[#18575A] border border-[#2D8E92]">
                <div className="text-[#D9F0EE] font-mono text-[10px] font-bold uppercase">The MASTERY Platform</div>
                <div className="text-white font-bold mt-1">Diagnostic Breakdown: Mastered Memory Paging, 22% in Concurrency Mutexes</div>
                <div className="text-[#D9F0EE] mt-0.5">Outcome: System flags topic deficit in Week 6; faculty approves targeted lab clinic; student recovers before semester cutoff.</div>
              </div>
            </div>
          </div>
        </div>

        {/* CTA to Solution */}
        <div className="mt-16 text-center">
          <h3 className="text-lg font-bold text-[#172825]">Ready to see how MASTERY addresses these four challenges?</h3>
          <p className="text-xs text-[#40524E] mt-1 mb-6">Explore our interconnected, seven-module evidence intelligence workflow.</p>
          <div className="flex items-center justify-center gap-4">
            <Link to="/solution">
              <Button variant="primary" size="md" className="gap-2 text-xs">
                <span>Explore Our Solution</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </Button>
            </Link>
            <Link to="/app/dashboard">
              <Button variant="outline" size="md" className="text-xs border-[#BDCEC8]">
                <span>Open Application Workspace</span>
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
