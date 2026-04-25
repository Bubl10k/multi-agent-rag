import { Navigate, Outlet } from 'react-router';
import { useAppSelector } from '@/store';
import { ROUTES } from './router';

const ProtectedRoute = () => {
  const token = useAppSelector(state => state.auth.token);
  return token ? <Outlet /> : <Navigate to={ROUTES.LOGIN} replace />;
};

export default ProtectedRoute;
