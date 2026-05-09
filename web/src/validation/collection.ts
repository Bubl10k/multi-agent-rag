import { z } from 'zod';

export const collectionFormSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  description: z.string().optional(),
  embedding_model: z.string().optional(),
});

export type CollectionFormValues = z.infer<typeof collectionFormSchema>;