import React from 'react';
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
  Activity,
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { useAuth } from '@/context/auth-context';
import { UserRole } from '@/types/auth';

interface NavItem {
  name: string;
  path: string;
  icon: React.ElementType;
  badge?: string;
  allowedRoles?: UserRole[];
}

const mainNav: NavItem[] = [
  {
    name: 'Dashboard Overview',
    path: '/',
    icon: LayoutDashboard,
  },
];

const moduleNav: NavItem[] = [
  {
    name: 'Academic Data Hub',
    path: '/academic-data',
    icon: Database,
    badge: 'Module 03',
    allowedRoles: ['STUDENT', 'FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN'],
  },
  {
    name: 'Syllabus & Competency',
    path: '/syllabus',
    icon: FileText,
    badge: 'Module 02',
    allowedRoles: ['STUDENT', 'FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN'],
  },
  {
    name: 'Assessment Engine',
    path: '/assessments',
    icon: CheckCircle2,
    badge: 'Module 04',
    allowedRoles: ['STUDENT', 'FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN'],
  },
  {
    name: 'Mastery Analytics',
    path: '/mastery',
    icon: Award,
    badge: 'Module 05',
    allowedRoles: ['STUDENT', 'FACULTY', 'PLACEMENT_OFFICER', 'INSTITUTION_ADMIN', 'SUPER_ADMIN'],
  },
  {
    name: 'Academic Risk Engine',
    path: '/academic-risk',
    icon: AlertTriangle,
    badge: 'Module 06',
    allowedRoles: ['STUDENT', 'FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN'],
  },
  {
    name: 'Interventions & Growth',
    path: '/interventions',
    icon: Compass,
    badge: 'Module 07',
    allowedRoles: ['STUDENT', 'FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN'],
  },
  {
    name: 'Career & Placement',
    path: '/career-readiness',
    icon: Briefcase,
    badge: 'Module 08',
    allowedRoles: ['STUDENT', 'PLACEMENT_OFFICER', 'FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN'],
  },
];

const systemNav: NavItem[] = [
  {
    name: 'System Diagnostics',
    path: '/diagnostics',
    icon: Activity,
    allowedRoles: ['SUPER_ADMIN', 'INSTITUTION_ADMIN'],
  },
];

export const Sidebar: React.FC = () => {
  const { role } = useAuth();

  const isAllowed = (item: NavItem): boolean => {
    if (!item.allowedRoles || item.allowedRoles.length === 0) return true;
    if (role === 'SUPER_ADMIN') return true;
    return item.allowedRoles.includes(role);
  };

  const visibleModules = moduleNav.filter(isAllowed);
  const visibleSystem = systemNav.filter(isAllowed);

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col shrink-0 min-h-[calc(100vh-4rem)] border-r border-slate-800">
      <div className="flex-1 py-4 px-3 space-y-6 overflow-y-auto">
        {/* Core Nav */}
        <div>
          <div className="px-3 mb-2 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Workspace
          </div>
          <div className="space-y-1">
            {mainNav.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-blue-600 text-white shadow-sm'
                      : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  )
                }
              >
                <item.icon className="h-4 w-4 shrink-0" />
                <span>{item.name}</span>
              </NavLink>
            ))}
          </div>
        </div>

        {/* 7 Modules Nav (Filtered by role) */}
        <div>
          <div className="px-3 mb-2 text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center justify-between">
            <span>Product Domains</span>
            <span className="text-[10px] text-slate-400 font-mono">
              {visibleModules.length} Modules
            </span>
          </div>
          <div className="space-y-1">
            {visibleModules.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  cn(
                    'flex items-center justify-between px-3 py-2 rounded-md text-sm font-medium transition-colors group',
                    isActive
                      ? 'bg-slate-800 text-white'
                      : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  )
                }
              >
                <div className="flex items-center gap-3 truncate">
                  <item.icon className="h-4 w-4 shrink-0 text-slate-400 group-hover:text-white" />
                  <span className="truncate">{item.name}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] bg-slate-800 border border-slate-700 text-slate-400 group-hover:text-slate-300 px-1.5 py-0.5 rounded font-mono shrink-0">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            ))}
          </div>
        </div>

        {/* System & Architecture (Admins only) */}
        {visibleSystem.length > 0 && (
          <div>
            <div className="px-3 mb-2 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              Administration
            </div>
            <div className="space-y-1">
              {visibleSystem.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-slate-800 text-white'
                        : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                    )
                  }
                >
                  <item.icon className="h-4 w-4 shrink-0 text-slate-400" />
                  <span>{item.name}</span>
                </NavLink>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800 text-xs text-slate-400">
        <p className="font-semibold text-slate-300">Phase 02 / 11</p>
        <p className="text-[11px] mt-0.5">Supabase Auth & RBAC Active</p>
      </div>
    </aside>
  );
};
