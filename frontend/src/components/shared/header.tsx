import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Server, ExternalLink, RefreshCw, LogOut, LogIn } from 'lucide-react';
import { healthService } from '@/services/health-service';
import { StatusIndicator } from '@/components/ui/status-indicator';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/context/auth-context';
import { Link } from 'react-router-dom';

export const Header: React.FC = () => {
  const { data: health, isLoading, isError, refetch } = useQuery({
    queryKey: ['backend-health'],
    queryFn: healthService.checkAppHealth,
    refetchInterval: 30000,
    retry: 1,
  });

  const { isAuthenticated, profile, role, accountStatus, logout } = useAuth();

  const getStatus = (): 'healthy' | 'error' | 'loading' => {
    if (isLoading) return 'loading';
    if (isError || !health) return 'error';
    return health.status === 'healthy' ? 'healthy' : 'error';
  };

  const getStatusLabel = (): string => {
    if (isLoading) return 'Probing Backend...';
    if (isError || !health) return 'Backend Offline';
    return `Backend Connected (v${health.version})`;
  };

  return (
    <header className="sticky top-0 z-30 h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between">
      {/* Brand & Tagline */}
      <div className="flex items-center gap-4">
        <Link to="/" className="flex items-center gap-2.5">
          <div className="h-9 w-9 rounded-md bg-blue-600 text-white flex items-center justify-center font-bold text-lg tracking-wider shadow-sm">
            M
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-900 tracking-tight text-lg">MASTERY</span>
              <Badge variant="outline" className="text-[10px] py-0 px-1.5 uppercase font-mono">
                Prototype v0.2
              </Badge>
            </div>
            <p className="text-xs text-slate-500 font-medium">Beyond Marks. Towards Mastery.</p>
          </div>
        </Link>
      </div>

      {/* Right Utility Bar: Health Status, Auth Profile, API Docs */}
      <div className="flex items-center gap-3">
        {/* Backend Connectivity Indicator */}
        <div
          onClick={() => refetch()}
          title="Click to re-probe backend connectivity"
          className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-md border border-slate-200 bg-slate-50 hover:bg-slate-100 transition-colors cursor-pointer text-xs"
        >
          <Server className="h-3.5 w-3.5 text-slate-500" />
          <StatusIndicator status={getStatus()} label={getStatusLabel()} />
          <RefreshCw className={`h-3 w-3 text-slate-400 ml-1 ${isLoading ? 'animate-spin' : ''}`} />
        </div>

        {/* OpenAPI Docs Link */}
        <a
          href="http://localhost:8000/docs"
          target="_blank"
          rel="noreferrer"
          className="hidden md:flex items-center gap-1.5 text-xs text-slate-600 hover:text-blue-600 font-medium px-2.5 py-1.5 rounded-md hover:bg-slate-100 transition-colors"
        >
          <ExternalLink className="h-3.5 w-3.5" />
          <span>API Docs</span>
        </a>

        {/* Authenticated User Profile Pill */}
        {isAuthenticated ? (
          <div className="flex items-center gap-3 pl-3 border-l border-slate-200">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-700 font-bold text-xs">
                {profile?.full_name ? profile.full_name[0].toUpperCase() : 'U'}
              </div>
              <div className="hidden lg:block text-left">
                <div className="text-xs font-semibold text-slate-900 leading-tight">
                  {profile?.full_name || profile?.email}
                </div>
                <div className="flex items-center gap-1 mt-0.5">
                  <Badge variant="info" className="text-[9px] py-0 px-1 font-mono">
                    {role}
                  </Badge>
                  {accountStatus === 'PENDING' && (
                    <Badge variant="warning" className="text-[9px] py-0 px-1 font-mono">
                      PENDING
                    </Badge>
                  )}
                </div>
              </div>
            </div>

            <Button
              variant="ghost"
              size="sm"
              onClick={() => logout()}
              title="Sign Out"
              className="text-slate-500 hover:text-slate-900 px-2 py-1"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        ) : (
          <div className="flex items-center gap-2 pl-3 border-l border-slate-200">
            <Link to="/login">
              <Button size="sm" variant="outline" className="gap-1.5">
                <LogIn className="h-3.5 w-3.5" />
                <span>Sign In</span>
              </Button>
            </Link>
            <Link to="/register">
              <Button size="sm" className="gap-1.5">
                <span>Register</span>
              </Button>
            </Link>
          </div>
        )}
      </div>
    </header>
  );
};
