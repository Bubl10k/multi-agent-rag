import { useMemo } from 'react';
import { Link, useNavigate } from 'react-router';
import { Typography } from '@mui/material';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useTranslation } from 'react-i18next';
import { toast } from 'react-toastify';

import { getLoginSchema, type LoginFormValues } from '@/validation/auth';
import { useLoginMutation } from '@/api/endpoints/auth';
import { useActions } from '@/hooks/useActions';
import { ROUTES } from '@/router/router';
import AuthCard from '../AuthCard';
import FormTextField from '@/components/Form/FormTextField';
import SubmitButton from '@/components/Form/SubmitButton';

const LoginPage = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { setCredentials } = useActions();
  const [login, { isLoading }] = useLoginMutation();

  const loginSchema = useMemo(() => getLoginSchema(t), [t]);
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
    } catch (err: any) {
      const detail = err?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : t('auth.login.genericError'));
    }
  };

  return (
    <AuthCard title={t('auth.login.title')}>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <FormTextField
          name="email"
          control={control}
          label={t('auth.login.email')}
          type="email"
          autoComplete="email"
          sx={{ mb: 2.5 }}
        />
        <FormTextField
          name="password"
          control={control}
          label={t('auth.login.password')}
          type="password"
          autoComplete="current-password"
          sx={{ mb: 2.5 }}
        />
        <SubmitButton isLoading={isLoading}>{t('auth.login.submit')}</SubmitButton>
      </form>

      <Typography variant="body2" color="text.secondary" textAlign="center">
        {t('auth.login.noAccount')}{' '}
        <Link
          to={ROUTES.REGISTER}
          style={{ color: 'inherit', fontWeight: 600 }}
        >
          {t('auth.login.signUp')}
        </Link>
      </Typography>
    </AuthCard>
  );
};

export default LoginPage;
