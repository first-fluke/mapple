import { cookies } from 'next/headers';
import { getDictionary } from './loader';
import type { Messages } from './locales/ko';
import type { Locale } from './types';
import { DEFAULT_LOCALE, LOCALE_COOKIE, SUPPORTED_LOCALES } from './types';

/**
 * Reads the locale cookie from the incoming request and returns a validated
 * Locale value. Falls back to DEFAULT_LOCALE when the cookie is absent or
 * contains an unsupported value.
 *
 * This function must only be called inside Server Components or Route Handlers
 * (anywhere `next/headers` cookies() is available).
 */
export async function getServerLocale(): Promise<Locale> {
  const cookieStore = await cookies();
  const raw = cookieStore.get(LOCALE_COOKIE)?.value;
  if (raw && (SUPPORTED_LOCALES as string[]).includes(raw)) {
    return raw as Locale;
  }
  return DEFAULT_LOCALE;
}

/**
 * Convenience wrapper — returns the full message dictionary for the current
 * server-side locale. Equivalent to getDictionary(await getServerLocale()).
 */
export async function getServerDictionary(): Promise<Messages> {
  const locale = await getServerLocale();
  return getDictionary(locale);
}
