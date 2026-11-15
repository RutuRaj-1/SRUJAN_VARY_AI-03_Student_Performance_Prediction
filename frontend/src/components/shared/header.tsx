import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { ShieldCheck, Server, ExternalLink, RefreshCw } from 'lucide-react';
import { healthService } from '@/services/health-service';
import { StatusIndicator } from '@/components/ui/status-indicator';
import { Badge } from '@/components/ui/badge';

export const Header: React.FC = () => {
  const { data: health, isLoading, isError, refetch } = useQuery({
    queryKey: ['backend-health'],
    queryFn: healthService.checkAppHealth,
    refetchInterval: 30000,
    retry: 1,
  });

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
        <div className="flex items-center gap-2.5">
          <div className="h-9 w-9 rounded-md bg-blue-600 text-white flex items-center justify-center font-bold text-lg tracking-wider shadow-sm">
            M
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-900 tracking-tight text-lg">MASTERY</span>
              <Badge variant="outline" className="text-[10px] py-0 px-1.5 uppercase font-mono">
                Prototype v0.1
              </Badge>
            </div>
            <p className="text-xs text-slate-500 font-medium">Beyond Marks. Towards Mastery.</p>
          </div>
        </div>
      </div>

      {/* Right Utility Bar: Health Status, Environment, API Docs */}
      <div className="flex items-center gap-4">
        {/* Backend Connectivity Indicator */}
        <div
          onClick={() => refetch()}
          title="Click to re-probe backend connectivity"
          className="flex items-center gap-2 px-3 py-1.5 rounded-md border border-slate-200 bg-slate-50 hover:bg-slate-100 transition-colors cursor-pointer text-xs"
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
          className="flex items-center gap-1.5 text-xs text-slate-600 hover:text-blue-600 font-medium px-2.5 py-1.5 rounded-md hover:bg-slate-100 transition-colors"
        >
          <ExternalLink className="h-3.5 w-3.5" />
          <span>API Docs</span>
        </a>

        {/* Security / Trust Mode Indicator */}
        <div className="flex items-center gap-1.5 text-xs text-slate-500 pl-2 border-l border-slate-200">
          <ShieldCheck className="h-4 w-4 text-emerald-600" />
          <span className="font-mono text-[11px] text-slate-600">Strict RBAC</span>
        </div>
      </div>
    </header>
  );
};
