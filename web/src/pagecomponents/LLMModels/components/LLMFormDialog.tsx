import { useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  FormControlLabel,
  Stack,
  Switch,
  Typography,
} from '@mui/material';

import FormTextField from '@/components/Form/FormTextField.tsx';
import SubmitButton from '@/components/Form/SubmitButton.tsx';
import {
  useCreateLLMMutation,
  useUpdateLLMMutation,
} from '@/api/endpoints/llm.ts';
import { llmFormSchema, type LLMFormValues } from '@/validation/llm.ts';

import type { LLMRead } from '@/api/types/llm.ts';

type Props = {
  open: boolean;
  llm?: LLMRead;
  onClose: () => void;
};

const LLMFormDialog = ({ open, llm, onClose }: Props) => {
  const isEdit = !!llm;
  const [createLLM, { isLoading: isCreating }] = useCreateLLMMutation();
  const [updateLLM, { isLoading: isUpdating }] = useUpdateLLMMutation();

  const { control, handleSubmit, reset, setError } = useForm<LLMFormValues>({
    resolver: zodResolver(llmFormSchema),
    defaultValues: { model_name: '', api_key: '', is_active: true },
  });

  useEffect(() => {
    if (open) {
      reset({
        model_name: llm?.model_name ?? '',
        api_key: '',
        is_active: llm?.is_active ?? true,
      });
    }
  }, [open, llm, reset]);

  const onSubmit = async (values: LLMFormValues) => {
    if (!isEdit && !values.api_key) {
      setError('api_key', { message: 'API key is required' });
      return;
    }
    if (isEdit) {
      const data: { model_name: string; is_active: boolean; api_key?: string } =
        {
          model_name: values.model_name,
          is_active: values.is_active,
        };
      if (values.api_key) data.api_key = values.api_key;
      await updateLLM({ id: llm.id, data });
    } else {
      await createLLM({
        model_name: values.model_name,
        api_key: values.api_key,
        is_active: values.is_active,
      });
    }
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle sx={{ pb: 0 }}>
        {isEdit ? 'Edit LLM Model' : 'Add LLM Model'}
      </DialogTitle>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent>
          <Stack spacing={2} sx={{ pt: 0.5 }}>
            <DialogContentText variant="body2">
              Enter the model identifier and API key from your provider.{' '}
              <Typography
                component="span"
                variant="body2"
                color="text.secondary"
                fontSize="inherit"
              >
                Model name must match the exact ID used by the provider (e.g.{' '}
                <code>gpt-4o</code> for OpenAI, <code>claude-sonnet-4-6</code>{' '}
                for Anthropic). API keys can be found in your provider's
                dashboard under API settings.
              </Typography>
            </DialogContentText>
            <FormTextField
              name="model_name"
              control={control}
              label="Model Name"
              placeholder="e.g. gpt-4o, claude-sonnet-4-6"
            />
            <FormTextField
              name="api_key"
              control={control}
              label="API Key"
              type="password"
              placeholder={isEdit ? 'Leave blank to keep current key' : ''}
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
            fullWidth={true}
            sx={{ flex: 1, py: 1 }}
          >
            {isEdit ? 'Save changes' : 'Add model'}
          </SubmitButton>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default LLMFormDialog;
