export type CollectionRead = {
  id: string;
  name: string;
  description: string | null;
  embedding_model: string;
};

export type CollectionCreate = {
  name: string;
  description?: string;
  embedding_model?: string;
};

export type CollectionUpdate = {
  name?: string;
  description?: string;
  embedding_model?: string;
};