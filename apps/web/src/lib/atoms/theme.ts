import { atom } from 'jotai';
import { atomWithStorage } from 'jotai/utils';

export type ThemeMode = 'system' | 'light' | 'dark';

/**
 * User's explicit theme preference persisted to localStorage.
 * 'system' means follow prefers-color-scheme.
 */
export const themeModeAtom = atomWithStorage<ThemeMode>('globe-crm:theme', 'system');

/**
 * Resolved theme ('light' | 'dark') derived from themeMode + system preference.
 * Used by ThemeProvider to toggle the .dark class on <html>.
 * Write-only from ThemeProvider; do not read directly in components — use themeModeAtom.
 */
export const resolvedThemeAtom = atom<'light' | 'dark'>('light');
