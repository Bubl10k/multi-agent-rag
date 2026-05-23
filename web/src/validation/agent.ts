import { z } from 'zod';
import { AgentType } from '@/api/types/agent';

export const agentFormSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  prompt: z.string().min(1, 'Prompt is required'),
  llm_selection: z.string().min(1, 'LLM model is required'),
  agent_type: z.nativeEnum(AgentType),
  collection_ids: z.array(z.string()),
  is_active: z.boolean(),
});

export type AgentFormValues = z.infer<typeof agentFormSchema>;

export function parseLLMSelection(selection: string): { llm_id?: string; platform_llm_id?: string } {
  if (selection.startsWith('platform:')) {
    return { platform_llm_id: selection.slice('platform:'.length) };
  }
  return { llm_id: selection.slice('user:'.length) };
}