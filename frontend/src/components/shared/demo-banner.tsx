import React from 'react';
import { useDemo } from '@/demo/demo-context';
import { UserRole } from '@/types/auth';
import { ShieldCheck, User, Compass, Layers, ToggleLeft, ToggleRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const DemoBanner: React.FC = () => {
  const {
    isDemoMode,
    setIsDemoMode,
    activeScenario,
    setActiveScenario,
    activeRole,
    setActiveRole,
  } = useDemo();

  return (
    <div className="bg-[#123E40] text-white border-b border-[#18575A] text-xs">
      <div className="max-w-7xl mx-auto px-4 py-2 flex flex-wrap items-center justify-between gap-3">
        {/* Left: Active Mode & Synthetic Disclaimer */}
        <div className="flex items-center gap-2.5">
          <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-[3px] bg-[#D9F0EE] text-[#123E40] font-mono font-bold text-[10px] uppercase tracking-wider">
            <ShieldCheck className="h-3 w-3 text-[#237277]" />
            {isDemoMode ? 'Synthetic Demo Mode' : 'Live Mode'}
          </div>
          <span className="text-slate-300 font-medium hidden sm:inline">
            DEMO DATA — SYNTHETIC / NOT REAL STUDENT RECORDS
          </span>
          <button
            onClick={() => setIsDemoMode(!isDemoMode)}
            className="flex items-center gap-1 text-[11px] text-slate-300 hover:text-white underline underline-offset-2 ml-2"
            title="Toggle between Frontend Demo Data and Live Backend API"
          >
            {isDemoMode ? <ToggleRight className="h-4 w-4 text-[#2D8E92]" /> : <ToggleLeft className="h-4 w-4 text-slate-400" />}
            <span>{isDemoMode ? 'Using Synthetic Fixtures' : 'Using Live Supabase'}</span>
          </button>
        </div>

        {/* Right: Walkthrough Guide link */}
        <div className="flex items-center gap-2 ml-auto">
          <Link
            to="/demo-guide"
            className="flex items-center gap-1 px-2.5 py-1 rounded-[3px] bg-[#237277] hover:bg-[#18575A] text-white font-medium transition-colors shadow-sm"
          >
            <Compass className="h-3 w-3" />
            <span>Interactive Demo Guide</span>
          </Link>
        </div>
      </div>

      {/* Sub-bar: Scenario Selector & Perspective Switcher */}
      {isDemoMode && (
        <div className="bg-[#0C2D2F] px-4 py-2 border-t border-[#18575A]/60 flex flex-wrap items-center justify-between gap-3">
          {/* Scenario Selector */}
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-[#BDCEC8] font-semibold text-[11px] uppercase tracking-wider flex items-center gap-1">
              <Layers className="h-3 w-3 text-[#2D8E92]" />
              Scenario:
            </span>
            <div className="inline-flex rounded-[4px] p-0.5 bg-[#123E40] border border-[#18575A] gap-0.5">
              {(
                [
                  { id: 'A', label: 'Scenario A: Strong Progress (Aarav)' },
                  { id: 'B', label: 'Scenario B: Inconsistent (Diya)' },
                  { id: 'C', label: 'Scenario C: Emerging Risk (Rohan)' },
                  { id: 'D', label: 'Scenario D: Insufficient Evidence (Ananya)' },
                ] as const
              ).map((s) => (
                <button
                  key={s.id}
                  onClick={() => setActiveScenario(s.id)}
                  className={`px-2 py-0.5 rounded-[2px] text-[11px] font-medium transition-all ${
                    activeScenario === s.id
                      ? 'bg-[#237277] text-white shadow-sm font-semibold'
                      : 'text-slate-300 hover:text-white hover:bg-[#18575A]'
                  }`}
                >
                  {s.label}
                </button>
              ))}
            </div>
          </div>

          {/* Perspective / Role Switcher */}
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-[#BDCEC8] font-semibold text-[11px] uppercase tracking-wider flex items-center gap-1">
              <User className="h-3 w-3 text-[#2D8E92]" />
              Role View:
            </span>
            <div className="inline-flex rounded-[4px] p-0.5 bg-[#123E40] border border-[#18575A] gap-0.5">
              {(
                [
                  { role: 'STUDENT', label: 'Student' },
                  { role: 'FACULTY', label: 'Faculty' },
                  { role: 'INSTITUTION_ADMIN', label: 'Admin' },
                  { role: 'PLACEMENT_OFFICER', label: 'Placement' },
                  { role: 'SUPER_ADMIN', label: 'Platform' },
                ] as const
              ).map((r) => (
                <button
                  key={r.role}
                  onClick={() => setActiveRole(r.role as UserRole)}
                  className={`px-2 py-0.5 rounded-[2px] text-[11px] font-medium transition-all ${
                    activeRole === r.role
                      ? 'bg-[#2D8E92] text-white shadow-sm font-semibold'
                      : 'text-slate-300 hover:text-white hover:bg-[#18575A]'
                  }`}
                >
                  {r.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
