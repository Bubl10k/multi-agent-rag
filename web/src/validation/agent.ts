import { z } from 'zod';

export const agentFormSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  prompt: z.string().min(1, 'Prompt is required'),
  llm_id: z.string().min(1, 'LLM model is required'),
  collection_ids: z.array(z.string()),
  is_active: z.boolean(),
});

export type AgentFormValues = z.infer<typeof agentFormSchema>;