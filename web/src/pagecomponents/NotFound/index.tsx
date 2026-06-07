import { Box, Button, Typography } from '@mui/material';
import { FileQuestion } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';

import { ROUTES } from '@/router/router';

const NotFound = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  return (
    <Box
      sx={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 2,
        color: 'text.disabled',
        bgcolor: 'background.default',
      }}
    >
      <FileQuestion size={48} strokeWidth={1.2} />
      <Typography variant="h6" color="text.secondary" fontWeight={500}>
        {t('notFound.title')}
      </Typography>
      <Typography variant="body2">
        {t('notFound.description')}
      </Typography>
      <Button
        variant="outlined"
        size="small"
        sx={{ mt: 1 }}
        onClick={() => navigate(ROUTES.HOME)}
      >
        {t('notFound.backHome')}
      </Button>
    </Box>
  );
};

export default NotFound;
