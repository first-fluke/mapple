'use client';

import { useAtomValue } from 'jotai';
import { useMemo } from 'react';
import { localeAtom } from '@/lib/i18n/atoms';
import { getDictionary } from '@/lib/i18n/loader';
import type { Messages } from '@/lib/i18n/locales/ko';

/**
 * Returns the full message dictionary for the current locale.
 *
 * Usage:
 *   const t = useTranslations();
 *   <h1>{t.nav.contacts}</h1>
 */
export function useTranslations(): Messages {
  const locale = useAtomValue(localeAtom);
  return useMemo(() => getDictionary(locale), [locale]);
}
