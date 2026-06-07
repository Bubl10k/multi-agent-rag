import { z } from 'zod';
import type { TFunction } from 'i18next';

export const getLLMFormSchema = (t: TFunction) =>
  z.object({
    model_name: z.string().min(1, t('llmModels.form.modelNameRequired')),
    api_key: z.string(),
    is_active: z.boolean(),
  });

export type LLMFormValues = z.infer<ReturnType<typeof getLLMFormSchema>>;
