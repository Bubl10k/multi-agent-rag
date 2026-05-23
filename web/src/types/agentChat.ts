import type { Message } from './chat';

export enum WsMessageType {
  Token = 'token',
  Done = 'done',
  Stopped = 'stopped',
  Error = 'error',
  Stop = 'stop',
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
  stopStreaming: () => void;
};

export type WsIncomingDone = {
  done: true;
  conversation_id: string;
};

export type WsIncomingStop = {
  stopped: true;
  conversation_id: string;
};

export type WsIncomingError = {
  error: string;
};