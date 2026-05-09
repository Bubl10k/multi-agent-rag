import { baseApi } from '../baseApi';
import type {
  LoginRequest,
  TokenResponse,
  RegisterRequest,
  UserResponse,
} from '../types/auth';

export const authApi = baseApi.injectEndpoints({
  endpoints: builder => ({
    login: builder.mutation<TokenResponse, LoginRequest>({
      query: ({ email, password }) => {
        const body = new URLSearchParams();
        body.append('username', email);
        body.append('password', password);
        return {
          url: '/auth/login',
          method: 'POST',
          body,
        };
      },
    }),
    register: builder.mutation<UserResponse, RegisterRequest>({
      query: body => ({
        url: '/auth/register',
        method: 'POST',
        body,
      }),
    }),
    refresh: builder.mutation<TokenResponse, { refresh_token: string }>({
      query: body => ({
        url: '/auth/refresh',
        method: 'POST',
        body,
      }),
    }),
    logout: builder.mutation<void, { refresh_token: string }>({
      query: body => ({
        url: '/auth/logout',
        method: 'POST',
        body,
      }),
    }),
    getMe: builder.query<UserResponse, void>({
      query: () => '/users/me',
    }),
  }),
});

export const {
  useLoginMutation,
  useRegisterMutation,
  useRefreshMutation,
  useLogoutMutation,
  useGetMeQuery,
} = authApi;
