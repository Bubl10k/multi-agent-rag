export type UploadDocumentResponse = {
  collection: string;
  chunks_stored: number;
};

export type CollectionFilesResponse = {
  collection: string;
  files: string[];
};

export type ParsedDocumentResponse = {
  filename: string;
  content: string;
};