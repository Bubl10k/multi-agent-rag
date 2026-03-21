import { useEffect, useRef, useState } from 'react';
import { Box, Divider } from '@mui/material';
import { MOCK_AGENTS } from '@/mocks/agents';
import { MOCK_MESSAGES } from '@/mocks/messages';
import { type Message, MessageRole } from '@/types/chat';
import ChatHeader from '@/components/Chat/ChatHeader';
import ChatMessage from '@/components/Chat/ChatMessage';
import ChatInput from '@/components/Chat/ChatInput';

const MOCK_AGENT = MOCK_AGENTS[0];

const ChatPage = () => {
  const [messages, setMessages] = useState<Message[]>(MOCK_MESSAGES);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: MessageRole.User,
      content: trimmed,
    };
    const mockReply: Message = {
      id: (Date.now() + 1).toString(),
      role: MessageRole.Assistant,
      content:
        'I received your message. This is a mocked response — real API integration coming soon.',
    };

    setMessages(prev => [...prev, userMessage, mockReply]);
    setInput('');
  };

  return (
    <Box
      sx={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.default',
      }}
    >
      <ChatHeader agent={MOCK_AGENT} />

      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          px: { xs: 2, sm: 4, md: 8, lg: 16 },
          py: 3,
        }}
      >
        <Box
          sx={{
            maxWidth: 760,
            mx: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: 3,
          }}
        >
          {messages.map(message => (
            <ChatMessage
              key={message.id}
              message={message}
              agentIcon={MOCK_AGENT.Icon}
            />
          ))}
          <div ref={messagesEndRef} />
        </Box>
      </Box>

      <Divider />

      <ChatInput
        value={input}
        onChange={setInput}
        onSend={handleSend}
        placeholder={`Message ${MOCK_AGENT.label}...`}
      />
    </Box>
  );
};

export default ChatPage;
