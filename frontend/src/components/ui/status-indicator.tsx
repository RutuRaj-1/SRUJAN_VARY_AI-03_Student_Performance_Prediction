import React from 'react';
import { cn } from '@/utils/cn';

export interface StatusIndicatorProps {
  status: 'connected' | 'healthy' | 'unconfigured' | 'disconnected' | 'error' | 'loading';
  label?: string;
  className?: string;
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({ status, label, className }) => {
  const statusConfig = {
    connected: { color: 'bg-emerald-500', ping: 'bg-emerald-400', text: 'Operational' },
    healthy: { color: 'bg-emerald-500', ping: 'bg-emerald-400', text: 'Healthy' },
    unconfigured: { color: 'bg-amber-400', ping: '', text: 'Not Configured' },
    disconnected: { color: 'bg-rose-500', ping: '', text: 'Disconnected' },
    error: { color: 'bg-rose-500', ping: '', text: 'Unavailable' },
    loading: { color: 'bg-blue-400', ping: 'bg-blue-300 animate-ping', text: 'Checking...' },
  };

  const config = statusConfig[status] || statusConfig.unconfigured;

  return (
    <div className={cn('inline-flex items-center gap-2 text-xs font-medium text-slate-700', className)}>
      <span className="relative flex h-2 w-2">
        {config.ping && (
          <span className={cn('animate-ping absolute inline-flex h-full w-full rounded-full opacity-75', config.ping)} />
        )}
        <span className={cn('relative inline-flex rounded-full h-2 w-2', config.color)} />
      </span>
      <span>{label || config.text}</span>
    </div>
  );
};
