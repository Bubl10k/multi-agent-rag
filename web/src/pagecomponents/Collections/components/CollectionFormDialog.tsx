import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Stack,
} from '@mui/material';

import FormTextField from '@/components/Form/FormTextField.tsx';
import SubmitButton from '@/components/Form/SubmitButton.tsx';
import {
  useCreateCollectionMutation,
  useUpdateCollectionMutation,
} from '@/api/endpoints/collection.ts';
import {
  collectionFormSchema,
  type CollectionFormValues,
} from '@/validation/collection.ts';
import type { CollectionRead } from '@/api/types/collection.ts';

type Props = {
  open: boolean;
  collection?: CollectionRead;
  onClose: () => void;
};

const CollectionFormDialog = ({ open, collection, onClose }: Props) => {
  const isEdit = !!collection;
  const [createCollection, { isLoading: isCreating }] =
    useCreateCollectionMutation();
  const [updateCollection, { isLoading: isUpdating }] =
    useUpdateCollectionMutation();

  const { control, handleSubmit, reset } = useForm<CollectionFormValues>({
    resolver: zodResolver(collectionFormSchema),
    defaultValues: { name: '', description: '', embedding_model: '' },
  });

  useEffect(() => {
    if (open) {
      reset({
        name: collection?.name ?? '',
        description: collection?.description ?? '',
        embedding_model: collection?.embedding_model ?? '',
      });
    }
  }, [open, collection, reset]);

  const onSubmit = async (values: CollectionFormValues) => {
    const data = {
      name: values.name,
      ...(values.description ? { description: values.description } : {}),
      ...(values.embedding_model
        ? { embedding_model: values.embedding_model }
        : {}),
    };
    if (isEdit) {
      await updateCollection({ id: collection.id, data });
    } else {
      await createCollection(data);
    }
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle sx={{ pb: 0 }}>
        {isEdit ? 'Edit Collection' : 'Add Collection'}
      </DialogTitle>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent>
          <Stack spacing={2} sx={{ pt: 0.5 }}>
            <FormTextField name="name" control={control} label="Name" />
            <FormTextField
              name="description"
              control={control}
              label="Description"
              multiline
              rows={2}
            />
            <FormTextField
              name="embedding_model"
              control={control}
              label="Embedding Model"
              placeholder="Leave blank to use default"
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
            {isEdit ? 'Save changes' : 'Add collection'}
          </SubmitButton>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default CollectionFormDialog;
