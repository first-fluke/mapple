'use client';

import { atom } from 'jotai';

export type ToastVariant = 'success' | 'error' | 'info';

export interface Toast {
  id: string;
  message: string;
  variant: ToastVariant;
}

export const toastsAtom = atom<Toast[]>([]);

export function createToast(message: string, variant: ToastVariant): Toast {
  return { id: crypto.randomUUID(), message, variant };
}
