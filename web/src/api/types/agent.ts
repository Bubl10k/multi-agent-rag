import type { LLMRead } from './llm';
import type { CollectionRead } from './collection';

export enum AgentType {
  GENERAL = 'general',
  PROGRAMMING = 'programming',
  MATH = 'math',
  RESEARCHER = 'researcher',
  INVOICE = 'invoice',
}

export type AgentRead = {
  id: string;
  name: string;
  prompt: string;
  agent_type: AgentType;
  agent_config: Record<string, unknown>;
  is_active: boolean;
  user_id: string;
  llm: LLMRead;
  collections: CollectionRead[];
};

export type AgentCreate = {
  name: string;
  prompt: string;
  llm_id: string;
  agent_type?: AgentType;
  agent_config?: Record<string, unknown>;
  collection_ids?: string[];
  is_active?: boolean;
};

export type AgentUpdate = {
  name?: string;
  prompt?: string;
  llm_id?: string;
  agent_type?: AgentType;
  agent_config?: Record<string, unknown>;
  collection_ids?: string[];
  is_active?: boolean;
};

export type AgentsListParams = {
  page?: number;
  limit?: number;
};

export type AgentDefaultPrompt = {
  agent_type: AgentType;
  content: string;
};

export type GraphNode = {
  id: string;
  name: string;
};

export type GraphEdge = {
  source: string;
  target: string;
  data: string | null;
  conditional: boolean;
};

export type AgentGraphJSON = {
  nodes: GraphNode[];
  edges: GraphEdge[];
};