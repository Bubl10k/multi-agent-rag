import { Link, useNavigate } from 'react-router';
import { Typography } from '@mui/material';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { toast } from 'react-toastify';

import { registerSchema, type RegisterFormValues } from '@/validation/auth';
import { useRegisterMutation } from '@/api/endpoints/auth';
import { ROUTES } from '@/router/router';
import AuthCard from '../AuthCard';
import FormTextField from '@/components/Form/FormTextField';
import SubmitButton from '@/components/Form/SubmitButton';

const RegisterPage = () => {
  const navigate = useNavigate();
  const [register, { isLoading }] = useRegisterMutation();

  const { control, handleSubmit } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { email: '', password: '', confirmPassword: '' },
  });

  const onSubmit = async ({ email, password }: RegisterFormValues) => {
    try {
      await register({ email, password }).unwrap();
      toast.success('Account created! Please sign in.');
      navigate(ROUTES.LOGIN);
    } catch (err: any) {
      const detail = err?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : 'Registration failed');
    }
  };

  return (
    <AuthCard title="Sign up">
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
          autoComplete="new-password"
          sx={{ mb: 2.5 }}
        />
        <FormTextField
          name="confirmPassword"
          control={control}
          label="Confirm password"
          type="password"
          autoComplete="new-password"
          sx={{ mb: 2.5 }}
        />
        <SubmitButton isLoading={isLoading}>Sign up</SubmitButton>
      </form>

      <Typography variant="body2" color="text.secondary" textAlign="center">
        Already have an account?{' '}
        <Link to={ROUTES.LOGIN} style={{ color: 'inherit', fontWeight: 600 }}>
          Sign in
        </Link>
      </Typography>
    </AuthCard>
  );
};

export default RegisterPage;