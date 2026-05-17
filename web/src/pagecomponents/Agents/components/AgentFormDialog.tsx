import { useEffect } from 'react';
import { useForm, Controller, useWatch } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Autocomplete,
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  FormControlLabel,
  FormHelperText,
  InputLabel,
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
import { useGetCollectionsQuery } from '@/api/endpoints/collection.ts';
import { agentFormSchema, type AgentFormValues } from '@/validation/agent.ts';
import { AgentType, type AgentRead } from '@/api/types/agent.ts';
import { useThemeMode } from '@/theme/ThemeContext.tsx';

const AGENT_TYPE_LABELS: Record<AgentType, string> = {
  [AgentType.GENERAL]: 'General',
  [AgentType.PROGRAMMING]: 'Programming',
  [AgentType.MATH]: 'Math',
  [AgentType.RESEARCHER]: 'Researcher',
  [AgentType.INVOICE]: 'Invoice',
};

type Props = {
  open: boolean;
  agent?: AgentRead;
  onClose: () => void;
};

const AgentFormDialog = ({ open, agent, onClose }: Props) => {
  const isEdit = !!agent;
  const { mode } = useThemeMode();
  const [createAgent, { isLoading: isCreating }] = useCreateAgentMutation();
  const [updateAgent, { isLoading: isUpdating }] = useUpdateAgentMutation();
  const { data: defaultPrompts = [] } = useGetDefaultPromptsQuery();
  const { data: llms = [], isLoading: llmsLoading } = useGetLLMsQuery();
  const { data: collections = [], isLoading: collectionsLoading } =
    useGetCollectionsQuery();

  const { control, handleSubmit, reset, setValue } = useForm<AgentFormValues>({
    resolver: zodResolver(agentFormSchema),
    defaultValues: {
      name: '',
      prompt: '',
      llm_id: '',
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
        llm_id: agent?.llm.id ?? '',
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
      llm_id: values.llm_id,
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

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
      <DialogTitle sx={{ pb: 0 }}>
        {isEdit ? 'Edit Agent' : 'Add Agent'}
      </DialogTitle>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent>
          <Stack spacing={2} sx={{ pt: 0.5 }}>
            <FormTextField name="name" control={control} label="Name" />

            <Controller
              name="prompt"
              control={control}
              render={({ field, fieldState }) => (
                <Box data-color-mode={mode}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography
                      variant="caption"
                      sx={{
                        ml: 1.75,
                        color: fieldState.error ? 'error.main' : 'text.secondary',
                      }}
                    >
                      System Prompt
                    </Typography>
                    <Button
                      size="small"
                      variant="text"
                      onClick={handleUseDefaultPrompt}
                      disabled={!defaultPrompts.some(p => p.agent_type === selectedAgentType)}
                    >
                      Use default
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
              name="llm_id"
              control={control}
              render={({ field, fieldState }) => (
                <FormControl fullWidth error={!!fieldState.error}>
                  <InputLabel>LLM Model</InputLabel>
                  <Select {...field} label="LLM Model" disabled={llmsLoading}>
                    {llmsLoading ? (
                      <MenuItem disabled>
                        <CircularProgress size={16} sx={{ mr: 1 }} /> Loading…
                      </MenuItem>
                    ) : (
                      llms.map(llm => (
                        <MenuItem key={llm.id} value={llm.id}>
                          {llm.model_name}
                        </MenuItem>
                      ))
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
                <FormControl fullWidth error={!!fieldState.error}>
                  <InputLabel>Agent Type</InputLabel>
                  <Select {...field} label="Agent Type">
                    {Object.values(AgentType).map(type => (
                      <MenuItem key={type} value={type}>
                        {AGENT_TYPE_LABELS[type]}
                      </MenuItem>
                    ))}
                  </Select>
                  {fieldState.error && (
                    <FormHelperText>{fieldState.error.message}</FormHelperText>
                  )}
                </FormControl>
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
                      label="Collections"
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
                  label="Active"
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
            Cancel
          </Button>
          <SubmitButton
            isLoading={isCreating || isUpdating}
            fullWidth
            sx={{ flex: 1, py: 1 }}
          >
            {isEdit ? 'Save changes' : 'Add agent'}
          </SubmitButton>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default AgentFormDialog;
