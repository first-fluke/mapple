'use client';

import dynamic from 'next/dynamic';
import { GlobeSkeleton } from './globe-skeleton';
import type { GlobeViewProps } from './globe-view';

export const GlobeDynamic = dynamic<GlobeViewProps>(() => import('./globe-view').then((mod) => mod.GlobeView), {
  ssr: false,
  loading: () => <GlobeSkeleton />,
});
