import { Brain, FolderOpen, LayoutDashboard, UserCog } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { ROUTES } from '@/router/router';

export type ActionButtonDef = {
  label: string;
  Icon: LucideIcon;
  path?: string;
};

export const ACTION_BUTTONS: ActionButtonDef[] = [
  { label: 'Manage Agents', Icon: UserCog, path: ROUTES.AGENTS },
  { label: 'LLM Models', Icon: Brain, path: ROUTES.LLM_MODELS },
  { label: 'Collections', Icon: FolderOpen, path: ROUTES.COLLECTIONS },
  { label: 'Dashboard', Icon: LayoutDashboard },
];
