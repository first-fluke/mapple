'use client';

import { useCallback, useEffect, useState } from 'react';

const STORAGE_KEY = 'globe-crm-prefer-list-view';

/**
 * Detects screen reader preference and provides a toggle for list view fallback.
 *
 * Since browsers intentionally do not expose screen reader status for privacy,
 * we use `prefers-reduced-motion` as a heuristic signal and allow explicit opt-in
 * via a persistent toggle stored in localStorage.
 */
export function useScreenReader() {
  const [prefersListView, setPrefersListView] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored !== null) {
      setPrefersListView(stored === 'true');
    }

    const mql = window.matchMedia('(prefers-reduced-motion: reduce)');
    setReducedMotion(mql.matches);

    const onChange = (e: MediaQueryListEvent) => setReducedMotion(e.matches);
    mql.addEventListener('change', onChange);
    return () => mql.removeEventListener('change', onChange);
  }, []);

  const toggleListView = useCallback(() => {
    setPrefersListView((prev) => {
      const next = !prev;
      localStorage.setItem(STORAGE_KEY, String(next));
      return next;
    });
  }, []);

  return {
    /** Whether the user should see list view (explicit toggle OR reduced motion) */
    shouldUseListView: prefersListView || reducedMotion,
    /** Whether user explicitly toggled list view */
    prefersListView,
    /** Whether OS-level reduced motion is enabled */
    reducedMotion,
    /** Toggle between globe and list view */
    toggleListView,
  };
}
