import { Backdrop, CircularProgress } from '@mui/material';

type Props = {
  background?: string;
  color?: string;
  loaderSize?: number;
};

const LoadingScreen = ({ background, color, loaderSize }: Props) => {
  return (
    <Backdrop
      sx={{
        color: color ? color : theme => theme.palette.primary.main,
        backgroundColor: background
          ? background
          : theme => theme.palette.background.default,
        zIndex: 9999,
      }}
      open={true}
    >
      <CircularProgress color="inherit" size={loaderSize} />
    </Backdrop>
  );
};

export default LoadingScreen;
