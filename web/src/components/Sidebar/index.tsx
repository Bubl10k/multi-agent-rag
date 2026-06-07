import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Avatar,
  Box,
  Divider,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Tooltip,
  Typography,
} from '@mui/material';
import {
  Bot,
  Languages,
  LogOut,
  MessageSquare,
  Moon,
  MoreHorizontal,
  PanelLeftClose,
  PanelLeftOpen,
  Sun,
  Trash2,
} from 'lucide-react';
import { useNavigate, useSearchParams } from 'react-router';

import { changeLanguage } from '@/i18n';
import { useThemeMode } from '@/theme/ThemeContext';
import { DEFAULT_LANGUAGE, LANGUAGE_NAMES, Language } from '@/types/i18n';
import { localStorageService } from '@/utils/localStorage';
import { useAppSelector } from '@/store';
import { useActions } from '@/hooks/useActions';
import { chatPath, conversationChatPath, ROUTES } from '@/router/router';
import ConfirmDialog from '@/components/ConfirmDialog';
import { useGetAgentsQuery } from '@/api/endpoints/agent';
import {
  useDeleteConversationMutation,
  useGetConversationsQuery,
} from '@/api/endpoints/conversation';
import type { AgentRead } from '@/api/types/agent';
import type { ConversationRead } from '@/api/types/conversation';
import {
  GROUP_ORDER,
  getConversationPreview,
  groupConversationsByDate,
} from '@/utils/conversation';
import SectionLabel from './SectionLabel';
import { ACTION_BUTTONS } from './constants';

const SIDEBAR_WIDTH = 260;
const SIDEBAR_WIDTH_COLLAPSED = 56;

const ICON_BTN_SX = {
  borderRadius: 2,
  width: 38,
  height: 38,
  flexShrink: 0,
} as const;

const Sidebar = () => {
  const { t, i18n } = useTranslation();
  const [collapsed, setCollapsed] = useState<boolean>(
    () => localStorageService.getSidebarCollapsed() ?? false,
  );
  const { mode, toggleTheme } = useThemeMode();
  const { logout } = useActions();
  const navigate = useNavigate();
  const [languageMenuAnchor, setLanguageMenuAnchor] =
    useState<HTMLElement | null>(null);

  const [searchParams] = useSearchParams();
  const user = useAppSelector(state => state.auth.user);
  const [logoutDialogOpen, setLogoutDialogOpen] = useState(false);

  const { data: agents = [], isLoading: agentsLoading } = useGetAgentsQuery();
  const { data: conversations = [], isLoading: conversationsLoading } =
    useGetConversationsQuery();
  const [deleteConversation] = useDeleteConversationMutation();

  const activeConversationId = searchParams.get('conversationId');
  const [menuState, setMenuState] = useState<{
    anchor: HTMLElement;
    conv: ConversationRead;
  } | null>(null);
  const [deletingConversation, setDeletingConversation] =
    useState<ConversationRead | null>(null);

  const handleLogoutConfirm = () => {
    logout();
    navigate(ROUTES.LOGIN);
  };

  const handleAgentClick = (agent: AgentRead) => {
    navigate(chatPath(agent.id));
  };

  const handleConversationClick = (conversation: ConversationRead) => {
    navigate(conversationChatPath(conversation.agent_id, conversation.id));
  };

  const handleMenuOpen = (
    e: React.MouseEvent<HTMLButtonElement>,
    conv: ConversationRead,
  ) => {
    e.stopPropagation();
    setMenuState({ anchor: e.currentTarget, conv });
  };

  const handleMenuClose = () => setMenuState(null);

  const handleDeleteMenuClick = () => {
    if (!menuState) return;
    setDeletingConversation(menuState.conv);
    handleMenuClose();
  };

  const handleDeleteConfirm = async () => {
    if (!deletingConversation) return;
    await deleteConversation(deletingConversation.id);
    if (activeConversationId === deletingConversation.id) {
      navigate(chatPath(deletingConversation.agent_id));
    }
    setDeletingConversation(null);
  };

  const handleCollapseToggle = () => {
    const next = !collapsed;
    setCollapsed(next);
    localStorageService.setSidebarCollapsed(next);
  };

  const handleLanguageMenuOpen = (e: React.MouseEvent<HTMLButtonElement>) => {
    setLanguageMenuAnchor(e.currentTarget);
  };

  const handleLanguageMenuClose = () => setLanguageMenuAnchor(null);

  const handleLanguageSelect = (language: Language) => {
    changeLanguage(language);
    handleLanguageMenuClose();
  };

  const grouped = groupConversationsByDate(conversations);

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
          title={collapsed ? t('sidebar.expand') : t('sidebar.collapse')}
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
        {!collapsed && <SectionLabel>{t('sidebar.agents')}</SectionLabel>}
        <List disablePadding sx={{ mb: 1 }}>
          {agentsLoading ? (
            <Box sx={{ px: 1.5, py: 1 }}>
              <Typography variant="caption" color="text.disabled">
                {t('common.loading')}
              </Typography>
            </Box>
          ) : (
            agents.map(agent =>
              collapsed ? (
                <Tooltip key={agent.id} title={agent.name} placement="right">
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
                    <Bot size={16} />
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
                  <Bot size={16} style={{ flexShrink: 0, opacity: 0.6 }} />
                  <ListItemText
                    primary={agent.name}
                    slotProps={{
                      primary: {
                        style: { fontSize: '0.875rem' },
                        noWrap: true,
                      },
                    }}
                  />
                </ListItemButton>
              ),
            )
          )}
        </List>

        <Divider sx={{ mx: collapsed ? 0 : 0.5, mb: 1 }} />

        {/* Conversation history */}
        {!collapsed && (
          <SectionLabel>{t('sidebar.conversationHistory')}</SectionLabel>
        )}
        {conversationsLoading ? (
          <Box sx={{ px: 1.5, py: 1 }}>
            <Typography variant="caption" color="text.disabled">
              {t('common.loading')}
            </Typography>
          </Box>
        ) : collapsed ? (
          <List
            disablePadding
            sx={{ display: 'flex', flexDirection: 'column', gap: 0.25 }}
          >
            {conversations.map(conv => (
              <Tooltip
                key={conv.id}
                title={getConversationPreview(conv)}
                placement="right"
              >
                <ListItemButton
                  selected={activeConversationId === conv.id}
                  onClick={() => handleConversationClick(conv)}
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
        ) : conversations.length === 0 ? (
          !collapsed && (
            <Box sx={{ px: 1.5, py: 1 }}>
              <Typography variant="caption" color="text.disabled">
                {t('sidebar.noConversations')}
              </Typography>
            </Box>
          )
        ) : (
          GROUP_ORDER.filter(g => grouped[g]?.length).map(group => (
            <Box key={group} sx={{ mb: 1 }}>
              <SectionLabel>{t(`sidebar.dateGroups.${group}`)}</SectionLabel>
              <List disablePadding>
                {grouped[group].map(conv => (
                  <ListItemButton
                    key={conv.id}
                    selected={activeConversationId === conv.id}
                    onClick={() => handleConversationClick(conv)}
                    sx={{
                      borderRadius: 1.5,
                      mb: 0.25,
                      py: 0.75,
                      px: 1.5,
                      '& .conv-menu-btn': { opacity: 0 },
                      '&:hover .conv-menu-btn': { opacity: 1 },
                    }}
                  >
                    <ListItemText
                      primary={getConversationPreview(conv)}
                      slotProps={{
                        primary: {
                          style: { fontSize: '0.875rem' },
                          noWrap: true,
                        },
                      }}
                    />
                    <IconButton
                      className="conv-menu-btn"
                      size="small"
                      onClick={e => handleMenuOpen(e, conv)}
                      sx={{ flexShrink: 0, p: 0.5, color: 'text.secondary' }}
                    >
                      <MoreHorizontal size={14} />
                    </IconButton>
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
        {ACTION_BUTTONS.map(({ labelKey, Icon, path }) => {
          const label = t(labelKey);
          const handleClick = path ? () => navigate(path) : undefined;
          return collapsed ? (
            <Tooltip key={labelKey} title={label} placement="right">
              <IconButton
                size="small"
                onClick={handleClick}
                sx={{ ...ICON_BTN_SX, border: 'none' }}
              >
                <Icon size={16} />
              </IconButton>
            </Tooltip>
          ) : (
            <Box
              key={labelKey}
              component="button"
              onClick={handleClick}
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
          );
        })}
      </Box>

      <Divider />

      {/* User + Theme toggle + Logout */}
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
          borderRadius: 2,
        }}
      >
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1.5,
            overflow: 'hidden',
          }}
        >
          <Tooltip
            title={collapsed ? (user?.email ?? t('sidebar.guest')) : ''}
            placement="right"
          >
            <Avatar
              sx={{
                width: 32,
                height: 32,
                bgcolor: user ? 'primary.main' : 'action.selected',
                fontSize: '0.8rem',
                fontWeight: 700,
                color: user ? 'primary.contrastText' : 'text.secondary',
                flexShrink: 0,
              }}
            >
              {user ? user.email[0].toUpperCase() : 'G'}
            </Avatar>
          </Tooltip>
          {!collapsed && (
            <Typography
              noWrap
              sx={{
                fontSize: '0.875rem',
                fontWeight: 500,
                color: 'text.primary',
              }}
            >
              {user?.email ?? t('sidebar.guest')}
            </Typography>
          )}
        </Box>

        <Box sx={{ display: 'flex', gap: 0.5, flexShrink: 0 }}>
          <Tooltip title={t('language.label')} placement="right">
            <IconButton onClick={handleLanguageMenuOpen} size="small">
              <Languages size={16} />
            </IconButton>
          </Tooltip>
          <Tooltip
            title={mode === 'light' ? t('theme.dark') : t('theme.light')}
            placement="right"
          >
            <IconButton onClick={toggleTheme} size="small">
              {mode === 'light' ? <Moon size={16} /> : <Sun size={16} />}
            </IconButton>
          </Tooltip>
          <Tooltip title={t('sidebar.signOut')} placement="right">
            <IconButton onClick={() => setLogoutDialogOpen(true)} size="small">
              <LogOut size={16} />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Menu
        anchorEl={menuState?.anchor}
        open={!!menuState}
        onClose={handleMenuClose}
        slotProps={{ paper: { sx: { minWidth: 160 } } }}
      >
        <MenuItem
          onClick={handleDeleteMenuClick}
          sx={{ color: 'error.main', gap: 1.5 }}
        >
          <ListItemIcon sx={{ color: 'inherit', minWidth: 'unset' }}>
            <Trash2 size={14} />
          </ListItemIcon>
          {t('common.delete')}
        </MenuItem>
      </Menu>

      <Menu
        anchorEl={languageMenuAnchor}
        open={!!languageMenuAnchor}
        onClose={handleLanguageMenuClose}
        slotProps={{ paper: { sx: { minWidth: 160 } } }}
      >
        {Object.values(Language).map(language => (
          <MenuItem
            key={language}
            selected={i18n.language === language}
            onClick={() => handleLanguageSelect(language)}
          >
            {LANGUAGE_NAMES[language] ?? LANGUAGE_NAMES[DEFAULT_LANGUAGE]}
          </MenuItem>
        ))}
      </Menu>

      <ConfirmDialog
        open={logoutDialogOpen}
        title={t('sidebar.signOutConfirmTitle')}
        description={t('sidebar.signOutConfirmDescription')}
        confirmLabel={t('sidebar.signOut')}
        cancelLabel={t('common.cancel')}
        onConfirm={handleLogoutConfirm}
        onCancel={() => setLogoutDialogOpen(false)}
      />

      <ConfirmDialog
        open={!!deletingConversation}
        title={t('sidebar.deleteConversationTitle')}
        description={t('sidebar.deleteConversationDescription')}
        confirmLabel={t('common.delete')}
        cancelLabel={t('common.cancel')}
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeletingConversation(null)}
      />
    </Box>
  );
};

export default Sidebar;
