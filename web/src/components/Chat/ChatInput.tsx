import { type KeyboardEvent } from 'react';
import { Box, IconButton, TextField, Tooltip, Typography } from '@mui/material';
import { ArrowUp } from 'lucide-react';

type Props = {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  placeholder?: string;
};

const ChatInput = ({ value, onChange, onSend, placeholder = 'Message...' }: Props) => {
  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  const canSend = !!value.trim();

  return (
    <Box
      sx={{
        px: { xs: 2, sm: 4, md: 8, lg: 16 },
        py: 2,
        bgcolor: 'background.default',
        flexShrink: 0,
      }}
    >
      <Box
        sx={{
          maxWidth: 760,
          mx: 'auto',
          display: 'flex',
          gap: 1,
          alignItems: 'flex-end',
          bgcolor: 'background.paper',
          border: '1px solid',
          borderColor: 'divider',
          borderRadius: 3,
          px: 1.5,
          py: 1,
          '&:focus-within': { borderColor: 'primary.main' },
        }}
      >
        <TextField
          fullWidth
          multiline
          maxRows={6}
          placeholder={placeholder}
          value={value}
          onChange={e => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          variant="standard"
          slotProps={{ input: { disableUnderline: true } }}
          sx={{ fontSize: '0.9rem' }}
        />
        <Tooltip title="Send (Enter)">
          <span>
            <IconButton
              onClick={onSend}
              disabled={!canSend}
              size="small"
              sx={{
                bgcolor: canSend ? 'primary.main' : 'action.disabledBackground',
                color: canSend ? 'primary.contrastText' : 'action.disabled',
                borderRadius: 1.5,
                width: 32,
                height: 32,
                flexShrink: 0,
                '&:hover': { bgcolor: 'primary.dark' },
                '&.Mui-disabled': { bgcolor: 'action.disabledBackground' },
              }}
            >
              <ArrowUp size={16} />
            </IconButton>
          </span>
        </Tooltip>
      </Box>
      <Typography
        variant="caption"
        sx={{ display: 'block', textAlign: 'center', mt: 1, color: 'text.disabled' }}
      >
        Press Enter to send · Shift+Enter for new line
      </Typography>
    </Box>
  );
};

export default ChatInput;