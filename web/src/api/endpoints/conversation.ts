import { baseApi } from '../baseApi';
import type {
  ConversationRead,
  ConversationsListParams,
} from '../types/conversation';

export const conversationApi = baseApi.injectEndpoints({
  endpoints: builder => ({
    getConversations: builder.query<
      ConversationRead[],
      ConversationsListParams | void
    >({
      query: params => ({
        url: '/conversations',
        params: params ?? {},
      }),
      providesTags: result =>
        result
          ? [
              ...result.map(({ id }) => ({
                type: 'Conversation' as const,
                id,
              })),
              { type: 'Conversation', id: 'LIST' },
            ]
          : [{ type: 'Conversation', id: 'LIST' }],
    }),
    getConversation: builder.query<ConversationRead, string>({
      query: id => `/conversations/${id}`,
      providesTags: (_result, _err, id) => [{ type: 'Conversation', id }],
    }),
    deleteConversation: builder.mutation<void, string>({
      query: id => ({ url: `/conversations/${id}`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, id) => [
        { type: 'Conversation', id },
        { type: 'Conversation', id: 'LIST' },
      ],
    }),
  }),
});

export const {
  useGetConversationsQuery,
  useGetConversationQuery,
  useDeleteConversationMutation,
} = conversationApi;
