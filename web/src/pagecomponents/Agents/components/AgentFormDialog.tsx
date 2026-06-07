import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useForm, Controller, useWatch } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  FormControlLabel,
  FormHelperText,
  InputLabel,
  ListSubheader,
  MenuItem,
  Select,
  Stack,
  Switch,
  TextField,
  Typography,
} from '@mui/material';
import MDEditor from '@uiw/react-md-editor';
import '@uiw/react-md-editor/markdown-editor.css';

import FormTextField from '@/components/Form/FormTextField.tsx';
import SubmitButton from '@/components/Form/SubmitButton.tsx';
import {
  useCreateAgentMutation,
  useGetDefaultPromptsQuery,
  useUpdateAgentMutation,
} from '@/api/endpoints/agent.ts';
import { useGetLLMsQuery } from '@/api/endpoints/llm.ts';
import { useGetPlatformLLMsQuery } from '@/api/endpoints/platform_llm.ts';
import { useGetCollectionsQuery } from '@/api/endpoints/collection.ts';
import { agentFormSchema, parseLLMSelection, type AgentFormValues } from '@/validation/agent.ts';
import { AgentType, type AgentRead } from '@/api/types/agent.ts';
import { useThemeMode } from '@/theme/ThemeContext.tsx';

type Props = {
  open: boolean;
  agent?: AgentRead;
  onClose: () => void;
};

function initialLLMSelection(agent?: AgentRead): string {
  if (!agent) return '';
  if (agent.platform_llm) return `platform:${agent.platform_llm.id}`;
  if (agent.llm) return `user:${agent.llm.id}`;
  return '';
}

const AgentFormDialog = ({ open, agent, onClose }: Props) => {
  const { t } = useTranslation();
  const isEdit = !!agent;
  const { mode } = useThemeMode();

  const AGENT_TYPE_LABELS: Record<AgentType, string> = {
    [AgentType.GENERAL]: t('dashboard.agentTypeLabels.general'),
    [AgentType.PROGRAMMING]: t('dashboard.agentTypeLabels.programming'),
    [AgentType.MATH]: t('dashboard.agentTypeLabels.math'),
    [AgentType.RESEARCHER]: t('dashboard.agentTypeLabels.researcher'),
    [AgentType.INVOICE]: t('dashboard.agentTypeLabels.invoice'),
    [AgentType.ROUTER]: t('dashboard.agentTypeLabels.router'),
  };

  const AGENT_TYPE_DESCRIPTIONS: Record<AgentType, string> = {
    [AgentType.GENERAL]: t('agents.descriptions.general'),
    [AgentType.PROGRAMMING]: t('agents.descriptions.programming'),
    [AgentType.MATH]: t('agents.descriptions.math'),
    [AgentType.RESEARCHER]: t('agents.descriptions.researcher'),
    [AgentType.INVOICE]: t('agents.descriptions.invoice'),
    [AgentType.ROUTER]: t('agents.descriptions.router'),
  };
  const [createAgent, { isLoading: isCreating }] = useCreateAgentMutation();
  const [updateAgent, { isLoading: isUpdating }] = useUpdateAgentMutation();
  const { data: defaultPrompts = [] } = useGetDefaultPromptsQuery();
  const { data: llms = [], isLoading: llmsLoading } = useGetLLMsQuery();
  const { data: platformLlms = [], isLoading: platformLlmsLoading } = useGetPlatformLLMsQuery();
  const { data: collections = [], isLoading: collectionsLoading } =
    useGetCollectionsQuery();

  const { control, handleSubmit, reset, setValue } = useForm<AgentFormValues>({
    resolver: zodResolver(agentFormSchema),
    defaultValues: {
      name: '',
      prompt: '',
      llm_selection: '',
      agent_type: AgentType.GENERAL,
      collection_ids: [],
      is_active: true,
    },
  });

  const selectedAgentType = useWatch({ control, name: 'agent_type' });

  const handleUseDefaultPrompt = () => {
    const match = defaultPrompts.find(p => p.agent_type === selectedAgentType);
    if (match) setValue('prompt', match.content);
  };

  useEffect(() => {
    if (open) {
      reset({
        name: agent?.name ?? '',
        prompt: agent?.prompt ?? '',
        llm_selection: initialLLMSelection(agent),
        agent_type: agent?.agent_type ?? AgentType.GENERAL,
        collection_ids: agent?.collections.map(c => c.id) ?? [],
        is_active: agent?.is_active ?? true,
      });
    }
  }, [open, agent, reset]);

  const onSubmit = async (values: AgentFormValues) => {
    const data = {
      name: values.name,
      prompt: values.prompt,
      ...parseLLMSelection(values.llm_selection),
      agent_type: values.agent_type,
      collection_ids: values.collection_ids,
      is_active: values.is_active,
    };
    if (isEdit) {
      await updateAgent({ id: agent.id, data });
    } else {
      await createAgent(data);
    }
    onClose();
  };

  const isLlmLoading = llmsLoading || platformLlmsLoading;

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
      <DialogTitle sx={{ pb: 0 }}>
        {isEdit ? t('agents.form.titleEdit') : t('agents.form.titleAdd')}
      </DialogTitle>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent>
          <Stack spacing={2} sx={{ pt: 0.5 }}>
            <FormTextField name="name" control={control} label={t('agents.form.name')} />

            <Controller
              name="prompt"
              control={control}
              render={({ field, fieldState }) => (
                <Box data-color-mode={mode}>
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      mb: 0.5,
                    }}
                  >
                    <Typography
                      variant="caption"
                      sx={{
                        ml: 1.75,
                        color: fieldState.error
                          ? 'error.main'
                          : 'text.secondary',
                      }}
                    >
                      {t('agents.form.systemPrompt')}
                    </Typography>
                    <Button
                      size="small"
                      variant="text"
                      onClick={handleUseDefaultPrompt}
                      disabled={
                        !defaultPrompts.some(
                          p => p.agent_type === selectedAgentType,
                        )
                      }
                    >
                      {t('agents.form.useDefault')}
                    </Button>
                  </Box>
                  <MDEditor
                    value={field.value}
                    onChange={v => field.onChange(v ?? '')}
                    height={500}
                    preview="edit"
                  />
                  {fieldState.error && (
                    <Typography
                      variant="caption"
                      color="error"
                      sx={{ ml: 1.75, mt: 0.5, display: 'block' }}
                    >
                      {fieldState.error.message}
                    </Typography>
                  )}
                </Box>
              )}
            />

            <Controller
              name="llm_selection"
              control={control}
              render={({ field, fieldState }) => (
                <FormControl fullWidth error={!!fieldState.error}>
                  <InputLabel>{t('agents.form.llmModel')}</InputLabel>
                  <Select {...field} label={t('agents.form.llmModel')} disabled={isLlmLoading}>
                    {isLlmLoading ? (
                      <MenuItem disabled>
                        <CircularProgress size={16} sx={{ mr: 1 }} /> {t('common.loading')}
                      </MenuItem>
                    ) : (
                      [
                        platformLlms.length > 0 && (
                          <ListSubheader key="platform-header">
                            {t('agents.form.platformModels')}
                          </ListSubheader>
                        ),
                        ...platformLlms.map(llm => (
                          <MenuItem key={`platform:${llm.id}`} value={`platform:${llm.id}`}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                              <span>{llm.display_name}</span>
                              <Chip
                                size="small"
                                label={`${llm.requests_used}/${llm.requests_limit} / hr`}
                                color={llm.requests_used >= llm.requests_limit ? 'error' : 'default'}
                                sx={{ ml: 'auto' }}
                              />
                            </Box>
                          </MenuItem>
                        )),
                        llms.length > 0 && (
                          <ListSubheader key="user-header">
                            {t('agents.form.yourModels')}
                          </ListSubheader>
                        ),
                        ...llms.map(llm => (
                          <MenuItem key={`user:${llm.id}`} value={`user:${llm.id}`}>
                            {llm.model_name}
                          </MenuItem>
                        )),
                      ]
                    )}
                  </Select>
                  {fieldState.error && (
                    <FormHelperText>{fieldState.error.message}</FormHelperText>
                  )}
                </FormControl>
              )}
            />

            <Controller
              name="agent_type"
              control={control}
              render={({ field, fieldState }) => (
                <Box>
                  <FormControl fullWidth error={!!fieldState.error}>
                    <InputLabel>{t('agents.table.type')}</InputLabel>
                    <Select {...field} label={t('agents.table.type')}>
                      {Object.values(AgentType).map(type => (
                        <MenuItem key={type} value={type}>
                          {AGENT_TYPE_LABELS[type]}
                        </MenuItem>
                      ))}
                    </Select>
                    {fieldState.error && (
                      <FormHelperText>
                        {fieldState.error.message}
                      </FormHelperText>
                    )}
                  </FormControl>
                  <Alert
                    severity={
                      selectedAgentType === AgentType.PROGRAMMING
                        ? 'warning'
                        : 'info'
                    }
                    sx={{ mt: 1 }}
                  >
                    {AGENT_TYPE_DESCRIPTIONS[selectedAgentType]}
                  </Alert>
                </Box>
              )}
            />

            <Controller
              name="collection_ids"
              control={control}
              render={({ field, fieldState }) => (
                <Autocomplete
                  multiple
                  options={collections}
                  loading={collectionsLoading}
                  getOptionLabel={c => c.name}
                  isOptionEqualToValue={(opt, val) => opt.id === val.id}
                  value={collections.filter(c => field.value.includes(c.id))}
                  onChange={(_e, selected) =>
                    field.onChange(selected.map(c => c.id))
                  }
                  renderInput={params => (
                    <TextField
                      {...params}
                      label={t('agents.table.collections')}
                      error={!!fieldState.error}
                      helperText={fieldState.error?.message}
                    />
                  )}
                />
              )}
            />

            <Controller
              name="is_active"
              control={control}
              render={({ field }) => (
                <FormControlLabel
                  control={
                    <Switch checked={field.value} onChange={field.onChange} />
                  }
                  label={t('agents.form.active')}
                />
              )}
            />
          </Stack>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2.5, gap: 1 }}>
          <Button
            onClick={onClose}
            variant="outlined"
            fullWidth
            sx={{ flex: 1 }}
          >
            {t('common.cancel')}
          </Button>
          <SubmitButton
            isLoading={isCreating || isUpdating}
            fullWidth
            sx={{ flex: 1, py: 1 }}
          >
            {isEdit ? t('agents.form.saveChanges') : t('agents.addAgent')}
          </SubmitButton>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default AgentFormDialog;