import { createBrowserRouter, Navigate } from 'react-router-dom';
import { PublicLayout } from '@/app/layouts/public-layout';
import { RootLayout } from '@/app/layouts/root-layout';
import { ProtectedRoute } from '@/app/router/protected-route';

// Public Website Pages
import { LandingPage } from '@/features/landing/landing-page';
import { ProblemPage } from '@/features/public-pages/problem-page';
import { SolutionPage } from '@/features/public-pages/solution-page';
import { ModulesOverviewPage } from '@/features/public-pages/modules-overview-page';
import { ModuleDetailPage } from '@/features/public-pages/module-detail-page';
import { ArchitecturePage } from '@/features/public-pages/architecture-page';
import { DifferentiatorsPage } from '@/features/public-pages/differentiators-page';
import { RolesPage } from '@/features/public-pages/roles-page';
import { NotFoundPage } from '@/features/not-found/not-found-page';

// Auth Pages
import { LoginPage } from '@/features/auth/login-page';
import { RegisterPage } from '@/features/auth/register-page';
import { ForgotPasswordPage } from '@/features/auth/forgot-password-page';
import { UnauthorizedPage } from '@/features/auth/unauthorized-page';

// Core Dashboard & Modules
import { DashboardPage } from '@/features/dashboard/dashboard-page';
import { AcademicDataPage } from '@/features/academic-data';
import { SyllabusPage } from '@/features/syllabus';
import { AssessmentPage } from '@/features/assessments';
import { MasteryPage } from '@/features/mastery';
import { AcademicRiskPage } from '@/features/academic-risk';
import { InterventionPage } from '@/features/interventions';
import { CareerReadinessPage } from '@/features/career-readiness';
import { DiagnosticsPage } from '@/features/diagnostics';

export const router = createBrowserRouter([
  // 1. Public Product Website (wrapped by PublicLayout with topbar and institutional footer)
  {
    path: '/',
    element: <PublicLayout />,
    children: [
      {
        index: true,
        element: <LandingPage />,
      },
      {
        path: 'problem',
        element: <ProblemPage />,
      },
      {
        path: 'solution',
        element: <SolutionPage />,
      },
      {
        path: 'modules',
        element: <ModulesOverviewPage />,
      },
      {
        path: 'modules/:moduleSlug',
        element: <ModuleDetailPage />,
      },
      {
        path: 'architecture',
        element: <ArchitecturePage />,
      },
      {
        path: 'differentiators',
        element: <DifferentiatorsPage />,
      },
      {
        path: 'roles',
        element: <RolesPage />,
      },
    ],
  },

  // Public Redirects & Aliases
  {
    path: '/platform',
    element: <Navigate to="/" replace />,
  },
  {
    path: '/demo-guide',
    element: <Navigate to="/app" replace />,
  },

  // 2. Public Authentication Routes
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/register',
    element: <RegisterPage />,
  },
  {
    path: '/forgot-password',
    element: <ForgotPasswordPage />,
  },
  {
    path: '/unauthorized',
    element: <UnauthorizedPage />,
  },

  // 3. Main Workspace Application Shell under /app/ (Clean RootLayout with no demo banners)
  {
    path: '/app',
    element: <RootLayout />,
    children: [
      {
        index: true,
        element: <Navigate to="/app/dashboard" replace />,
      },
      {
        path: 'dashboard',
        element: (
          <ProtectedRoute allowedRoles={['STUDENT', 'FACULTY', 'INSTITUTION_ADMIN', 'PLACEMENT_OFFICER', 'SUPER_ADMIN']}>
            <DashboardPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'academic-data',
        element: (
          <ProtectedRoute allowedRoles={['STUDENT', 'FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN']}>
            <AcademicDataPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'syllabus',
        element: (
          <ProtectedRoute allowedRoles={['STUDENT', 'FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN']}>
            <SyllabusPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'assessments',
        element: (
          <ProtectedRoute allowedRoles={['STUDENT', 'FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN']}>
            <AssessmentPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'mastery',
        element: (
          <ProtectedRoute allowedRoles={['STUDENT', 'FACULTY', 'PLACEMENT_OFFICER', 'INSTITUTION_ADMIN', 'SUPER_ADMIN']}>
            <MasteryPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'risk',
        element: (
          <ProtectedRoute allowedRoles={['STUDENT', 'FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN']}>
            <AcademicRiskPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'academic-risk',
        element: <Navigate to="/app/risk" replace />,
      },
      {
        path: 'interventions',
        element: (
          <ProtectedRoute allowedRoles={['STUDENT', 'FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN']}>
            <InterventionPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'career-readiness',
        element: (
          <ProtectedRoute allowedRoles={['STUDENT', 'PLACEMENT_OFFICER', 'FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN']}>
            <CareerReadinessPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'career',
        element: <Navigate to="/app/career-readiness" replace />,
      },
      {
        path: 'diagnostics',
        element: (
          <ProtectedRoute allowedRoles={['INSTITUTION_ADMIN', 'SUPER_ADMIN']}>
            <DiagnosticsPage />
          </ProtectedRoute>
        ),
      },
    ],
  },

  // Backward-Compatible Top-Level Direct Route Redirects
  {
    path: '/dashboard',
    element: <Navigate to="/app/dashboard" replace />,
  },
  {
    path: '/dashboard/*',
    element: <Navigate to="/app/dashboard" replace />,
  },
  {
    path: '/academic-data',
    element: <Navigate to="/app/academic-data" replace />,
  },
  {
    path: '/syllabus',
    element: <Navigate to="/app/syllabus" replace />,
  },
  {
    path: '/assessments',
    element: <Navigate to="/app/assessments" replace />,
  },
  {
    path: '/mastery',
    element: <Navigate to="/app/mastery" replace />,
  },
  {
    path: '/academic-risk',
    element: <Navigate to="/app/risk" replace />,
  },
  {
    path: '/risk',
    element: <Navigate to="/app/risk" replace />,
  },
  {
    path: '/interventions',
    element: <Navigate to="/app/interventions" replace />,
  },
  {
    path: '/career-readiness',
    element: <Navigate to="/app/career-readiness" replace />,
  },
  {
    path: '/career',
    element: <Navigate to="/app/career-readiness" replace />,
  },
  {
    path: '/diagnostics',
    element: <Navigate to="/app/diagnostics" replace />,
  },

  // 404 Catch-All
  {
    path: '*',
    element: <NotFoundPage />,
  },
]);
