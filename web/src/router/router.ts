export const ROUTES = {
  HOME: '/',
  CHAT: '/chat/:agentId',
  AGENTS: '/agents',
  LLM_MODELS: '/llm-models',
  COLLECTIONS: '/collections',
  LOGIN: '/login',
  REGISTER: '/register',
} as const;

export const chatPath = (agentId: string) => `/chat/${agentId}`;
export const conversationChatPath = (agentId: string, conversationId: string) =>
  `/chat/${agentId}?conversationId=${conversationId}`;
