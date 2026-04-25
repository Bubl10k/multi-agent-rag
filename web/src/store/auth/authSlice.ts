import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import { localStorageService } from '@/utils/localStorage';

export type AuthUser = {
  id: string;
  email: string;
};

type AuthState = {
  token: string | null;
  refreshToken: string | null;
  user: AuthUser | null;
};

const initialState: AuthState = {
  token: localStorageService.getAuthToken(),
  refreshToken: localStorageService.getRefreshToken(),
  user: localStorageService.getAuthUser<AuthUser>(),
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials(
      state,
      action: PayloadAction<{ token: string; refreshToken: string; user: AuthUser }>,
    ) {
      state.token = action.payload.token;
      state.refreshToken = action.payload.refreshToken;
      state.user = action.payload.user;
      localStorageService.setAuthToken(action.payload.token);
      localStorageService.setRefreshToken(action.payload.refreshToken);
      localStorageService.setAuthUser(action.payload.user);
    },
    logout(state) {
      state.token = null;
      state.refreshToken = null;
      state.user = null;
      localStorageService.removeAuthToken();
      localStorageService.removeRefreshToken();
      localStorageService.removeAuthUser();
    },
  },
});

export const { setCredentials, logout } = authSlice.actions;
export default authSlice.reducer;