import { Button, CircularProgress, type ButtonProps } from '@mui/material';

type SubmitButtonProps = ButtonProps & {
  isLoading?: boolean;
};

const SubmitButton = ({
  isLoading,
  children,
  disabled,
  ...props
}: SubmitButtonProps) => (
  <Button
    type="submit"
    variant="contained"
    fullWidth
    disabled={isLoading || disabled}
    sx={{ py: 1.25, fontWeight: 600 }}
    {...props}
  >
    {isLoading ? <CircularProgress size={20} color="inherit" /> : children}
  </Button>
);

export default SubmitButton;
