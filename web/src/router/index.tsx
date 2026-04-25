import { Suspense } from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router';

import { ROUTES } from './router';
import ProtectedRoute from './ProtectedRoute';
import LoadingScreen from '@/components/LoadingScreen';
import Layout from '@/components/Layout';

const router = createBrowserRouter([
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <Layout />,
        children: [
          {
            path: ROUTES.HOME,
            lazy: async () => {
              const { default: Component } =
                await import('@/pagecomponents/Home');
              return { Component };
            },
          },
          {
            path: ROUTES.CHAT,
            lazy: async () => {
              const { default: Component } =
                await import('@/pagecomponents/Chat');
              return { Component };
            },
          },
          {
            path: '*',
            lazy: async () => {
              const { default: Component } =
                await import('@/pagecomponents/NotFound');
              return { Component };
            },
          },
        ],
      },
    ],
  },
  {
    path: ROUTES.LOGIN,
    lazy: async () => {
      const { default: Component } =
        await import('@/pagecomponents/Auth/Login');
      return { Component };
    },
  },
  {
    path: ROUTES.REGISTER,
    lazy: async () => {
      const { default: Component } =
        await import('@/pagecomponents/Auth/Register');
      return { Component };
    },
  },
]);

export const AppRouter = () => (
  <Suspense fallback={<LoadingScreen />}>
    <RouterProvider router={router} />
  </Suspense>
);
