import { Avatar } from '@mui/material';
import { Bot, User } from 'lucide-react';

type Props = {
  variant?: 'agent' | 'user';
};

const ChatAvatar = ({ variant = 'user' }: Props) => (
  <Avatar
    sx={{
      width: 32,
      height: 32,
      bgcolor: variant === 'agent' ? 'primary.main' : 'action.selected',
      fontSize: '0.75rem',
      fontWeight: 700,
      flexShrink: 0,
    }}
  >
    {variant === 'agent'
      ? <Bot size={16} color="white" />
      : <User size={16} />
    }
  </Avatar>
);

export default ChatAvatar;