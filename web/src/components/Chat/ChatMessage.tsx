import { Box, Typography } from '@mui/material';
import { MessageRole, type Message } from '@/types/chat';
import ChatAvatar from '@/components/Chat/ChatAvatar';
import MarkdownRenderer from '@/components/MarkdownRenderer';

type Props = {
  message: Message;
  agentName?: string;
};

const ChatMessage = ({ message }: Props) => {
  const isUser = message.role === MessageRole.User;

  return (
    <Box
      sx={{
        display: 'flex',
        gap: 1.5,
        flexDirection: isUser ? 'row-reverse' : 'row',
        alignItems: 'flex-start',
      }}
    >
      <ChatAvatar variant={isUser ? 'user' : 'agent'} />

      <Box
        sx={{
          maxWidth: '80%',
          px: 1.5,
          py: 2,
          borderRadius: isUser ? '16px 4px 16px 16px' : '4px 16px 16px 16px',
          bgcolor: isUser ? 'primary.main' : 'background.paper',
          border: isUser ? 'none' : '1px solid',
          borderColor: 'divider',
        }}
      >
        {isUser ? (
          <Typography
            sx={{
              lineHeight: 1.65,
              color: 'primary.contrastText',
            }}
          >
            {message.content}
          </Typography>
        ) : (
          <MarkdownRenderer>{message.content}</MarkdownRenderer>
        )}
      </Box>
    </Box>
  );
};

export default ChatMessage;
