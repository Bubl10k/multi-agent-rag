import { Box, Button, Typography } from '@mui/material';
import { FileQuestion } from 'lucide-react';
import { useNavigate } from 'react-router';

import { ROUTES } from '@/router/router';

const NotFound = () => {
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
        404 — Page not found
      </Typography>
      <Typography variant="body2">
        The page you're looking for doesn't exist.
      </Typography>
      <Button
        variant="outlined"
        size="small"
        sx={{ mt: 1 }}
        onClick={() => navigate(ROUTES.HOME)}
      >
        Go home
      </Button>
    </Box>
  );
};

export default NotFound;