import { atomWithStorage } from 'jotai/utils';
import type { Locale } from './types';
import { DEFAULT_LOCALE } from './types';

/**
 * User's chosen locale, persisted to a cookie-like localStorage key.
 * Defaults to 'ko' (Korean).
 */
export const localeAtom = atomWithStorage<Locale>('globe-crm:locale', DEFAULT_LOCALE);
