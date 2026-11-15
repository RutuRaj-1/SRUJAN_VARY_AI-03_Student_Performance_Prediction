import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/context/auth-context';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ShieldAlert, ArrowLeft, LogOut } from 'lucide-react';

export const UnauthorizedPage: React.FC = () => {
  const { role, logout, profile } = useAuth();

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <div className="max-w-md w-full space-y-6">
        <Card className="shadow-md border-rose-200">
          <CardHeader>
            <div className="flex items-center gap-2 text-rose-600">
              <ShieldAlert className="h-5 w-5" />
              <CardTitle>403 — Access Restricted</CardTitle>
            </div>
            <Badge variant="error" className="font-mono text-[10px]">
              RBAC Violation
            </Badge>
          </CardHeader>
          <CardContent className="space-y-4 text-xs text-slate-600">
            <p>
              Your current authenticated identity (<strong>{profile?.email}</strong>) has been verified with role:
            </p>
            <div className="text-center py-2 bg-slate-100 rounded font-mono font-bold text-slate-800">
              {role}
            </div>
            <p className="leading-relaxed">
              You do not hold the required institutional permissions or administrative scope to view this section. If you believe this is an error, please reach out to your faculty administrator.
            </p>

            <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-3">
              <Link to="/">
                <Button variant="outline" size="sm" className="gap-1.5">
                  <ArrowLeft className="h-3.5 w-3.5" />
                  <span>Return to Dashboard</span>
                </Button>
              </Link>
              <Button variant="ghost" size="sm" onClick={() => logout()} className="gap-1.5 text-rose-600 hover:text-rose-700">
                <LogOut className="h-3.5 w-3.5" />
                <span>Switch Account</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
