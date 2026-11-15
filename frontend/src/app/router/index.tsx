import { createBrowserRouter, Navigate } from 'react-router-dom';
import { RootLayout } from '@/app/layouts/root-layout';
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
        element: <AcademicDataPage />,
      },
      {
        path: 'syllabus',
        element: <SyllabusPage />,
      },
      {
        path: 'assessments',
        element: <AssessmentPage />,
      },
      {
        path: 'mastery',
        element: <MasteryPage />,
      },
      {
        path: 'academic-risk',
        element: <AcademicRiskPage />,
      },
      {
        path: 'interventions',
        element: <InterventionPage />,
      },
      {
        path: 'career-readiness',
        element: <CareerReadinessPage />,
      },
      {
        path: 'diagnostics',
        element: <DiagnosticsPage />,
      },
      {
        path: '*',
        element: <Navigate to="/" replace />,
      },
    ],
  },
]);
