import MuiMarkdown from 'mui-markdown';
import { Box, Typography } from '@mui/material';
import type { LucideIcon } from 'lucide-react';
import { MessageRole, type Message } from '@/types/chat';
import ChatAvatar from '@/components/Chat/ChatAvatar.tsx';

type Props = {
  message: Message;
  agentIcon: LucideIcon;
};

const ChatMessage = ({ message, agentIcon }: Props) => {
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
      {isUser ? <ChatAvatar /> : <ChatAvatar icon={agentIcon} />}

      <Box
        sx={{
          maxWidth: '80%',
          px: 1.5,
          py: 1,
          borderRadius: isUser ? '16px 4px 16px 16px' : '4px 16px 16px 16px',
          bgcolor: isUser ? 'primary.main' : 'background.paper',
          border: isUser ? 'none' : '1px solid',
          borderColor: 'divider',
        }}
      >
        {isUser ? (
          <Typography sx={{ fontSize: '0.9rem', lineHeight: 1.65, color: 'primary.contrastText' }}>
            {message.content}
          </Typography>
        ) : (
          <MuiMarkdown>{message.content}</MuiMarkdown>
        )}
      </Box>
    </Box>
  );
};

export default ChatMessage;