import { Box, Typography } from '@mui/material';
import ChatAvatar from '@/components/Chat/ChatAvatar';

type Props = {
  agentName?: string;
};

const ChatHeader = ({ agentName }: Props) => (
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
    <ChatAvatar variant="agent" />
    <Typography sx={{ fontWeight: 600, fontSize: '0.95rem' }}>
      {agentName ?? '…'}
    </Typography>
  </Box>
);

export default ChatHeader;