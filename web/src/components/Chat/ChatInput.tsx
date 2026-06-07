import { type KeyboardEvent, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Chip,
  CircularProgress,
  IconButton,
  ListSubheader,
  MenuItem,
  Select,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import { ArrowUp, Paperclip, Square, X } from 'lucide-react';
import type { LLMRead } from '@/api/types/llm';
import type { PlatformLLMRead } from '@/api/types/platform_llm';

type Props = {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  onStop?: () => void;
  placeholder?: string;
  disabled?: boolean;
  llms?: LLMRead[];
  platformLlms?: PlatformLLMRead[];
  selectedLlmSelection?: string;
  onLlmChange?: (selection: string) => void;
  attachedFileName?: string | null;
  onAttach?: (file: File) => void;
  onRemoveAttachment?: () => void;
  isAttaching?: boolean;
};

const ChatInput = ({
  value,
  onChange,
  onSend,
  onStop,
  placeholder,
  disabled = false,
  llms,
  platformLlms,
  selectedLlmSelection,
  onLlmChange,
  attachedFileName,
  onAttach,
  onRemoveAttachment,
  isAttaching = false,
}: Props) => {
  const { t } = useTranslation();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onAttach) {
      onAttach(file);
    }
    e.target.value = '';
  };

  const canSend = (!!value.trim() || !!attachedFileName) && !disabled && !isAttaching;
  const hasLlmOptions = (llms && llms.length > 0) || (platformLlms && platformLlms.length > 0);

  return (
    <Box
      sx={{
        px: { xs: 2, sm: 4, md: 8, lg: 16 },
        py: 2,
        bgcolor: 'background.default',
        flexShrink: 0,
      }}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.txt,.md,.docx"
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />
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
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 0.5 }}>
          {hasLlmOptions && onLlmChange && (
            <Select
              variant="standard"
              disableUnderline
              size="small"
              value={selectedLlmSelection ?? ''}
              onChange={e => onLlmChange(e.target.value)}
              displayEmpty
              sx={{
                fontSize: '0.75rem',
                color: 'text.secondary',
                alignSelf: 'flex-start',
                '.MuiSelect-select': { py: 0, pr: '20px !important' },
              }}
            >
              {platformLlms && platformLlms.length > 0 && [
                <ListSubheader key="platform-header" sx={{ fontSize: '0.7rem', lineHeight: '28px' }}>
                  {t('chat.platformModels')}
                </ListSubheader>,
                ...platformLlms.map(llm => (
                  <MenuItem key={`platform:${llm.id}`} value={`platform:${llm.id}`} sx={{ fontSize: '0.8rem' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                      <span>{llm.display_name}</span>
                      <Chip
                        size="small"
                        label={`${llm.requests_used}/${llm.requests_limit}/hr`}
                        color={llm.requests_used >= llm.requests_limit ? 'error' : 'default'}
                        sx={{ ml: 'auto', fontSize: '0.65rem', height: 18 }}
                      />
                    </Box>
                  </MenuItem>
                )),
              ]}
              {llms && llms.length > 0 && [
                <ListSubheader key="user-header" sx={{ fontSize: '0.7rem', lineHeight: '28px' }}>
                  {t('chat.yourModels')}
                </ListSubheader>,
                ...llms.map(llm => (
                  <MenuItem key={`user:${llm.id}`} value={`user:${llm.id}`} sx={{ fontSize: '0.8rem' }}>
                    {llm.model_name}
                  </MenuItem>
                )),
              ]}
            </Select>
          )}
          {attachedFileName && (
            <Chip
              size="small"
              label={attachedFileName}
              onDelete={onRemoveAttachment}
              deleteIcon={<X size={12} />}
              sx={{ alignSelf: 'flex-start', maxWidth: '100%', fontSize: '0.72rem' }}
            />
          )}
          <TextField
            fullWidth
            multiline
            maxRows={6}
            placeholder={placeholder ?? t('chat.inputPlaceholder')}
            value={value}
            onChange={e => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            variant="standard"
            slotProps={{ input: { disableUnderline: true } }}
            sx={{ fontSize: '0.9rem' }}
          />
        </Box>
        {onAttach && (
          <Tooltip title={t('chat.attachFile')}>
            <span>
              <IconButton
                onClick={() => fileInputRef.current?.click()}
                disabled={disabled || isAttaching}
                size="small"
                sx={{ flexShrink: 0, width: 32, height: 32 }}
              >
                {isAttaching ? <CircularProgress size={14} /> : <Paperclip size={16} />}
              </IconButton>
            </span>
          </Tooltip>
        )}
        {disabled && onStop ? (
          <Tooltip title={t('chat.stop')}>
            <IconButton
              onClick={onStop}
              size="small"
              sx={{
                bgcolor: 'primary.main',
                color: 'primary.contrastText',
                borderRadius: 1.5,
                width: 32,
                height: 32,
                flexShrink: 0,
                '&:hover': { bgcolor: 'primary.dark' },
              }}
            >
              <Square size={14} fill="currentColor" />
            </IconButton>
          </Tooltip>
        ) : (
          <Tooltip title={t('chat.sendEnter')}>
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
        )}
      </Box>
      <Typography
        variant="caption"
        sx={{
          display: 'block',
          textAlign: 'center',
          mt: 1,
          color: 'text.disabled',
        }}
      >
        {t('chat.sendHint')}
      </Typography>
    </Box>
  );
};

export default ChatInput;