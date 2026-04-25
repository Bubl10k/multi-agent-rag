import type { LLMRead } from './llm';
import type { CollectionRead } from './collection';

export type AgentRead = {
  id: string;
  name: string;
  prompt: string;
  tool_calls: unknown[];
  is_active: boolean;
  llm: LLMRead;
  collections: CollectionRead[];
};

export type AgentCreate = {
  name: string;
  prompt: string;
  llm_id: string;
  tool_calls?: unknown[];
  collection_ids?: string[];
  is_active?: boolean;
};

export type AgentUpdate = {
  name?: string;
  prompt?: string;
  llm_id?: string;
  tool_calls?: unknown[];
  collection_ids?: string[];
  is_active?: boolean;
};

export type AgentsListParams = {
  page?: number;
  limit?: number;
};