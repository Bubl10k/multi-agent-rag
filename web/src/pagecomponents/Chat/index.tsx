import { useEffect, useMemo, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams, useSearchParams } from 'react-router';
import { Box, Divider, Typography } from '@mui/material';
import { MessageSquare } from 'lucide-react';

import { MessageRole, type Message } from '@/types/chat';
import { useAgentChat } from '@/hooks/useAgentChat';
import {
  useGetAgentQuery,
  useUpdateAgentMutation,
} from '@/api/endpoints/agent';
import { useGetConversationQuery } from '@/api/endpoints/conversation';
import { useParseDocumentMutation } from '@/api/endpoints/documents';
import { useGetLLMsQuery } from '@/api/endpoints/llm';
import { useGetPlatformLLMsQuery } from '@/api/endpoints/platform_llm';
import { parseLLMSelection } from '@/validation/agent';
import ChatHeader from '@/components/Chat/ChatHeader';
import ChatMessage from '@/components/Chat/ChatMessage';
import ChatInput from '@/components/Chat/ChatInput';
import ThinkingBubble from '@/components/Chat/ThinkingBubble';

const ChatPage = () => {
  const { t } = useTranslation();
  const { agentId } = useParams<{ agentId: string }>();
  const [searchParams] = useSearchParams();
  const conversationId = searchParams.get('conversationId') ?? undefined;

  const { data: agent } = useGetAgentQuery(agentId!, { skip: !agentId });
  const { data: llms } = useGetLLMsQuery();
  const { data: platformLlms } = useGetPlatformLLMsQuery();
  const [updateAgent] = useUpdateAgentMutation();

  const initialSelection = agent?.platform_llm
    ? `platform:${agent.platform_llm.id}`
    : agent?.llm
      ? `user:${agent.llm.id}`
      : undefined;

  const [selectedLlmSelection, setSelectedLlmSelection] = useState<
    string | undefined
  >(initialSelection);

  useEffect(() => {
    if (initialSelection && !selectedLlmSelection) {
      setSelectedLlmSelection(initialSelection);
    }
  }, [initialSelection, selectedLlmSelection]);

  const handleLlmChange = (selection: string) => {
    if (!agentId) return;
    setSelectedLlmSelection(selection);
    updateAgent({ id: agentId, data: parseLLMSelection(selection) });
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

  const {
    messages,
    streamingContent,
    isStreaming,
    sendMessage,
    stopStreaming,
  } = useAgentChat({
    agentId: agentId ?? '',
    initialConversationId: conversationId,
    initialMessages,
  });

  const [parseDocument, { isLoading: isAttaching }] = useParseDocumentMutation();
  const [attachedFile, setAttachedFile] = useState<{ name: string; content: string } | null>(null);

  const handleAttach = async (file: File) => {
    const result = await parseDocument(file).unwrap();
    setAttachedFile({ name: result.filename, content: result.content });
  };

  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  const handleSend = () => {
    const text = input.trim();
    if ((!text && !attachedFile) || isStreaming) return;
    const message = attachedFile
      ? `[File: ${attachedFile.name}]\n${attachedFile.content}${text ? `\n\n${text}` : ''}`
      : text;
    sendMessage(message);
    setInput('');
    setAttachedFile(null);
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
                ? t('chat.startConversationWith', { name: agent.name })
                : t('chat.startConversation')}
            </Typography>
          </Box>
        ) : (
          <Box
            sx={{
              maxWidth: 900,
              minWidth: 700,
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
        onStop={stopStreaming}
        placeholder={agent ? t('chat.messagePlaceholderWith', { name: agent.name }) : t('chat.messagePlaceholder')}
        disabled={isStreaming}
        llms={llms}
        platformLlms={platformLlms}
        selectedLlmSelection={selectedLlmSelection}
        onLlmChange={handleLlmChange}
        attachedFileName={attachedFile?.name}
        onAttach={handleAttach}
        onRemoveAttachment={() => setAttachedFile(null)}
        isAttaching={isAttaching}
      />
    </Box>
  );
};

export default ChatPage;
