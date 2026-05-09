import { useRef, useState } from 'react';
import {
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  List,
  ListItem,
  ListItemText,
  Typography,
} from '@mui/material';
import { FileUp } from 'lucide-react';

import {
  useGetCollectionFilesQuery,
  useUploadDocumentMutation,
} from '@/api/endpoints/documents.ts';
import type { CollectionRead } from '@/api/types/collection.ts';

type Props = {
  open: boolean;
  collection: CollectionRead | null;
  onClose: () => void;
};

const CollectionFilesDialog = ({ open, collection, onClose }: Props) => {
  const [uploadDocument, { isLoading: isUploading }] =
    useUploadDocumentMutation();
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { data, isLoading: isLoadingFiles } = useGetCollectionFilesQuery(
    collection?.name ?? '',
    { skip: !open || !collection },
  );

  const handleFiles = async (files: FileList | null) => {
    if (!files || !collection) return;
    for (const file of Array.from(files)) {
      await uploadDocument({ collectionName: collection.name, file });
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    handleFiles(e.dataTransfer.files);
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle sx={{ pb: 1 }}>Files — {collection?.name}</DialogTitle>
      <DialogContent>
        <Box
          onDragOver={e => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          sx={{
            border: '2px dashed',
            borderColor: dragOver ? 'primary.main' : 'divider',
            borderRadius: 2,
            p: 4,
            textAlign: 'center',
            cursor: 'pointer',
            transition: 'border-color 0.2s',
            bgcolor: dragOver ? 'action.hover' : 'transparent',
            '&:hover': { borderColor: 'primary.light' },
          }}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            hidden
            onChange={e => handleFiles(e.target.files)}
          />
          {isUploading ? (
            <CircularProgress size={28} />
          ) : (
            <>
              <FileUp size={28} style={{ opacity: 0.5 }} />
              <Typography variant="body2" color="text.secondary" mt={1}>
                Click or drag files here to upload
              </Typography>
            </>
          )}
        </Box>

        <Box mt={2}>
          <Divider sx={{ mb: 1.5 }} />
          <Typography variant="caption" color="text.secondary" fontWeight={600}>
            FILES IN COLLECTION
          </Typography>
          {isLoadingFiles ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
              <CircularProgress size={22} />
            </Box>
          ) : !data?.files.length ? (
            <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
              No files uploaded yet.
            </Typography>
          ) : (
            <List dense disablePadding>
              {data.files.map((name, i) => (
                <ListItem key={i} disableGutters>
                  <ListItemText
                    primary={name}
                    primaryTypographyProps={{ variant: 'body2' }}
                  />
                </ListItem>
              ))}
            </List>
          )}
        </Box>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2.5 }}>
        <Button onClick={onClose} variant="outlined" fullWidth>
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CollectionFilesDialog;
