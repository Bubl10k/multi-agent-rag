import { baseApi } from '../baseApi';
import type { LLMCreate, LLMRead, LLMUpdate } from '../types/llm';

export const llmApi = baseApi.injectEndpoints({
  endpoints: builder => ({
    getLLMs: builder.query<LLMRead[], void>({
      query: () => '/llms',
      providesTags: result =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'LLM' as const, id })),
              { type: 'LLM', id: 'LIST' },
            ]
          : [{ type: 'LLM', id: 'LIST' }],
    }),
    createLLM: builder.mutation<LLMRead, LLMCreate>({
      query: body => ({ url: '/llms', method: 'POST', body }),
      invalidatesTags: [{ type: 'LLM', id: 'LIST' }],
    }),
    updateLLM: builder.mutation<LLMRead, { id: string; data: LLMUpdate }>({
      query: ({ id, data }) => ({ url: `/llms/${id}`, method: 'PATCH', body: data }),
      invalidatesTags: (_result, _err, { id }) => [
        { type: 'LLM', id },
        { type: 'LLM', id: 'LIST' },
      ],
    }),
    deleteLLM: builder.mutation<LLMRead, string>({
      query: id => ({ url: `/llms/${id}`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, id) => [
        { type: 'LLM', id },
        { type: 'LLM', id: 'LIST' },
      ],
    }),
  }),
});

export const {
  useGetLLMsQuery,
  useCreateLLMMutation,
  useUpdateLLMMutation,
  useDeleteLLMMutation,
} = llmApi;