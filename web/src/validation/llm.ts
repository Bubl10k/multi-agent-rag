import { z } from 'zod';

export const llmFormSchema = z.object({
  model_name: z.string().min(1, 'Model name is required'),
  api_key: z.string(),
  is_active: z.boolean(),
});

export type LLMFormValues = z.infer<typeof llmFormSchema>;
