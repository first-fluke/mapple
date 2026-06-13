'use client';

import { useSetAtom } from 'jotai';
import { useCallback } from 'react';
import type { ToastVariant } from '@/stores/toast';
import { createToast, toastsAtom } from '@/stores/toast';

const TOAST_DURATION_MS = 4000;

export function useToast() {
  const setToasts = useSetAtom(toastsAtom);

  const toast = useCallback(
    (message: string, variant: ToastVariant = 'info') => {
      const t = createToast(message, variant);
      setToasts((prev) => [...prev, t]);
      setTimeout(() => {
        setToasts((prev) => prev.filter((x) => x.id !== t.id));
      }, TOAST_DURATION_MS);
    },
    [setToasts],
  );

  const success = useCallback((message: string) => toast(message, 'success'), [toast]);
  const error = useCallback((message: string) => toast(message, 'error'), [toast]);

  return { toast, success, error };
}
