import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/context/auth-context';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, CheckCircle2, Lock, Mail, User, ShieldCheck } from 'lucide-react';

export const RegisterPage: React.FC = () => {
  const { register } = useAuth();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setSuccessMsg(null);

    if (password.length < 6) {
      setErrorMsg('Password must be at least 6 characters long.');
      return;
    }

    if (password !== confirmPassword) {
      setErrorMsg('Passwords do not match. Please verify.');
      return;
    }

    setIsLoading(true);
    const { error, data } = await register(fullName, email, password);
    setIsLoading(false);

    if (error) {
      setErrorMsg(error.message);
    } else {
      if (data?.user && !data.session) {
        setSuccessMsg(
          'Registration successful! Please check your institutional email address to confirm your account before logging in.'
        );
      } else {
        setSuccessMsg(
          'Registration submitted successfully! Your account has been registered with STUDENT role and is currently PENDING approval.'
        );
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <div className="max-w-md w-full space-y-6">
        <div className="text-center space-y-2">
          <div className="inline-flex border-2 border-black rounded-[6px] overflow-hidden bg-white shadow-sm p-1">
            <img src="/logo.png" alt="MASTERY" className="h-12 w-auto object-contain block" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Student Account Registration</h1>
          <p className="text-xs text-slate-500">Beyond Marks. Towards Mastery.</p>
        </div>

        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle className="text-sm">Create New Student Identity</CardTitle>
            <Badge variant="outline" className="text-[10px] font-mono">
              Role: STUDENT
            </Badge>
          </CardHeader>
          <CardContent>
            {successMsg ? (
              <div className="space-y-4">
                <div className="p-4 bg-emerald-50 border border-emerald-200 rounded text-xs text-emerald-800 flex items-start gap-3">
                  <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0 mt-0.5" />
                  <div className="space-y-1">
                    <strong className="block text-emerald-900">Registration Complete</strong>
                    <p className="leading-relaxed">{successMsg}</p>
                  </div>
                </div>
                <Link to="/login">
                  <Button className="w-full">Proceed to Sign In</Button>
                </Link>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                {errorMsg && (
                  <div className="p-3 bg-rose-50 border border-rose-200 rounded text-xs text-rose-700 flex items-start gap-2">
                    <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                    <span>{errorMsg}</span>
                  </div>
                )}

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-700">Full Name</label>
                  <div className="relative">
                    <User className="h-4 w-4 text-slate-400 absolute left-3 top-2.5" />
                    <input
                      type="text"
                      required
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="e.g. John Doe"
                      className="w-full pl-9 pr-3 py-2 text-sm rounded-md border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-700">Institutional Email Address</label>
                  <div className="relative">
                    <Mail className="h-4 w-4 text-slate-400 absolute left-3 top-2.5" />
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="student@institution.edu"
                      className="w-full pl-9 pr-3 py-2 text-sm rounded-md border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-700">Password</label>
                  <div className="relative">
                    <Lock className="h-4 w-4 text-slate-400 absolute left-3 top-2.5" />
                    <input
                      type="password"
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Minimum 6 characters"
                      className="w-full pl-9 pr-3 py-2 text-sm rounded-md border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-700">Confirm Password</label>
                  <div className="relative">
                    <Lock className="h-4 w-4 text-slate-400 absolute left-3 top-2.5" />
                    <input
                      type="password"
                      required
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="Re-enter password"
                      className="w-full pl-9 pr-3 py-2 text-sm rounded-md border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                <div className="p-2.5 bg-slate-50 border border-slate-200 rounded text-[11px] text-slate-600 flex items-start gap-2">
                  <ShieldCheck className="h-4 w-4 text-blue-600 shrink-0 mt-0.5" />
                  <span>
                    New public registrations receive the default <strong>STUDENT</strong> role with <strong>PENDING</strong> approval status. Faculty and Administrator accounts are provisioned exclusively through authorized institutional administrators.
                  </span>
                </div>

                <Button type="submit" isLoading={isLoading} className="w-full mt-2">
                  Create Student Account
                </Button>
              </form>
            )}

            <div className="mt-6 pt-4 border-t border-slate-100 text-center text-xs text-slate-500">
              Already registered?{' '}
              <Link to="/login" className="font-semibold text-blue-600 hover:text-blue-700">
                Sign in here
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
