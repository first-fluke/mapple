'use client';

import { useTranslations } from '@/hooks/use-translations';

export function GlobeSkeleton() {
  const d = useTranslations();
  return (
    <output
      className="flex h-full w-full items-center justify-center"
      style={{ background: '#1c1917' }}
      aria-busy="true"
      aria-label={d.globe.loadingAriaLabel}
    >
      <div className="relative flex items-center justify-center">
        {/* Outer warm atmosphere glow */}
        <div
          className="absolute animate-pulse rounded-full opacity-20"
          style={{
            width: 480,
            height: 480,
            background: 'radial-gradient(circle, #d97706 0%, transparent 70%)',
          }}
        />
        {/* Globe sphere placeholder */}
        <div
          className="animate-pulse rounded-full"
          style={{
            width: 320,
            height: 320,
            background: 'radial-gradient(circle at 35% 38%, #44403c 0%, #292524 45%, #1c1917 100%)',
          }}
        />
        {/* Subtle outline ring */}
        <div
          className="absolute rounded-full border opacity-20"
          style={{
            width: 320,
            height: 320,
            borderColor: '#78716c',
          }}
        />
      </div>
    </output>
  );
}
