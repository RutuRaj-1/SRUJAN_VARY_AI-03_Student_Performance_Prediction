import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Server, Database, RefreshCw, Terminal } from 'lucide-react';
import { healthService } from '@/services/health-service';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { StatusIndicator } from '@/components/ui/status-indicator';

export const DiagnosticsPage: React.FC = () => {
  const {
    data: appHealth,
    isLoading: isAppLoading,
    refetch: refetchApp,
    isRefetching: isAppRefetching,
  } = useQuery({
    queryKey: ['backend-health'],
    queryFn: healthService.checkAppHealth,
  });

  const {
    data: dbHealth,
    isLoading: isDbLoading,
    refetch: refetchDb,
    isRefetching: isDbRefetching,
  } = useQuery({
    queryKey: ['database-health'],
    queryFn: healthService.checkDatabaseHealth,
  });

  const refreshAll = () => {
    refetchApp();
    refetchDb();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900">System Diagnostics & Environment Probe</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time verification of backend services, database readiness, and integration contracts.
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={refreshAll}
          isLoading={isAppRefetching || isDbRefetching}
          className="gap-2"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          <span>Re-probe All Services</span>
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* API Health Probe */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Server className="h-4 w-4 text-blue-600" />
              <CardTitle>FastAPI Core Engine (/api/v1/health)</CardTitle>
            </div>
            <StatusIndicator
              status={isAppLoading ? 'loading' : appHealth?.status === 'healthy' ? 'healthy' : 'disconnected'}
            />
          </CardHeader>
          <CardContent className="space-y-3 text-xs">
            <div className="flex justify-between py-1.5 border-b border-slate-100">
              <span className="text-slate-500">Service Name:</span>
              <span className="font-mono font-medium">{appHealth?.app_name || 'MASTERY'}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-100">
              <span className="text-slate-500">Environment:</span>
              <span className="font-mono font-medium">{appHealth?.environment || 'development'}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-100">
              <span className="text-slate-500">API Version:</span>
              <span className="font-mono font-medium">{appHealth?.version || '0.1.0'}</span>
            </div>
            <div className="flex justify-between py-1.5">
              <span className="text-slate-500">Timestamp:</span>
              <span className="font-mono text-slate-600">{appHealth?.timestamp || 'N/A'}</span>
            </div>
          </CardContent>
        </Card>

        {/* Database Health Probe */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Database className="h-4 w-4 text-emerald-600" />
              <CardTitle>Database Connectivity (/api/v1/health/database)</CardTitle>
            </div>
            <StatusIndicator
              status={
                isDbLoading
                  ? 'loading'
                  : dbHealth?.status === 'connected'
                  ? 'connected'
                  : 'unconfigured'
              }
            />
          </CardHeader>
          <CardContent className="space-y-3 text-xs">
            <div className="flex justify-between py-1.5 border-b border-slate-100">
              <span className="text-slate-500">Configuration Flag:</span>
              <Badge variant={dbHealth?.configured ? 'success' : 'default'} className="font-mono text-[10px]">
                {dbHealth?.configured ? 'DATABASE_URL Set' : 'Unconfigured (Safe Standby)'}
              </Badge>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-100">
              <span className="text-slate-500">Target Driver:</span>
              <span className="font-mono font-medium">PostgreSQL / Supabase (SQLAlchemy 2.x)</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-100">
              <span className="text-slate-500">Roundtrip Latency:</span>
              <span className="font-mono font-medium">
                {dbHealth?.latency_ms !== null && dbHealth?.latency_ms !== undefined
                  ? `${dbHealth.latency_ms} ms`
                  : 'N/A'}
              </span>
            </div>
            <div className="flex justify-between py-1.5">
              <span className="text-slate-500">Status Message:</span>
              <span className="font-mono text-slate-600 truncate max-w-[220px]" title={dbHealth?.message}>
                {dbHealth?.message || 'Probing...'}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* CLI & Local Command Reference */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Terminal className="h-4 w-4 text-slate-700" />
            <CardTitle>Local Service Execution Reference</CardTitle>
          </div>
          <Badge variant="outline" className="font-mono text-xs">
            PowerShell / Bash
          </Badge>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
            <div className="p-3 bg-slate-900 text-slate-200 rounded-md">
              <div className="text-slate-400 text-[11px] mb-1"># Run FastAPI Backend</div>
              <code>cd backend</code><br />
              <code>.venv\Scripts\uvicorn app.main:app --reload --port 8000</code>
            </div>
            <div className="p-3 bg-slate-900 text-slate-200 rounded-md">
              <div className="text-slate-400 text-[11px] mb-1"># Run React Frontend</div>
              <code>cd frontend</code><br />
              <code>pnpm dev --port 5173</code>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
