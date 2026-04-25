export const ROUTES = {
  HOME: '/',
  CHAT: '/chat/:agentId',
  LOGIN: '/login',
  REGISTER: '/register',
} as const;

export const chatPath = (agentId: string) => `/chat/${agentId}`;
export const conversationChatPath = (agentId: string, conversationId: string) =>
  `/chat/${agentId}?conversationId=${conversationId}`;