import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Database,
  FileText,
  CheckCircle2,
  Award,
  AlertTriangle,
  Compass,
  Briefcase,
  ChevronLeft,
  ChevronRight,
  ShieldAlert,
  BookOpen,
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { useAuth } from '@/context/auth-context';
import { useDemo } from '@/demo/demo-context';
import { UserRole } from '@/types/auth';

interface NavItem {
  name: string;
  path: string;
  icon: React.ElementType;
  moduleNumber?: string;
  allowedRoles?: UserRole[];
  firewalledFor?: UserRole[];
}

const mainNav: NavItem[] = [
  {
    name: 'Unified Dashboard',
    path: '/app/dashboard',
    icon: LayoutDashboard,
  },
  {
    name: 'Demo Walkthrough',
    path: '/demo-guide',
    icon: Compass,
  },
];

const moduleNav: NavItem[] = [
  {
    name: 'Academic Data Hub',
    path: '/app/academic-data',
    icon: Database,
    moduleNumber: '01',
    allowedRoles: ['STUDENT', 'FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN'],
  },
  {
    name: 'AI Syllabus Intelligence',
    path: '/app/syllabus',
    icon: FileText,
    moduleNumber: '02',
    allowedRoles: ['STUDENT', 'FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN'],
  },
  {
    name: 'Assessment Engine',
    path: '/app/assessments',
    icon: CheckCircle2,
    moduleNumber: '03',
    allowedRoles: ['STUDENT', 'FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN'],
  },
  {
    name: 'Mastery Analytics',
    path: '/app/mastery',
    icon: Award,
    moduleNumber: '04',
    allowedRoles: ['STUDENT', 'FACULTY', 'PLACEMENT_OFFICER', 'INSTITUTION_ADMIN', 'SUPER_ADMIN'],
  },
  {
    name: 'Academic Risk Engine',
    path: '/app/risk',
    icon: AlertTriangle,
    moduleNumber: '05',
    allowedRoles: ['STUDENT', 'FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN'],
    firewalledFor: ['PLACEMENT_OFFICER'],
  },
  {
    name: 'Personalized Interventions',
    path: '/app/interventions',
    icon: BookOpen,
    moduleNumber: '06',
    allowedRoles: ['STUDENT', 'FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN'],
    firewalledFor: ['PLACEMENT_OFFICER'],
  },
  {
    name: 'Career Readiness',
    path: '/app/career-readiness',
    icon: Briefcase,
    moduleNumber: '07',
    allowedRoles: ['STUDENT', 'PLACEMENT_OFFICER', 'FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN'],
  },
];

export const Sidebar: React.FC = () => {
  const { role: authRole } = useAuth();
  const { isDemoMode, activeRole } = useDemo();
  const [collapsed, setCollapsed] = useState(false);

  const effectiveRole = isDemoMode ? activeRole : authRole;

  const isAllowed = (item: NavItem): boolean => {
    if (item.firewalledFor && item.firewalledFor.includes(effectiveRole)) {
      return false;
    }
    if (!item.allowedRoles || item.allowedRoles.length === 0) return true;
    if (effectiveRole === 'SUPER_ADMIN') return true;
    return item.allowedRoles.includes(effectiveRole);
  };

  return (
    <aside
      className={cn(
        'bg-white border-r border-[#DCE6E2] flex flex-col transition-all duration-200 z-20 select-none',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Navigation Groups */}
      <div className="flex-1 overflow-y-auto py-4 px-2 space-y-6">
        {/* Core Nav */}
        <div>
          {!collapsed && (
            <div className="px-3 mb-2 text-[10px] font-bold text-[#687A75] uppercase tracking-wider font-mono">
              Workspace
            </div>
          )}
          <nav className="space-y-1">
            {mainNav.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 px-3 py-2 rounded-[4px] text-xs font-medium transition-colors',
                      isActive
                        ? 'bg-[#EEF8F7] text-[#123E40] border-l-2 border-[#237277] font-semibold'
                        : 'text-[#40524E] hover:bg-[#F7FAF9] hover:text-[#172825]'
                    )
                  }
                  title={collapsed ? item.name : undefined}
                >
                  <Icon className="h-4 w-4 shrink-0 text-[#237277]" />
                  {!collapsed && <span>{item.name}</span>}
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Seven Modules Group */}
        <div>
          {!collapsed && (
            <div className="px-3 mb-2 flex items-center justify-between text-[10px] font-bold text-[#687A75] uppercase tracking-wider font-mono">
              <span>Seven Modules</span>
              <span className="text-[9px] bg-[#EEF8F7] text-[#237277] px-1 py-0.2 rounded border border-[#BDCEC8]">
                M01–M07
              </span>
            </div>
          )}
          <nav className="space-y-1">
            {moduleNav.map((item) => {
              const allowed = isAllowed(item);
              const Icon = item.icon;
              const isFirewalled = item.firewalledFor?.includes(effectiveRole);

              if (isFirewalled) {
                // If firewalled (e.g. Placement Officer accessing Risk), display firewall lock indicator
                return (
                  <div
                    key={item.path}
                    className="flex items-center gap-3 px-3 py-2 rounded-[4px] text-xs text-slate-400 bg-slate-50/80 cursor-not-allowed opacity-60 border border-dashed border-slate-200"
                    title="Firewalled: Placement Officers are prohibited from viewing Student Risk predictions."
                  >
                    <ShieldAlert className="h-4 w-4 shrink-0 text-amber-600" />
                    {!collapsed && (
                      <div className="flex items-center justify-between flex-1">
                        <span className="line-through">{item.name}</span>
                        <span className="text-[9px] text-amber-700 bg-amber-50 px-1 py-0.5 rounded font-mono">
                          Firewall
                        </span>
                      </div>
                    )}
                  </div>
                );
              }

              if (!allowed) return null;

              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 px-3 py-2 rounded-[4px] text-xs font-medium transition-colors group',
                      isActive
                        ? 'bg-[#EEF8F7] text-[#123E40] border-l-2 border-[#237277] font-semibold'
                        : 'text-[#40524E] hover:bg-[#F7FAF9] hover:text-[#172825]'
                    )
                  }
                  title={collapsed ? `${item.moduleNumber}: ${item.name}` : undefined}
                >
                  <Icon className="h-4 w-4 shrink-0 text-[#237277] group-hover:text-[#123E40] transition-colors" />
                  {!collapsed && (
                    <div className="flex items-center justify-between flex-1">
                      <span className="truncate">{item.name}</span>
                      {item.moduleNumber && (
                        <span className="text-[10px] font-mono text-[#687A75] bg-[#F7FAF9] px-1 py-0.2 rounded border border-[#DCE6E2]">
                          M{item.moduleNumber}
                        </span>
                      )}
                    </div>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Footer: Collapse button */}
      <div className="p-3 border-t border-[#DCE6E2] flex items-center justify-between bg-[#F7FAF9]">
        {!collapsed && (
          <div className="text-[10px] text-[#687A75] font-mono">
            VARY · SRUJAN '26
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1 rounded-[4px] hover:bg-[#EEF8F7] text-[#687A75] hover:text-[#123E40] ml-auto transition-colors"
          title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </div>
    </aside>
  );
};
