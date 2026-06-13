'use client';

import { useAtomValue, useSetAtom } from 'jotai';
import { CheckCircle2, Info, X, XCircle } from 'lucide-react';
import { useTranslations } from '@/hooks/use-translations';
import { cn } from '@/lib/utils';
import type { Toast, ToastVariant } from '@/stores/toast';
import { toastsAtom } from '@/stores/toast';

const variantConfig: Record<ToastVariant, { icon: React.ComponentType<{ className?: string }>; classes: string }> = {
  success: {
    icon: CheckCircle2,
    classes: 'bg-[#faf8f5] border-green-600/30 text-green-700',
  },
  error: {
    icon: XCircle,
    classes: 'bg-[#faf8f5] border-red-600/30 text-red-700',
  },
  info: {
    icon: Info,
    classes: 'bg-[#faf8f5] border-stone-200 text-stone-700',
  },
};

function ToastItem({ t, onDismiss }: { t: Toast; onDismiss: () => void }) {
  const { icon: Icon, classes } = variantConfig[t.variant];
  const d = useTranslations();
  return (
    <output
      aria-live="polite"
      aria-atomic="true"
      className={cn(
        'flex items-start gap-3 rounded-xl border px-4 py-3 shadow-sm',
        'motion-safe:animate-in motion-safe:fade-in-0 motion-safe:slide-in-from-bottom-2 duration-150',
        classes,
      )}
    >
      <Icon className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
      <p className="flex-1 text-sm leading-snug">{t.message}</p>
      <button
        type="button"
        onClick={onDismiss}
        aria-label={d.toasts.close}
        className="ml-1 shrink-0 rounded-md p-0.5 opacity-60 transition-opacity hover:opacity-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-current"
      >
        <X className="size-3.5" aria-hidden="true" />
      </button>
    </output>
  );
}

export function Toaster() {
  const toasts = useAtomValue(toastsAtom);
  const setToasts = useSetAtom(toastsAtom);
  const d = useTranslations();

  if (toasts.length === 0) return null;

  const dismiss = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <section
      aria-live="polite"
      aria-label={d.toasts.notifications}
      className="fixed bottom-4 right-4 z-[100] flex w-[min(360px,calc(100vw-2rem))] flex-col gap-2"
    >
      {toasts.map((t) => (
        <ToastItem key={t.id} t={t} onDismiss={() => dismiss(t.id)} />
      ))}
    </section>
  );
}
