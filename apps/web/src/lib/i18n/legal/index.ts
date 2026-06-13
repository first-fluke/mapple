import type { Locale } from '../types';
import { privacyEn } from './privacy.en';
import { privacyKo } from './privacy.ko';
import { termsEn } from './terms.en';
import { termsKo } from './terms.ko';
import type { LegalDoc, LegalDocName } from './types';

export type { LegalDoc, LegalDocName, LegalSection } from './types';

/**
 * Returns the structured legal document content for the given locale and doc name.
 * Falls back to Korean when the locale is not explicitly supported.
 */
export function getLegalContent(locale: Locale | string, doc: LegalDocName): LegalDoc {
  switch (doc) {
    case 'privacy':
      return locale === 'en' ? privacyEn : privacyKo;
    case 'terms':
      return locale === 'en' ? termsEn : termsKo;
  }
}
