import { Box } from '@mui/material';
import { keyframes } from '@mui/system';
import ChatAvatar from '@/components/Chat/ChatAvatar';

const bounce = keyframes`
  0%, 80%, 100% { transform: translateY(0); opacity: 0.35; }
  40% { transform: translateY(-5px); opacity: 1; }
`;

const ThinkingBubble = () => (
  <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'flex-start' }}>
    <ChatAvatar variant="agent" />
    <Box
      sx={{
        px: 2,
        py: 1.75,
        borderRadius: '4px 16px 16px 16px',
        bgcolor: 'background.paper',
        border: '1px solid',
        borderColor: 'divider',
        display: 'flex',
        gap: 0.75,
        alignItems: 'center',
      }}
    >
      {[0, 1, 2].map(i => (
        <Box
          key={i}
          sx={{
            width: 7,
            height: 7,
            borderRadius: '50%',
            bgcolor: 'text.disabled',
            animation: `${bounce} 1.4s ease-in-out infinite`,
            animationDelay: `${i * 0.16}s`,
          }}
        />
      ))}
    </Box>
  </Box>
);

export default ThinkingBubble;