import { useState } from 'react';
import {
  Avatar,
  Box,
  Divider,
  IconButton,
  List,
  ListItemButton,
  ListItemText,
  Tooltip,
  Typography,
} from '@mui/material';
import type { LucideIcon } from 'lucide-react';
import {
  CirclePlus,
  LayoutDashboard,
  MessageSquare,
  Moon,
  PanelLeftClose,
  PanelLeftOpen,
  Sun,
  UserCog,
} from 'lucide-react';

import { useThemeMode } from '@/theme/ThemeContext';
import { localStorageService } from '@/utils/localStorage';
import { MOCK_AGENTS } from '@/mocks/agents';
import { MOCK_SESSIONS } from '@/mocks/sessions';
import { MOCK_USER } from '@/mocks/user';
import type { Agent, Session } from '@/types/chat.tsx';

const SIDEBAR_WIDTH = 260;
const SIDEBAR_WIDTH_COLLAPSED = 56;

type ActionButton = { label: string; Icon: LucideIcon };

const ACTION_BUTTONS: ActionButton[] = [
  { label: 'Add Agent', Icon: CirclePlus },
  { label: 'Modify Agents', Icon: UserCog },
  { label: 'Dashboard', Icon: LayoutDashboard },
];

const groupSessions = (sessions: Session[]) =>
  sessions.reduce<Record<string, Session[]>>((acc, session) => {
    (acc[session.group] ??= []).push(session);
    return acc;
  }, {});

const ICON_BTN_SX = {
  borderRadius: 2,
  width: 38,
  height: 38,
  flexShrink: 0,
} as const;

const SectionLabel = ({ children }: { children: string }) => (
  <Typography
    variant="caption"
    sx={{
      display: 'block',
      px: 1.5,
      py: 0.75,
      color: 'text.disabled',
      fontWeight: 600,
      textTransform: 'uppercase',
      letterSpacing: '0.06em',
      fontSize: '0.65rem',
      whiteSpace: 'nowrap',
    }}
  >
    {children}
  </Typography>
);

const Sidebar = () => {
  const [sessions, setSessions] = useState<Session[]>(MOCK_SESSIONS);
  const [activeSessionId, setActiveSessionId] = useState<string>('1');
  const [collapsed, setCollapsed] = useState<boolean>(
    () => localStorageService.getSidebarCollapsed() ?? false,
  );
  const { mode, toggleTheme } = useThemeMode();

  const grouped = groupSessions(sessions);

  const handleAgentClick = (agent: Agent) => {
    const newSession: Session = {
      id: Date.now().toString(),
      title: `New ${agent.label} conversation`,
      group: 'Today',
      agentId: agent.id,
    };
    setSessions(prev => [newSession, ...prev]);
    setActiveSessionId(newSession.id);
  };

  const handleCollapseToggle = () => {
    const next = !collapsed;
    setCollapsed(next);
    localStorageService.setSidebarCollapsed(next);
  };

  return (
    <Box
      sx={{
        width: collapsed ? SIDEBAR_WIDTH_COLLAPSED : SIDEBAR_WIDTH,
        minWidth: collapsed ? SIDEBAR_WIDTH_COLLAPSED : SIDEBAR_WIDTH,
        height: '100vh',
        bgcolor: 'background.paper',
        display: 'flex',
        flexDirection: 'column',
        borderRight: '1px solid',
        borderColor: 'divider',
        transition: 'width 0.2s ease, min-width 0.2s ease',
        overflow: 'hidden',
      }}
    >
      {/* Collapse toggle */}
      <Box
        sx={{
          p: 1.5,
          display: 'flex',
          justifyContent: collapsed ? 'center' : 'flex-end',
        }}
      >
        <Tooltip
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          placement="right"
        >
          <IconButton
            onClick={handleCollapseToggle}
            size="small"
            sx={ICON_BTN_SX}
          >
            {collapsed ? (
              <PanelLeftOpen size={16} />
            ) : (
              <PanelLeftClose size={16} />
            )}
          </IconButton>
        </Tooltip>
      </Box>

      {/* Scrollable content */}
      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          overflowX: 'hidden',
          px: collapsed ? 0.75 : 1,
        }}
      >
        {/* Agents */}
        {!collapsed && <SectionLabel>Agents</SectionLabel>}
        <List disablePadding sx={{ mb: 1 }}>
          {MOCK_AGENTS.map(agent =>
            collapsed ? (
              <Tooltip key={agent.id} title={agent.label} placement="right">
                <ListItemButton
                  onClick={() => handleAgentClick(agent)}
                  sx={{
                    borderRadius: 1.5,
                    mb: 0.25,
                    py: 0.75,
                    justifyContent: 'center',
                    px: 0,
                  }}
                >
                  <agent.Icon size={16} />
                </ListItemButton>
              </Tooltip>
            ) : (
              <ListItemButton
                key={agent.id}
                onClick={() => handleAgentClick(agent)}
                sx={{
                  borderRadius: 1.5,
                  mb: 0.25,
                  py: 0.75,
                  px: 1.5,
                  gap: 1.5,
                }}
              >
                <agent.Icon size={16} style={{ flexShrink: 0, opacity: 0.6 }} />
                <ListItemText
                  primary={agent.label}
                  slotProps={{
                    primary: { style: { fontSize: '0.875rem' }, noWrap: true },
                  }}
                />
              </ListItemButton>
            ),
          )}
        </List>

        <Divider sx={{ mx: collapsed ? 0 : 0.5, mb: 1 }} />

        {/* Sessions history */}
        {!collapsed && <SectionLabel>Conversation History</SectionLabel>}
        {collapsed ? (
          <List
            disablePadding
            sx={{ display: 'flex', flexDirection: 'column', gap: 0.25 }}
          >
            {sessions.map(session => (
              <Tooltip key={session.id} title={session.title} placement="right">
                <ListItemButton
                  selected={activeSessionId === session.id}
                  onClick={() => setActiveSessionId(session.id)}
                  sx={{
                    borderRadius: 1.5,
                    justifyContent: 'center',
                    py: 0.75,
                    px: 0,
                  }}
                >
                  <MessageSquare size={16} />
                </ListItemButton>
              </Tooltip>
            ))}
          </List>
        ) : (
          Object.entries(grouped).map(([group, groupedSessions]) => (
            <Box key={group} sx={{ mb: 1 }}>
              <SectionLabel>{group}</SectionLabel>
              <List disablePadding>
                {groupedSessions.map(session => (
                  <ListItemButton
                    key={session.id}
                    selected={activeSessionId === session.id}
                    onClick={() => setActiveSessionId(session.id)}
                    sx={{ borderRadius: 1.5, mb: 0.25, py: 0.75, px: 1.5 }}
                  >
                    <ListItemText
                      primary={session.title}
                      slotProps={{
                        primary: {
                          style: { fontSize: '0.875rem' },
                          noWrap: true,
                        },
                      }}
                    />
                  </ListItemButton>
                ))}
              </List>
            </Box>
          ))
        )}
      </Box>

      <Divider />

      {/* Action buttons */}
      <Box
        sx={{
          px: collapsed ? 0.75 : 1,
          py: 1.5,
          display: 'flex',
          flexDirection: 'column',
          gap: 0.25,
          alignItems: collapsed ? 'center' : 'stretch',
        }}
      >
        {ACTION_BUTTONS.map(({ label, Icon }) =>
          collapsed ? (
            <Tooltip key={label} title={label} placement="right">
              <IconButton size="small" sx={{ ...ICON_BTN_SX, border: 'none' }}>
                <Icon size={16} />
              </IconButton>
            </Tooltip>
          ) : (
            <Box
              key={label}
              component="button"
              onClick={() => {}}
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1.5,
                px: 1.5,
                py: 0.85,
                border: 'none',
                background: 'none',
                cursor: 'pointer',
                borderRadius: 1.5,
                color: 'text.secondary',
                fontSize: '0.875rem',
                fontFamily: 'inherit',
                width: '100%',
                textAlign: 'left',
                '&:hover': { bgcolor: 'action.hover', color: 'text.primary' },
              }}
            >
              <Icon size={16} />
              <Typography
                component="span"
                sx={{ fontSize: '0.875rem', fontWeight: 500 }}
              >
                {label}
              </Typography>
            </Box>
          ),
        )}
      </Box>

      <Divider />

      {/* User + Theme toggle */}
      <Box
        sx={{
          m: 1,
          px: collapsed ? 0 : 1.5,
          py: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'space-between',
          flexDirection: collapsed ? 'column' : 'row',
          gap: collapsed ? 1 : 0,
          cursor: 'pointer',
          borderRadius: 2,
          '&:hover': { bgcolor: 'action.hover' },
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Tooltip
            title={collapsed ? (MOCK_USER ?? 'Guest') : ''}
            placement="right"
          >
            <Avatar
              sx={{
                width: 32,
                height: 32,
                bgcolor: MOCK_USER ? 'primary.main' : 'action.selected',
                fontSize: '0.8rem',
                fontWeight: 700,
                color: MOCK_USER ? 'primary.contrastText' : 'text.secondary',
                flexShrink: 0,
              }}
            >
              {MOCK_USER ? MOCK_USER[0].toUpperCase() : 'G'}
            </Avatar>
          </Tooltip>
          {!collapsed && (
            <Typography
              sx={{
                fontSize: '0.875rem',
                fontWeight: 500,
                color: 'text.primary',
              }}
            >
              {MOCK_USER ?? 'Guest'}
            </Typography>
          )}
        </Box>

        <Tooltip
          title={mode === 'light' ? 'Dark mode' : 'Light mode'}
          placement="right"
        >
          <IconButton
            onClick={e => {
              e.stopPropagation();
              toggleTheme();
            }}
            size="small"
            sx={{ flexShrink: 0 }}
          >
            {mode === 'light' ? <Moon size={16} /> : <Sun size={16} />}
          </IconButton>
        </Tooltip>
      </Box>
    </Box>
  );
};

export default Sidebar;
