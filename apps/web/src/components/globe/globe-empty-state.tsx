'use client';

import { MapPin } from 'lucide-react';
import { useTranslations } from '@/hooks/use-translations';

/**
 * Shown when the user has no geolocated contacts.
 * Uses Terrazzo warm-dark palette (Dark Earth background).
 */
export function GlobeEmptyState() {
  const t = useTranslations();

  return (
    <output
      className="flex h-full w-full flex-col items-center justify-center gap-5 rounded-xl p-8 text-center"
      style={{ background: '#1c1917' }}
      aria-label={t.globe.emptyAriaLabel}
    >
      {/* Icon cluster */}
      <div
        className="flex h-20 w-20 items-center justify-center rounded-full"
        style={{ background: '#292524', border: '1px solid #44403c' }}
      >
        <MapPin className="h-9 w-9" style={{ color: '#f97316' }} aria-hidden="true" />
      </div>

      <div className="max-w-xs">
        <p className="text-base font-semibold" style={{ color: '#faf8f5' }}>
          {t.globe.emptyTitle}
        </p>
        <p className="mt-2 text-sm leading-relaxed" style={{ color: '#a8a29e' }}>
          {t.globe.emptyDescription}
        </p>
      </div>
    </output>
  );
}
