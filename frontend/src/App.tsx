import React from 'react';
import { RouterProvider } from 'react-router-dom';
import { router } from '@/app/router';
import { QueryProvider } from '@/app/providers/query-provider';
import { AuthProvider } from '@/context/auth-context';
import { DemoProvider } from '@/demo/demo-context';

export const App: React.FC = () => {
  return (
    <QueryProvider>
      <AuthProvider>
        <DemoProvider>
          <RouterProvider router={router} />
        </DemoProvider>
      </AuthProvider>
    </QueryProvider>
  );
};

export default App;
