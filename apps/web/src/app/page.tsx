'use client';

import { Suspense } from 'react';
import { GlobeDynamic, GlobeErrorBoundary, GlobeSkeleton } from '@/components/globe';
import { useWindowSize } from '@/hooks/use-window-size';

const SAMPLE_PINS = [
  { id: '1', lat: 37.5665, lng: 126.978, name: 'Seoul' },
  { id: '2', lat: 35.6762, lng: 139.6503, name: 'Tokyo' },
  { id: '3', lat: 40.7128, lng: -74.006, name: 'New York' },
];

export default function Home() {
  const size = useWindowSize();

  return (
    <main className="relative h-screen w-screen overflow-hidden bg-background">
      <GlobeErrorBoundary>
        <Suspense fallback={<GlobeSkeleton />}>
          <GlobeDynamic pins={SAMPLE_PINS} width={size?.width} height={size?.height} />
        </Suspense>
      </GlobeErrorBoundary>
    </main>
  );
}
