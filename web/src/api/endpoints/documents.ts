import { baseApi } from '../baseApi';
import type {
  CollectionFilesResponse,
  ParsedDocumentResponse,
  UploadDocumentResponse,
} from '../types/documents';

export const documentsApi = baseApi.injectEndpoints({
  endpoints: builder => ({
    getCollectionFiles: builder.query<CollectionFilesResponse, string>({
      query: collectionName =>
        `/documents/files?collection_name=${encodeURIComponent(collectionName)}`,
      providesTags: (_result, _err, collectionName) => [
        { type: 'CollectionFiles', id: collectionName },
      ],
    }),
    uploadDocument: builder.mutation<
      UploadDocumentResponse,
      { collectionName: string; file: File }
    >({
      query: ({ collectionName, file }) => {
        const formData = new FormData();
        formData.append('file', file);
        return {
          url: `/documents/upload?collection_name=${encodeURIComponent(collectionName)}`,
          method: 'POST',
          body: formData,
        };
      },
      invalidatesTags: (_result, _err, { collectionName }) => [
        { type: 'CollectionFiles', id: collectionName },
      ],
    }),
    parseDocument: builder.mutation<ParsedDocumentResponse, File>({
      query: file => {
        const formData = new FormData();
        formData.append('file', file);
        return {
          url: '/documents/parse',
          method: 'POST',
          body: formData,
        };
      },
    }),
  }),
});

export const {
  useGetCollectionFilesQuery,
  useUploadDocumentMutation,
  useParseDocumentMutation,
} = documentsApi;
