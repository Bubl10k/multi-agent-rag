export type UploadDocumentResponse = {
  collection: string;
  chunks_stored: number;
};

export type CollectionFilesResponse = {
  collection: string;
  files: string[];
};