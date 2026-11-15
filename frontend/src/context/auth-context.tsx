import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { User, Session } from '@supabase/supabase-js';
import { supabase } from '@/lib/supabase';
import { apiClient } from '@/lib/api-client';
import { UserProfile, UserRole, AccountStatus } from '@/types/auth';

interface AuthContextType {
  user: User | null;
  session: Session | null;
  profile: UserProfile | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  role: UserRole;
  accountStatus: AccountStatus;
  login: (email: string, password: string) => Promise<{ error: Error | null }>;
  register: (fullName: string, email: string, password: string) => Promise<{ error: Error | null; data?: any }>;
  logout: () => Promise<void>;
  resetPassword: (email: string) => Promise<{ error: Error | null }>;
  refreshProfile: () => Promise<void>;
  hasRole: (...roles: UserRole[]) => boolean;
  hasPermission: (permission: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchAuthoritativeProfile = useCallback(async (currentSession: Session | null) => {
    if (!currentSession?.access_token) {
      setProfile(null);
      return;
    }
    try {
      const data = await apiClient.get<UserProfile>('/auth/me');
      setProfile(data);
    } catch {
      // If backend is in standalone mode or unreachable, construct fallback from session metadata
      const meta = currentSession.user.user_metadata || {};
      const fallbackProfile: UserProfile = {
        user_id: currentSession.user.id,
        email: currentSession.user.email || '',
        full_name: meta.full_name || (currentSession.user.email ? currentSession.user.email.split('@')[0] : 'User'),
        role: (meta.role as UserRole) || 'STUDENT',
        account_status: (meta.account_status as AccountStatus) || 'PENDING',
        institution_id: meta.institution_id || null,
        permissions: [],
      };
      setProfile(fallbackProfile);
    }
  }, []);

  useEffect(() => {
    // 1. Initial Session check
    supabase.auth.getSession().then(({ data: { session: initialSession } }) => {
      setSession(initialSession);
      setUser(initialSession?.user ?? null);
      if (initialSession) {
        fetchAuthoritativeProfile(initialSession).finally(() => setIsLoading(false));
      } else {
        setIsLoading(false);
      }
    });

    // 2. Real-time Auth state change subscription
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (_event, newSession) => {
        setSession(newSession);
        setUser(newSession?.user ?? null);
        if (newSession) {
          await fetchAuthoritativeProfile(newSession);
        } else {
          setProfile(null);
        }
        setIsLoading(false);
      }
    );

    return () => {
      subscription.unsubscribe();
    };
  }, [fetchAuthoritativeProfile]);

  const login = async (email: string, password: string) => {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });
      if (error) throw error;
      if (data.session) {
        await fetchAuthoritativeProfile(data.session);
      }
      return { error: null };
    } catch (err: any) {
      return { error: err };
    }
  };

  const register = async (fullName: string, email: string, password: string) => {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: fullName.trim(),
            role: 'STUDENT',
            account_status: 'PENDING',
          },
        },
      });
      if (error) throw error;
      return { error: null, data };
    } catch (err: any) {
      return { error: err };
    }
  };

  const logout = async () => {
    await supabase.auth.signOut();
    setUser(null);
    setSession(null);
    setProfile(null);
  };

  const resetPassword = async (email: string) => {
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/login`,
      });
      if (error) throw error;
      return { error: null };
    } catch (err: any) {
      return { error: err };
    }
  };

  const refreshProfile = async () => {
    if (session) {
      await fetchAuthoritativeProfile(session);
    }
  };

  const role: UserRole = profile?.role || 'STUDENT';
  const accountStatus: AccountStatus = profile?.account_status || 'PENDING';

  const hasRole = (...roles: UserRole[]): boolean => {
    if (role === 'SUPER_ADMIN') return true;
    return roles.includes(role);
  };

  const hasPermission = (permission: string): boolean => {
    if (role === 'SUPER_ADMIN') return true;
    return profile?.permissions?.includes(permission) ?? false;
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        session,
        profile,
        isLoading,
        isAuthenticated: !!user,
        role,
        accountStatus,
        login,
        register,
        logout,
        resetPassword,
        refreshProfile,
        hasRole,
        hasPermission,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
