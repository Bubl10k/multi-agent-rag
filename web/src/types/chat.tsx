import type { LucideIcon } from 'lucide-react';

export type Agent = {
  id: string;
  label: string;
  Icon: LucideIcon;
};

export enum MessageRole {
  User = 'user',
  Assistant = 'assistant',
  Tool = 'tool',
}

export type Message = {
  id: string;
  role: MessageRole;
  content: string;
};

export type Session = {
  id: string;
  title: string;
  group: string;
  agentId: string;
};
