import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import en from './locales/en';
import uk from './locales/uk';
import { DEFAULT_LANGUAGE, Language } from '@/types/i18n';
import { localStorageService } from '@/utils/localStorage';

const storedLanguage = localStorageService.getLanguage();
const initialLanguage = Object.values(Language).includes(
  storedLanguage as Language,
)
  ? (storedLanguage as Language)
  : DEFAULT_LANGUAGE;

i18n.use(initReactI18next).init({
  resources: {
    [Language.EN]: { translation: en },
    [Language.UK]: { translation: uk },
  },
  lng: initialLanguage,
  fallbackLng: DEFAULT_LANGUAGE,
  interpolation: {
    escapeValue: false,
  },
});

export const changeLanguage = (language: Language): void => {
  localStorageService.setLanguage(language);
  void i18n.changeLanguage(language);
};

export default i18n;
