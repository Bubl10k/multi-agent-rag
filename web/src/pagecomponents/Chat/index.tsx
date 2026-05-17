import { useEffect, useMemo, useRef, useState } from 'react';
import { useParams, useSearchParams } from 'react-router';
import { Box, Divider, Typography } from '@mui/material';
import { MessageSquare } from 'lucide-react';

import { MessageRole, type Message } from '@/types/chat';
import { useAgentChat } from '@/hooks/useAgentChat';
import { useGetAgentQuery, useUpdateAgentMutation } from '@/api/endpoints/agent';
import { useGetConversationQuery } from '@/api/endpoints/conversation';
import { useGetLLMsQuery } from '@/api/endpoints/llm';
import ChatHeader from '@/components/Chat/ChatHeader';
import ChatMessage from '@/components/Chat/ChatMessage';
import ChatInput from '@/components/Chat/ChatInput';
import ThinkingBubble from '@/components/Chat/ThinkingBubble';

const ChatPage = () => {
  const { agentId } = useParams<{ agentId: string }>();
  const [searchParams] = useSearchParams();
  const conversationId = searchParams.get('conversationId') ?? undefined;

  const { data: agent } = useGetAgentQuery(agentId!, { skip: !agentId });
  const { data: llms } = useGetLLMsQuery();
  const [updateAgent] = useUpdateAgentMutation();

  const [selectedLlmId, setSelectedLlmId] = useState<string | undefined>(
    agent?.llm.id,
  );

  useEffect(() => {
    if (agent?.llm.id && !selectedLlmId) {
      setSelectedLlmId(agent.llm.id);
    }
  }, [agent?.llm.id, selectedLlmId]);

  const handleLlmChange = (llmId: string) => {
    if (!agentId) return;
    setSelectedLlmId(llmId);
    updateAgent({ id: agentId, data: { llm_id: llmId } });
  };

  const { data: existingConversation } = useGetConversationQuery(
    conversationId!,
    {
      skip: !conversationId,
    },
  );

  const initialMessages = useMemo<Message[] | undefined>(() => {
    if (!existingConversation) return undefined;
    return existingConversation.messages.map(m => ({
      id: m.id,
      role: m.role as MessageRole,
      content: m.content,
    }));
  }, [existingConversation]);

  const { messages, streamingContent, isStreaming, sendMessage } = useAgentChat(
    {
      agentId: agentId ?? '',
      initialConversationId: conversationId,
      initialMessages,
    },
  );

  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  const handleSend = () => {
    const text = input.trim();
    if (!text || isStreaming) return;
    sendMessage(text);
    setInput('');
  };

  const streamingMessage: Message | null = streamingContent
    ? {
        id: 'streaming',
        role: MessageRole.Assistant,
        content: streamingContent,
      }
    : null;

  return (
    <Box
      sx={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.default',
      }}
    >
      <ChatHeader agentName={agent?.name} />

      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          px: { xs: 2, sm: 4, md: 8, lg: 18 },
          py: 3,
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {messages.length === 0 && !streamingMessage ? (
          <Box
            sx={{
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 2,
              color: 'text.disabled',
            }}
          >
            <MessageSquare size={40} strokeWidth={1.2} />
            <Typography variant="body2">
              {agent
                ? `Start a conversation with ${agent.name}`
                : 'Start a conversation'}
            </Typography>
          </Box>
        ) : (
          <Box
            sx={{
              maxWidth: 900,
              mx: 'auto',
              display: 'flex',
              flexDirection: 'column',
              gap: 3,
            }}
          >
            {messages.map(message => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isStreaming && !streamingMessage && <ThinkingBubble />}
            {streamingMessage && (
              <ChatMessage message={streamingMessage} isTyping />
            )}
            <div ref={messagesEndRef} />
          </Box>
        )}
      </Box>

      <Divider />

      <ChatInput
        value={input}
        onChange={setInput}
        onSend={handleSend}
        placeholder={agent ? `Message ${agent.name}…` : 'Message…'}
        disabled={isStreaming}
        llms={llms}
        selectedLlmId={selectedLlmId}
        onLlmChange={handleLlmChange}
      />
    </Box>
  );
};

export default ChatPage;
