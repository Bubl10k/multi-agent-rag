import { Box, Typography } from '@mui/material';
import type { ReactNode } from 'react';

type AuthCardProps = {
  title: string;
  children: ReactNode;
};

const AuthCard = ({ title, children }: AuthCardProps) => (
  <Box
    sx={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      bgcolor: 'background.default',
      px: 2,
    }}
  >
    <Box
      sx={{
        width: '100%',
        maxWidth: 400,
        bgcolor: 'background.paper',
        borderRadius: 3,
        border: '1px solid',
        borderColor: 'divider',
        p: 4,
        display: 'flex',
        flexDirection: 'column',
        gap: 2.5,
      }}
    >
      <Typography variant="h5" fontWeight={700}>
        {title}
      </Typography>
      {children}
    </Box>
  </Box>
);

export default AuthCard;