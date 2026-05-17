import { createApi, fetchBaseQuery, type BaseQueryFn, type FetchArgs, type FetchBaseQueryError } from '@reduxjs/toolkit/query/react';
import type { RootState } from '@/store';
import { logout, setCredentials } from '@/store/auth/authSlice';
import { localStorageService } from '@/utils/localStorage';
import type { TokenResponse } from './types/auth';

const baseQuery = fetchBaseQuery({
  baseUrl: import.meta.env.VITE_API_BASE_URL ?? '/api',
  prepareHeaders: (headers, { getState }) => {
    const token = (getState() as RootState).auth.token;
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
    return headers;
  },
});

const baseQueryWithReauth: BaseQueryFn<string | FetchArgs, unknown, FetchBaseQueryError> = async (
  args,
  api,
  extraOptions,
) => {
  let result = await baseQuery(args, api, extraOptions);

  if (result.error?.status === 401) {
    const refreshToken = localStorageService.getRefreshToken();

    if (refreshToken) {
      const refreshResult = await baseQuery(
        { url: '/auth/refresh', method: 'POST', body: { refresh_token: refreshToken } },
        api,
        extraOptions,
      );

      if (refreshResult.data) {
        const { access_token, refresh_token } = refreshResult.data as TokenResponse;
        const user = (api.getState() as RootState).auth.user!;
        api.dispatch(setCredentials({ token: access_token, refreshToken: refresh_token, user }));
        result = await baseQuery(args, api, extraOptions);
      } else {
        api.dispatch(logout());
      }
    } else {
      api.dispatch(logout());
    }
  }

  return result;
};

export const baseApi = createApi({
  reducerPath: 'api',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['Agent', 'Conversation', 'LLM', 'Collection', 'CollectionFiles'],
  endpoints: () => ({}),
});