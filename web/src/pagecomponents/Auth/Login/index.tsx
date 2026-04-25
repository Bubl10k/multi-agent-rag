import { Link, useNavigate } from 'react-router';
import { Typography } from '@mui/material';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { toast } from 'react-toastify';

import { loginSchema, type LoginFormValues } from '@/validation/auth';
import { useLoginMutation } from '@/api/endpoints/auth';
import { useActions } from '@/hooks/useActions';
import { ROUTES } from '@/router/router';
import AuthCard from '../AuthCard';
import FormTextField from '@/components/Form/FormTextField';
import SubmitButton from '@/components/Form/SubmitButton';

const LoginPage = () => {
  const navigate = useNavigate();
  const { setCredentials } = useActions();
  const [login, { isLoading }] = useLoginMutation();

  const { control, handleSubmit } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
  });

  const onSubmit = async ({ email, password }: LoginFormValues) => {
    try {
      const { access_token, refresh_token } = await login({
        email,
        password,
      }).unwrap();
      setCredentials({
        token: access_token,
        refreshToken: refresh_token,
        user: { id: '', email },
      });
      navigate(ROUTES.HOME);
    } catch {
      toast.error('Invalid email or password');
    }
  };

  return (
    <AuthCard title="Sign in">
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <FormTextField
          name="email"
          control={control}
          label="Email"
          type="email"
          autoComplete="email"
          sx={{ mb: 2.5 }}
        />
        <FormTextField
          name="password"
          control={control}
          label="Password"
          type="password"
          autoComplete="current-password"
          sx={{ mb: 2.5 }}
        />
        <SubmitButton isLoading={isLoading}>Sign in</SubmitButton>
      </form>

      <Typography variant="body2" color="text.secondary" textAlign="center">
        Don&apos;t have an account?{' '}
        <Link
          to={ROUTES.REGISTER}
          style={{ color: 'inherit', fontWeight: 600 }}
        >
          Sign up
        </Link>
      </Typography>
    </AuthCard>
  );
};

export default LoginPage;
