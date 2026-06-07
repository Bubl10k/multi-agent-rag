import { Brain, FolderOpen, LayoutDashboard, UserCog } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { ROUTES } from '@/router/router';

export type ActionButtonDef = {
  labelKey: string;
  Icon: LucideIcon;
  path?: string;
};

export const ACTION_BUTTONS: ActionButtonDef[] = [
  { labelKey: 'sidebar.manageAgents', Icon: UserCog, path: ROUTES.AGENTS },
  { labelKey: 'sidebar.llmModels', Icon: Brain, path: ROUTES.LLM_MODELS },
  { labelKey: 'sidebar.collections', Icon: FolderOpen, path: ROUTES.COLLECTIONS },
  { labelKey: 'sidebar.dashboard', Icon: LayoutDashboard, path: ROUTES.DASHBOARD },
];
