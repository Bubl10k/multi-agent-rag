import { useMemo } from 'react';
import { Link, useNavigate } from 'react-router';
import { Typography } from '@mui/material';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useTranslation } from 'react-i18next';
import { toast } from 'react-toastify';

import { getRegisterSchema, type RegisterFormValues } from '@/validation/auth';
import { useRegisterMutation } from '@/api/endpoints/auth';
import { ROUTES } from '@/router/router';
import AuthCard from '../AuthCard';
import FormTextField from '@/components/Form/FormTextField';
import SubmitButton from '@/components/Form/SubmitButton';

const RegisterPage = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [register, { isLoading }] = useRegisterMutation();

  const registerSchema = useMemo(() => getRegisterSchema(t), [t]);
  const { control, handleSubmit } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { email: '', password: '', confirmPassword: '' },
  });

  const onSubmit = async ({ email, password }: RegisterFormValues) => {
    try {
      await register({ email, password }).unwrap();
      toast.success(t('auth.register.success'));
      navigate(ROUTES.LOGIN);
    } catch (err: any) {
      const detail = err?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : t('auth.register.genericError'));
    }
  };

  return (
    <AuthCard title={t('auth.register.title')}>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <FormTextField
          name="email"
          control={control}
          label={t('auth.register.email')}
          type="email"
          autoComplete="email"
          sx={{ mb: 2.5 }}
        />
        <FormTextField
          name="password"
          control={control}
          label={t('auth.register.password')}
          type="password"
          autoComplete="new-password"
          sx={{ mb: 2.5 }}
        />
        <FormTextField
          name="confirmPassword"
          control={control}
          label={t('auth.register.confirmPassword')}
          type="password"
          autoComplete="new-password"
          sx={{ mb: 2.5 }}
        />
        <SubmitButton isLoading={isLoading}>{t('auth.register.submit')}</SubmitButton>
      </form>

      <Typography variant="body2" color="text.secondary" textAlign="center">
        {t('auth.register.haveAccount')}{' '}
        <Link to={ROUTES.LOGIN} style={{ color: 'inherit', fontWeight: 600 }}>
          {t('auth.register.signIn')}
        </Link>
      </Typography>
    </AuthCard>
  );
};

export default RegisterPage;
