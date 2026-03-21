import { MessageRole, type Message } from '@/types/chat';

export const MOCK_MESSAGES: Message[] = [
  {
    id: '1',
    role: MessageRole.Assistant,
    content:
      "Hello! I'm the Programming Agent. I can help you with code, architecture, debugging, and technical questions. What would you like to work on?",
  },
  {
    id: '2',
    role: MessageRole.User,
    content: 'Can you help me set up a RAG pipeline in Python?',
  },
  {
    id: '3',
    role: MessageRole.Assistant,
    content:
      'Absolutely! A RAG (Retrieval-Augmented Generation) pipeline typically has three main steps:\n\n\ 1. **Ingestion** — load and chunk your documents\n2. **Retrieval** — embed the query and find relevant chunks via vector search\n3. **Generation** — pass the retrieved context to an LLM to generate a response\n\nWhich part would you like to start with?',
  },
];
