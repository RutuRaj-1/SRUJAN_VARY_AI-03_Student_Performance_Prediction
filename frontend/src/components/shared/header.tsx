import React from 'react';
import { LogOut, LogIn, Globe, Compass } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/context/auth-context';
import { useDemo } from '@/demo/demo-context';
import { Link, useLocation } from 'react-router-dom';

export const Header: React.FC = () => {
  const { isAuthenticated, profile, role, logout } = useAuth();
  const { isDemoMode, activeRole } = useDemo();
  const location = useLocation();

  // Determine current effective role (demo role takes precedence when in demo mode)
  const effectiveRole = isDemoMode ? activeRole : role;

  return (
    <header className="sticky top-0 z-30 h-14 bg-white border-b border-[#DCE6E2] px-6 flex items-center justify-between shadow-subtle">
      {/* Brand & Wordmark */}
      <div className="flex items-center gap-6">
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="h-8 w-8 rounded-[4px] bg-[#123E40] text-white flex items-center justify-center font-bold text-base tracking-wider shadow-sm group-hover:bg-[#237277] transition-colors">
            M
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-[#172825] tracking-tight text-base font-sans">MASTERY</span>
              <span className="text-[11px] font-mono text-[#687A75] hidden sm:inline">SRUJAN 2026</span>
            </div>
            <p className="text-[11px] text-[#687A75] font-medium leading-none hidden md:block">
              Beyond Marks. Towards Mastery.
            </p>
          </div>
        </Link>

        {/* Global Navigation links */}
        <nav className="hidden lg:flex items-center gap-1 text-xs font-medium text-[#40524E]">
          <Link
            to="/"
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-[4px] hover:bg-[#EEF8F7] hover:text-[#123E40] transition-colors"
          >
            <Globe className="h-3.5 w-3.5 text-[#237277]" />
            <span>Public Website</span>
          </Link>
          <Link
            to="/app/dashboard"
            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-[4px] transition-colors ${
              location.pathname.startsWith('/app')
                ? 'bg-[#EEF8F7] text-[#123E40] font-semibold'
                : 'hover:bg-[#EEF8F7] hover:text-[#123E40]'
            }`}
          >
            <span>Workspace</span>
          </Link>
          <Link
            to="/demo-guide"
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-[4px] hover:bg-[#EEF8F7] hover:text-[#123E40] transition-colors"
          >
            <Compass className="h-3.5 w-3.5 text-[#237277]" />
            <span>Demo Walkthrough</span>
          </Link>
        </nav>
      </div>

      {/* Right Controls: Role Indicator, Demo Mode Pill, User Auth */}
      <div className="flex items-center gap-3">
        {/* Effective Persona Badge */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-[4px] bg-[#EEF8F7] border border-[#BDCEC8]">
          <span className="text-[10px] text-[#687A75] uppercase tracking-wider font-semibold">Perspective:</span>
          <span className="text-xs font-semibold text-[#123E40]">{effectiveRole}</span>
        </div>

        {/* Auth Profile or Demo Guest State */}
        {isAuthenticated ? (
          <div className="flex items-center gap-2 pl-2 border-l border-[#DCE6E2]">
            <div className="text-right hidden sm:block">
              <div className="text-xs font-semibold text-[#172825] leading-tight">
                {profile?.full_name || profile?.email}
              </div>
              <div className="text-[10px] text-[#687A75]">{role}</div>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => logout()}
              className="gap-1 text-xs py-1 px-2 border-[#DCE6E2]"
              title="Sign Out"
            >
              <LogOut className="h-3 w-3 text-rose-600" />
              <span className="hidden sm:inline">Sign Out</span>
            </Button>
          </div>
        ) : (
          <div className="flex items-center gap-2 pl-2 border-l border-[#DCE6E2]">
            <Link to="/login">
              <Button variant="outline" size="sm" className="gap-1 text-xs py-1 px-2.5 border-[#DCE6E2]">
                <LogIn className="h-3 w-3 text-[#237277]" />
                <span>Institutional Login</span>
              </Button>
            </Link>
          </div>
        )}
      </div>
    </header>
  );
};
