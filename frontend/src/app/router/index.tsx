import { createBrowserRouter, Navigate } from 'react-router-dom';
import { RootLayout } from '@/app/layouts/root-layout';
import { ProtectedRoute } from '@/app/router/protected-route';

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
  // Public Authentication Routes
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

  // Main Application Shell
  {
    path: '/',
    element: <RootLayout />,
    children: [
      {
        index: true,
        element: <DashboardPage />,
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
        path: 'academic-risk',
        element: (
          <ProtectedRoute allowedRoles={['STUDENT', 'FACULTY', 'INSTITUTION_ADMIN', 'SUPER_ADMIN']}>
            <AcademicRiskPage />
          </ProtectedRoute>
        ),
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
        path: 'diagnostics',
        element: (
          <ProtectedRoute allowedRoles={['INSTITUTION_ADMIN', 'SUPER_ADMIN']}>
            <DiagnosticsPage />
          </ProtectedRoute>
        ),
      },
      {
        path: '*',
        element: <Navigate to="/" replace />,
      },
    ],
  },
]);
