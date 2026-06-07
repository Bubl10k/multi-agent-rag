import { Box, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';

const HomePage = () => {
  const { t } = useTranslation();
  return (
    <Box
      sx={{
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
      }}
    >
      <Typography variant="h6" color="text.secondary">
        {t('home.subtitle')}
      </Typography>
    </Box>
  );
};

export default HomePage;
