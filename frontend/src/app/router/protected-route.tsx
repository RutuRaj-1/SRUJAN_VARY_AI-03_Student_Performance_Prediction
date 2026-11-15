import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/context/auth-context';
import { UserRole } from '@/types/auth';
import { Clock, LogOut } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
  requireActive?: boolean;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  allowedRoles,
  requireActive = true,
}) => {
  const { isAuthenticated, isLoading, role, accountStatus, profile, logout } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 rounded-full border-2 border-blue-600 border-t-transparent animate-spin" />
          <p className="text-xs text-slate-500 font-medium">Verifying security credentials...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to={`/login?returnUrl=${encodeURIComponent(location.pathname)}`} replace />;
  }

  // Account Status Check (PENDING / SUSPENDED)
  if (requireActive && accountStatus === 'PENDING' && role !== 'SUPER_ADMIN') {
    return (
      <div className="min-h-screen flex items-center justify-center p-6 bg-slate-50">
        <Card className="max-w-md w-full shadow-md">
          <CardHeader>
            <div className="flex items-center gap-2 text-amber-600">
              <Clock className="h-5 w-5" />
              <CardTitle>Account Pending Institutional Approval</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4 text-xs text-slate-600">
            <p>
              Welcome, <strong>{profile?.full_name || profile?.email}</strong>. Your account has been registered with the{' '}
              <Badge variant="outline" className="font-mono text-[10px]">STUDENT</Badge> role.
            </p>
            <div className="p-3 bg-amber-50 border border-amber-200 rounded text-amber-900 leading-relaxed">
              Institutional security policies require your faculty advisor or department administrator to verify and activate your profile before you can access academic ledgers and assessment evaluations.
            </div>
            <div className="flex items-center justify-between pt-2 border-t border-slate-100">
              <span className="text-slate-400">Account Status: PENDING</span>
              <Button variant="outline" size="sm" onClick={() => logout()} className="gap-1.5">
                <LogOut className="h-3.5 w-3.5" />
                <span>Sign Out</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Role-Based Access Control Check
  if (allowedRoles && allowedRoles.length > 0 && !allowedRoles.includes(role) && role !== 'SUPER_ADMIN') {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};
