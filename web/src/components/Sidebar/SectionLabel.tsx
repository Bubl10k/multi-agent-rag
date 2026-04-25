import { Typography } from '@mui/material';

const SectionLabel = ({ children }: { children: string }) => (
  <Typography
    variant="caption"
    sx={{
      display: 'block',
      px: 1.5,
      py: 0.75,
      color: 'text.disabled',
      fontWeight: 600,
      textTransform: 'uppercase',
      letterSpacing: '0.06em',
      fontSize: '0.65rem',
      whiteSpace: 'nowrap',
    }}
  >
    {children}
  </Typography>
);

export default SectionLabel;