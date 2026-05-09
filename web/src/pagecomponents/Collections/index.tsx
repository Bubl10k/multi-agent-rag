import { useState } from 'react';
import {
  Box,
  Button,
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
import { Files, Pencil, Plus, Trash2 } from 'lucide-react';

import ConfirmDialog from '@/components/ConfirmDialog';
import {
  useDeleteCollectionMutation,
  useGetCollectionsQuery,
} from '@/api/endpoints/collection';
import type { CollectionRead } from '@/api/types/collection';
import CollectionFormDialog from './components/CollectionFormDialog.tsx';
import CollectionFilesDialog from './components/CollectionFilesDialog.tsx';

const CollectionsPage = () => {
  const { data: collections = [], isLoading } = useGetCollectionsQuery();
  const [deleteCollection] = useDeleteCollectionMutation();

  const [addOpen, setAddOpen] = useState(false);
  const [editingCollection, setEditingCollection] =
    useState<CollectionRead | null>(null);
  const [deletingCollection, setDeletingCollection] =
    useState<CollectionRead | null>(null);
  const [filesCollection, setFilesCollection] = useState<CollectionRead | null>(
    null,
  );

  const handleDeleteConfirm = async () => {
    if (!deletingCollection) return;
    await deleteCollection(deletingCollection.id);
    setDeletingCollection(null);
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
          Collections
        </Typography>
        <Button
          variant="contained"
          startIcon={<Plus size={16} />}
          onClick={() => setAddOpen(true)}
        >
          Add collection
        </Button>
      </Box>

      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : collections.length === 0 ? (
        <Box sx={{ py: 8, textAlign: 'center' }}>
          <Typography color="text.secondary">
            No collections yet. Create one to start uploading documents.
          </Typography>
        </Box>
      ) : (
        <TableContainer component={Paper} variant="outlined">
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Embedding Model</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {collections.map(collection => (
                <TableRow key={collection.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight={500}>
                      {collection.name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">
                      {collection.description ?? '—'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">
                      {collection.embedding_model}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="Files">
                      <IconButton
                        size="small"
                        onClick={() => setFilesCollection(collection)}
                      >
                        <Files size={15} />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Edit">
                      <IconButton
                        size="small"
                        onClick={() => setEditingCollection(collection)}
                        sx={{ ml: 0.5 }}
                      >
                        <Pencil size={15} />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton
                        size="small"
                        onClick={() => setDeletingCollection(collection)}
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

      <CollectionFormDialog open={addOpen} onClose={() => setAddOpen(false)} />

      <CollectionFormDialog
        open={!!editingCollection}
        collection={editingCollection ?? undefined}
        onClose={() => setEditingCollection(null)}
      />

      <CollectionFilesDialog
        open={!!filesCollection}
        collection={filesCollection}
        onClose={() => setFilesCollection(null)}
      />

      <ConfirmDialog
        open={!!deletingCollection}
        title="Delete collection"
        description={`"${deletingCollection?.name}" and all its documents will be permanently deleted.`}
        confirmLabel="Delete"
        cancelLabel="Cancel"
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeletingCollection(null)}
      />
    </Box>
  );
};

export default CollectionsPage;
