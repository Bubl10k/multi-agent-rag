import { baseApi } from '../baseApi';
import type { PlatformLLMRead } from '../types/platform_llm';

export const platformLlmApi = baseApi.injectEndpoints({
  endpoints: builder => ({
    getPlatformLLMs: builder.query<PlatformLLMRead[], void>({
      query: () => '/platform-llms',
      providesTags: [{ type: 'PlatformLLM', id: 'LIST' }],
    }),
  }),
});

export const { useGetPlatformLLMsQuery } = platformLlmApi;