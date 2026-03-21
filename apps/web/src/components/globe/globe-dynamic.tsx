'use client';

import dynamic from 'next/dynamic';
import { GlobeSkeleton } from './globe-skeleton';

export const GlobeDynamic = dynamic(() => import('./globe-view').then((mod) => mod.GlobeView), {
  ssr: false,
  loading: () => <GlobeSkeleton />,
});
