import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/context/auth-context';
import { useDemo } from '@/demo/demo-context';
import { UserRole } from '@/types/auth';
import { Clock, LogOut, Sparkles } from 'lucide-react';
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
  const { isAuthenticated, isLoading, role: authRole, accountStatus, profile, logout } = useAuth();
  const { isDemoMode, setIsDemoMode, activeRole } = useDemo();
  const location = useLocation();

  // If loading live session and not in demo mode
  if (isLoading && !isDemoMode) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F7FAF9]">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 rounded-full border-2 border-[#237277] border-t-transparent animate-spin" />
          <p className="text-xs text-[#687A75] font-medium">Verifying security credentials...</p>
        </div>
      </div>
    );
  }

  // In demo mode, bypass live auth redirection
  if (!isDemoMode && !isAuthenticated) {
    return <Navigate to={`/login?returnUrl=${encodeURIComponent(location.pathname)}`} replace />;
  }

  // Effective role: Demo role takes precedence in Demo Mode
  const effectiveRole = isDemoMode ? activeRole : authRole;

  // Account Status Check (PENDING / SUSPENDED) - only enforced for real live authenticated accounts
  if (!isDemoMode && requireActive && accountStatus === 'PENDING' && effectiveRole !== 'SUPER_ADMIN') {
    return (
      <div className="min-h-screen flex items-center justify-center p-6 bg-[#F7FAF9]">
        <Card className="max-w-md w-full shadow-subtle border-[#DCE6E2]">
          <CardHeader>
            <div className="flex items-center gap-2 text-amber-600">
              <Clock className="h-5 w-5" />
              <CardTitle>Account Pending Institutional Approval</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4 text-xs text-[#40524E]">
            <p>
              Welcome, <strong>{profile?.full_name || profile?.email}</strong>. Your account has been registered with the{' '}
              <Badge variant="outline" className="font-mono text-[10px]">STUDENT</Badge> role.
            </p>
            <div className="p-3 bg-amber-50 border border-amber-200 rounded-[4px] text-amber-900 leading-relaxed">
              Institutional security policies require your faculty advisor or department administrator to verify and activate your profile before you can access live academic ledgers.
            </div>
            <div className="pt-3 border-t border-[#DCE6E2] space-y-2">
              <Button
                variant="primary"
                size="sm"
                onClick={() => setIsDemoMode(true)}
                className="w-full gap-2 bg-[#237277] hover:bg-[#18575A] text-white text-xs font-semibold"
              >
                <Sparkles className="h-3.5 w-3.5" />
                <span>Explore with In-Memory Synthetic Data (No DB Writes)</span>
              </Button>
              <div className="flex items-center justify-between pt-1">
                <span className="text-[#687A75]">Account Status: PENDING</span>
                <Button variant="outline" size="sm" onClick={() => logout()} className="gap-1.5 text-xs">
                  <LogOut className="h-3.5 w-3.5" />
                  <span>Sign Out</span>
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Role-Based Access Control Check
  if (allowedRoles && allowedRoles.length > 0 && !allowedRoles.includes(effectiveRole) && effectiveRole !== 'SUPER_ADMIN') {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};
