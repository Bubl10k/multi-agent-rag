import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Button,
  Chip,
  CircularProgress,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
  Typography,
} from '@mui/material';
import { Network, Pencil, Plus, Trash2 } from 'lucide-react';

import ConfirmDialog from '@/components/ConfirmDialog';
import {
  useDeleteAgentMutation,
  useGetAgentsQuery,
} from '@/api/endpoints/agent';
import { AgentType, type AgentRead } from '@/api/types/agent';
import AgentFormDialog from './components/AgentFormDialog.tsx';
import AgentGraphDialog from './components/AgentGraphDialog.tsx';

const AgentsPage = () => {
  const { t } = useTranslation();

  const AGENT_TYPE_LABELS: Record<AgentType, string> = {
    [AgentType.GENERAL]: t('dashboard.agentTypeLabels.general'),
    [AgentType.PROGRAMMING]: t('dashboard.agentTypeLabels.programming'),
    [AgentType.MATH]: t('dashboard.agentTypeLabels.math'),
    [AgentType.RESEARCHER]: t('dashboard.agentTypeLabels.researcher'),
    [AgentType.INVOICE]: t('dashboard.agentTypeLabels.invoice'),
    [AgentType.ROUTER]: t('dashboard.agentTypeLabels.router'),
  };

  const { data: agents = [], isLoading } = useGetAgentsQuery();
  const [deleteAgent] = useDeleteAgentMutation();

  const [addOpen, setAddOpen] = useState(false);
  const [editingAgent, setEditingAgent] = useState<AgentRead | null>(null);
  const [deletingAgent, setDeletingAgent] = useState<AgentRead | null>(null);
  const [graphAgent, setGraphAgent] = useState<AgentRead | null>(null);

  const handleDeleteConfirm = async () => {
    if (!deletingAgent) return;
    await deleteAgent(deletingAgent.id);
    setDeletingAgent(null);
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1250, mx: 'auto' }}>
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 3,
        }}
      >
        <Typography variant="h5" fontWeight={600}>
          {t('agents.title')}
        </Typography>
        <Button
          variant="contained"
          startIcon={<Plus size={16} />}
          onClick={() => setAddOpen(true)}
        >
          {t('agents.addAgent')}
        </Button>
      </Box>

      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : agents.length === 0 ? (
        <Box sx={{ py: 8, textAlign: 'center' }}>
          <Typography color="text.secondary">
            {t('agents.noAgents')}
          </Typography>
        </Box>
      ) : (
        <TableContainer component={Paper} variant="outlined">
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>{t('agents.table.name')}</TableCell>
                <TableCell>{t('agents.table.type')}</TableCell>
                <TableCell>{t('agents.table.llmModel')}</TableCell>
                <TableCell>{t('agents.table.collections')}</TableCell>
                <TableCell>{t('agents.table.status')}</TableCell>
                <TableCell align="right">{t('agents.table.actions')}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {agents.map(agent => (
                <TableRow key={agent.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight={500}>
                      {agent.name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={AGENT_TYPE_LABELS[agent.agent_type]}
                      size="small"
                      variant="outlined"
                      color="primary"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">
                      {agent.platform_llm?.display_name ?? agent.llm?.model_name ?? '—'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {agent.collections.length === 0 ? (
                      <Typography variant="body2" color="text.secondary">
                        —
                      </Typography>
                    ) : (
                      <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                        {agent.collections.map(c => (
                          <Chip
                            key={c.id}
                            label={c.name}
                            size="small"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    )}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={agent.is_active ? t('agents.active') : t('agents.inactive')}
                      color={agent.is_active ? 'success' : 'default'}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title={t('agents.viewGraph')}>
                      <IconButton
                        size="small"
                        onClick={() => setGraphAgent(agent)}
                        sx={{ color: 'text.secondary' }}
                      >
                        <Network size={15} />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title={t('common.edit')}>
                      <IconButton
                        size="small"
                        onClick={() => setEditingAgent(agent)}
                        sx={{ ml: 0.5 }}
                      >
                        <Pencil size={15} />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title={t('common.delete')}>
                      <IconButton
                        size="small"
                        onClick={() => setDeletingAgent(agent)}
                        sx={{ color: 'error.main', ml: 0.5 }}
                      >
                        <Trash2 size={15} />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <AgentFormDialog open={addOpen} onClose={() => setAddOpen(false)} />

      <AgentFormDialog
        open={!!editingAgent}
        agent={editingAgent ?? undefined}
        onClose={() => setEditingAgent(null)}
      />

      <ConfirmDialog
        open={!!deletingAgent}
        title={t('agents.deleteConfirmTitle')}
        description={t('agents.deleteConfirmDescription', { name: deletingAgent?.name })}
        confirmLabel={t('common.delete')}
        cancelLabel={t('common.cancel')}
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeletingAgent(null)}
      />

      {graphAgent && (
        <AgentGraphDialog
          agentId={graphAgent.id}
          agentName={graphAgent.name}
          open={!!graphAgent}
          onClose={() => setGraphAgent(null)}
        />
      )}
    </Box>
  );
};

export default AgentsPage;
