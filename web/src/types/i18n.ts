export enum Language {
  EN = 'en',
  UK = 'uk',
}

export const DEFAULT_LANGUAGE = Language.EN;

export const LANGUAGE_NAMES: Record<Language, string> = {
  [Language.EN]: 'English',
  [Language.UK]: 'Українська',
};
