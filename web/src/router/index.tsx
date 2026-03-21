import { Suspense } from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router';

import { ROUTES } from './router';
import LoadingScreen from '@/components/LoadingScreen';
import Layout from '@/components/Layout';

const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      {
        path: ROUTES.HOME,
        lazy: async () => {
          const { default: Component } = await import('@/pagecomponents/Chat');
          return { Component };
        },
      },
    ],
  },
]);

export const AppRouter = () => (
  <Suspense fallback={<LoadingScreen />}>
    <RouterProvider router={router} />
  </Suspense>
);
