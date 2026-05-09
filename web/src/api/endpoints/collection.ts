import { baseApi } from '../baseApi';
import type {
  CollectionCreate,
  CollectionRead,
  CollectionUpdate,
} from '../types/collection';

export const collectionApi = baseApi.injectEndpoints({
  endpoints: builder => ({
    getCollections: builder.query<CollectionRead[], void>({
      query: () => '/collections',
      providesTags: result =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'Collection' as const, id })),
              { type: 'Collection', id: 'LIST' },
            ]
          : [{ type: 'Collection', id: 'LIST' }],
    }),
    createCollection: builder.mutation<CollectionRead, CollectionCreate>({
      query: body => ({ url: '/collections', method: 'POST', body }),
      invalidatesTags: [{ type: 'Collection', id: 'LIST' }],
    }),
    updateCollection: builder.mutation<
      CollectionRead,
      { id: string; data: CollectionUpdate }
    >({
      query: ({ id, data }) => ({
        url: `/collections/${id}`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: (_result, _err, { id }) => [
        { type: 'Collection', id },
        { type: 'Collection', id: 'LIST' },
      ],
    }),
    deleteCollection: builder.mutation<CollectionRead, string>({
      query: id => ({ url: `/collections/${id}`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, id) => [
        { type: 'Collection', id },
        { type: 'Collection', id: 'LIST' },
      ],
    }),
  }),
});

export const {
  useGetCollectionsQuery,
  useCreateCollectionMutation,
  useUpdateCollectionMutation,
  useDeleteCollectionMutation,
} = collectionApi;
