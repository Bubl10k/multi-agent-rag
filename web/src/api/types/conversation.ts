import type { MessageRole } from '@/types/chat';

export type MessageRead = {
  id: string;
  role: MessageRole;
  content: string;
  created_at: string;
};

export type ConversationRead = {
  id: string;
  agent_id: string;
  user_id: string;
  created_at: string;
  messages: MessageRead[];
};

export type ConversationsListParams = {
  page?: number;
  limit?: number;
};