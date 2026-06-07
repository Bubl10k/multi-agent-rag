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
import { Pencil, Plus, Trash2 } from 'lucide-react';

import ConfirmDialog from '@/components/ConfirmDialog';
import { useDeleteLLMMutation, useGetLLMsQuery } from '@/api/endpoints/llm';
import type { LLMRead } from '@/api/types/llm';
import LLMFormDialog from './components/LLMFormDialog.tsx';

const LLMModelsPage = () => {
  const { t } = useTranslation();
  const { data: llms = [], isLoading } = useGetLLMsQuery();
  const [deleteLLM] = useDeleteLLMMutation();

  const [addOpen, setAddOpen] = useState(false);
  const [editingLLM, setEditingLLM] = useState<LLMRead | null>(null);
  const [deletingLLM, setDeletingLLM] = useState<LLMRead | null>(null);

  const handleDeleteConfirm = async () => {
    if (!deletingLLM) return;
    await deleteLLM(deletingLLM.id);
    setDeletingLLM(null);
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
          {t('llmModels.title')}
        </Typography>
        <Button
          variant="contained"
          startIcon={<Plus size={16} />}
          onClick={() => setAddOpen(true)}
        >
          {t('llmModels.addModel')}
        </Button>
      </Box>

      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : llms.length === 0 ? (
        <Box sx={{ py: 8, textAlign: 'center' }}>
          <Typography color="text.secondary">
            {t('llmModels.noModels')}
          </Typography>
        </Box>
      ) : (
        <TableContainer component={Paper} variant="outlined">
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>{t('llmModels.table.modelName')}</TableCell>
                <TableCell>{t('llmModels.table.status')}</TableCell>
                <TableCell align="right">{t('llmModels.table.actions')}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {llms.map(llm => (
                <TableRow key={llm.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight={500}>
                      {llm.model_name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={llm.is_active ? t('llmModels.active') : t('llmModels.inactive')}
                      color={llm.is_active ? 'success' : 'default'}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title={t('common.edit')}>
                      <IconButton
                        size="small"
                        onClick={() => setEditingLLM(llm)}
                      >
                        <Pencil size={15} />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title={t('common.delete')}>
                      <IconButton
                        size="small"
                        onClick={() => setDeletingLLM(llm)}
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

      <LLMFormDialog open={addOpen} onClose={() => setAddOpen(false)} />

      <LLMFormDialog
        open={!!editingLLM}
        llm={editingLLM ?? undefined}
        onClose={() => setEditingLLM(null)}
      />

      <ConfirmDialog
        open={!!deletingLLM}
        title={t('llmModels.deleteConfirmTitle')}
        description={t('llmModels.deleteConfirmDescription', { name: deletingLLM?.model_name })}
        confirmLabel={t('common.delete')}
        cancelLabel={t('common.cancel')}
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeletingLLM(null)}
      />
    </Box>
  );
};

export default LLMModelsPage;
