import React from 'react';
import { RouterProvider } from 'react-router-dom';
import { router } from '@/app/router';
import { QueryProvider } from '@/app/providers/query-provider';
import { AuthProvider } from '@/context/auth-context';

export const App: React.FC = () => {
  return (
    <QueryProvider>
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
    </QueryProvider>
  );
};

export default App;
