import { Box, Typography } from '@mui/material';
import { keyframes } from '@mui/system';
import { MessageRole, type Message } from '@/types/chat';
import ChatAvatar from '@/components/Chat/ChatAvatar';
import MarkdownRenderer from '@/components/MarkdownRenderer';

const blink = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
`;

type Props = {
  message: Message;
  agentName?: string;
  isTyping?: boolean;
};

const ChatMessage = ({ message, isTyping }: Props) => {
  const isUser = message.role === MessageRole.User;
  const isError = message.role === MessageRole.Error;

  if (isError) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
        }}
      >
        <Typography
          variant="body2"
          sx={{
            px: 2,
            py: 1,
            borderRadius: 2,
            bgcolor: 'error.main',
            color: 'error.contrastText',
            maxWidth: '80%',
          }}
        >
          {message.content}
        </Typography>
      </Box>
    );
  }

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
          <>
            <MarkdownRenderer>{message.content}</MarkdownRenderer>
            {isTyping && (
              <Box
                sx={{
                  width: 16,
                  height: 2,
                  borderRadius: 1,
                  bgcolor: 'text.disabled',
                  mt: 0.75,
                  animation: `${blink} 1s step-end infinite`,
                }}
              />
            )}
          </>
        )}
      </Box>
    </Box>
  );
};

export default ChatMessage;
