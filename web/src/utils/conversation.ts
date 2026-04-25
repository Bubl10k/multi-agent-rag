import type { ConversationRead } from '@/api/types/conversation';
import { MessageRole } from '@/types/chat';

export const GROUP_ORDER = ['Today', 'Yesterday', 'Older'] as const;

export const getConversationPreview = (conversation: ConversationRead): string => {
  const firstUserMsg = conversation.messages.find(m => m.role === MessageRole.User);
  const text = firstUserMsg?.content ?? 'New conversation';
  return text.length > 38 ? text.slice(0, 38) + '…' : text;
};

export const groupConversationsByDate = (
  conversations: ConversationRead[],
): Record<string, ConversationRead[]> => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);

  return conversations.reduce<Record<string, ConversationRead[]>>((acc, conv) => {
    const date = new Date(conv.created_at);
    date.setHours(0, 0, 0, 0);
    let group: string;
    if (date.getTime() === today.getTime()) group = 'Today';
    else if (date.getTime() === yesterday.getTime()) group = 'Yesterday';
    else group = 'Older';
    (acc[group] ??= []).push(conv);
    return acc;
  }, {});
};