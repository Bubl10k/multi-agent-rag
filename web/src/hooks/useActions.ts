import { useMemo } from 'react';
import { useDispatch } from 'react-redux';
import { bindActionCreators } from '@reduxjs/toolkit';
import type { AppDispatch } from '@/store';
import { setCredentials, logout } from '@/store/auth/authSlice';

const authActions = { setCredentials, logout };

export const useActions = () => {
  const dispatch = useDispatch<AppDispatch>();
  return useMemo(() => bindActionCreators(authActions, dispatch), [dispatch]);
};
