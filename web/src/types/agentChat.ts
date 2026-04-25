import type { Message } from './chat';

export enum WsMessageType {
  Token = 'token',
  Done = 'done',
  Error = 'error',
}

export type UseAgentChatOptions = {
  agentId: string;
  initialConversationId?: string;
  initialMessages?: Message[];
};

export type UseAgentChatReturn = {
  messages: Message[];
  streamingContent: string;
  isStreaming: boolean;
  conversationId: string | null;
  sendMessage: (text: string) => void;
};

export type WsIncomingDone = {
  done: true;
  conversation_id: string;
};

export type WsIncomingError = {
  error: string;
};