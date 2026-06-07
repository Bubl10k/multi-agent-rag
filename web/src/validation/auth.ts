import { z } from 'zod';
import type { TFunction } from 'i18next';

export const getLoginSchema = (t: TFunction) =>
  z.object({
    email: z.string().email(t('auth.validation.invalidEmail')),
    password: z.string().min(1, t('auth.validation.passwordRequired')),
  });

export const getRegisterSchema = (t: TFunction) =>
  z
    .object({
      email: z.string().email(t('auth.validation.invalidEmail')),
      password: z.string().min(8, t('auth.validation.passwordMinLength')),
      confirmPassword: z.string(),
    })
    .refine(data => data.password === data.confirmPassword, {
      message: t('auth.validation.passwordsDoNotMatch'),
      path: ['confirmPassword'],
    });

export type LoginFormValues = z.infer<ReturnType<typeof getLoginSchema>>;
export type RegisterFormValues = z.infer<ReturnType<typeof getRegisterSchema>>;
