import { BookOpen, Bot, Calculator, Code2, PenLine } from 'lucide-react';
import type { Agent } from '@/types/chat.tsx';

export const MOCK_AGENTS: Agent[] = [
  { id: 'programming', label: 'Programming Agent', Icon: Code2 },
  { id: 'math', label: 'Math Agent', Icon: Calculator },
  { id: 'research', label: 'Research Agent', Icon: BookOpen },
  { id: 'writing', label: 'Writing Agent', Icon: PenLine },
  { id: 'general', label: 'General Agent', Icon: Bot },
];
