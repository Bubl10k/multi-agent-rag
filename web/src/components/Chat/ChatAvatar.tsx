import { Avatar } from '@mui/material';
import type { LucideIcon } from 'lucide-react';

type Props = {
  icon?: LucideIcon;
  label?: string;
};

const ChatAvatar = ({ icon: Icon, label = 'G' }: Props) => (
  <Avatar
    sx={{
      width: 32,
      height: 32,
      bgcolor: Icon ? 'primary.main' : 'action.selected',
      fontSize: '0.75rem',
      fontWeight: 700,
      color: Icon ? 'white' : 'text.secondary',
      flexShrink: 0,
    }}
  >
    {Icon ? <Icon size={16} color="white" /> : label}
  </Avatar>
);

export default ChatAvatar;