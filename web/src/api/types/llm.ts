export type LLMRead = {
  id: string;
  model_name: string;
  is_active: boolean;
  user_id: string;
};

export type LLMCreate = {
  model_name: string;
  api_key: string;
  is_active?: boolean;
};

export type LLMUpdate = {
  model_name?: string;
  api_key?: string;
  is_active?: boolean;
};