import { Box, Typography } from '@mui/material';
import type { Agent } from '@/types/chat';
import ChatAvatar from '@/components/Chat/ChatAvatar.tsx';

type Props = {
  agent: Agent;
};

const ChatHeader = ({ agent }: Props) => (
  <Box
    sx={{
      px: 3,
      py: 1.5,
      display: 'flex',
      alignItems: 'center',
      gap: 1.5,
      bgcolor: 'background.paper',
      borderBottom: '1px solid',
      borderColor: 'divider',
      flexShrink: 0,
    }}
  >
    <ChatAvatar icon={agent.Icon} />
    <Typography sx={{ fontWeight: 600, fontSize: '0.95rem' }}>
      {agent.label}
    </Typography>
  </Box>
);

export default ChatHeader;
