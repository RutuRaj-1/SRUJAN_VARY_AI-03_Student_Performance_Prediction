export type UserRole =
  | 'SUPER_ADMIN'
  | 'INSTITUTION_ADMIN'
  | 'STUDENT'
  | 'FACULTY'
  | 'PLACEMENT_OFFICER';

export type AccountStatus = 'PENDING' | 'ACTIVE' | 'SUSPENDED' | 'DISABLED';

export interface UserProfile {
  user_id: string;
  email: string;
  full_name: string;
  role: UserRole;
  account_status: AccountStatus;
  institution_id?: string | null;
  permissions: string[];
}

export interface AuthState {
  user: any | null;
  session: any | null;
  profile: UserProfile | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}
