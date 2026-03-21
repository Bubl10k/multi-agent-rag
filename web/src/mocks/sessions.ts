import type { Session } from '@/types/chat.tsx';

export const MOCK_SESSIONS: Session[] = [
  {
    id: '1',
    title: 'RAG pipeline setup',
    group: 'Today',
    agentId: 'programming',
  },
  {
    id: '2',
    title: 'Document ingestion question',
    group: 'Today',
    agentId: 'research',
  },
  {
    id: '3',
    title: 'Agent configuration help',
    group: 'Yesterday',
    agentId: 'general',
  },
  {
    id: '4',
    title: 'Vector store optimization',
    group: 'Yesterday',
    agentId: 'programming',
  },
  {
    id: '5',
    title: 'Embedding model comparison',
    group: 'Previous 7 Days',
    agentId: 'research',
  },
  {
    id: '6',
    title: 'Multi-agent orchestration',
    group: 'Previous 7 Days',
    agentId: 'general',
  },
];
