'use client';

import { useAtom, useSetAtom } from 'jotai';
import { useEffect } from 'react';
import type { ThemeMode } from '@/lib/atoms/theme';
import { resolvedThemeAtom, themeModeAtom } from '@/lib/atoms/theme';

/**
 * Reads themeModeAtom, resolves system preference, and toggles .dark on <html>.
 * Must be rendered inside JotaiProvider.
 */
export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [themeMode] = useAtom(themeModeAtom);
  const setResolved = useSetAtom(resolvedThemeAtom);

  useEffect(() => {
    const root = document.documentElement;

    function apply(mode: ThemeMode) {
      let resolved: 'light' | 'dark';

      if (mode === 'system') {
        resolved = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      } else {
        resolved = mode;
      }

      root.classList.toggle('dark', resolved === 'dark');
      setResolved(resolved);
    }

    apply(themeMode);

    if (themeMode === 'system') {
      const mq = window.matchMedia('(prefers-color-scheme: dark)');
      const handler = () => apply('system');
      mq.addEventListener('change', handler);
      return () => mq.removeEventListener('change', handler);
    }
  }, [themeMode, setResolved]);

  return <>{children}</>;
}
