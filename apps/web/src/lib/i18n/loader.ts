import { en } from './locales/en';
import type { Messages } from './locales/ko';
import { ko } from './locales/ko';
import type { Locale } from './types';
import { DEFAULT_LOCALE } from './types';

/**
 * Returns the message dictionary for the given locale.
 * Falls back to DEFAULT_LOCALE (ko) when the locale is unknown.
 */
export function getDictionary(locale: Locale | string): Messages {
  switch (locale) {
    case 'en':
      return en;
    default:
      return ko;
  }
}

/**
 * Returns the default (ko) dictionary — safe to call anywhere including tests.
 */
export function getDefaultDictionary(): Messages {
  return ko;
}

export type { Messages };
export { DEFAULT_LOCALE };
