export type PlatformLLMBasicRead = {
  id: string;
  display_name: string;
  model_name: string;
  provider: string;
  is_active: boolean;
};

export type PlatformLLMRead = PlatformLLMBasicRead & {
  requests_used: number;
  requests_limit: number;
};