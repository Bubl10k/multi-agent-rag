import { Box, Typography } from '@mui/material';

const HomePage = () => (
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
      Select an agent to start a conversation
    </Typography>
  </Box>
);

export default HomePage;