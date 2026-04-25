import { baseApi } from '../baseApi';
import type {
  AgentCreate,
  AgentRead,
  AgentUpdate,
  AgentsListParams,
} from '../types/agent';

export const agentApi = baseApi.injectEndpoints({
  endpoints: builder => ({
    getAgents: builder.query<AgentRead[], AgentsListParams | void>({
      query: params => ({
        url: '/agents',
        params: params ?? {},
      }),
      providesTags: result =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'Agent' as const, id })),
              { type: 'Agent', id: 'LIST' },
            ]
          : [{ type: 'Agent', id: 'LIST' }],
    }),
    getAgent: builder.query<AgentRead, string>({
      query: id => `/agents/${id}`,
      providesTags: (_result, _err, id) => [{ type: 'Agent', id }],
    }),
    createAgent: builder.mutation<AgentRead, AgentCreate>({
      query: body => ({ url: '/agents', method: 'POST', body }),
      invalidatesTags: [{ type: 'Agent', id: 'LIST' }],
    }),
    updateAgent: builder.mutation<AgentRead, { id: string; data: AgentUpdate }>(
      {
        query: ({ id, data }) => ({
          url: `/agents/${id}`,
          method: 'PATCH',
          body: data,
        }),
        invalidatesTags: (_result, _err, { id }) => [
          { type: 'Agent', id },
          { type: 'Agent', id: 'LIST' },
        ],
      },
    ),
    deleteAgent: builder.mutation<AgentRead, string>({
      query: id => ({ url: `/agents/${id}`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, id) => [
        { type: 'Agent', id },
        { type: 'Agent', id: 'LIST' },
      ],
    }),
  }),
});

export const {
  useGetAgentsQuery,
  useGetAgentQuery,
  useCreateAgentMutation,
  useUpdateAgentMutation,
  useDeleteAgentMutation,
} = agentApi;
