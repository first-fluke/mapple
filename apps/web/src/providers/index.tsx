'use client';

import { Provider as JotaiProvider } from 'jotai';
import { NuqsAdapter } from 'nuqs/adapters/next/app';
import type { ReactNode } from 'react';
import { QueryProvider } from './query';

export function Providers({ children }: { children: ReactNode }) {
  return (
    <NuqsAdapter>
      <QueryProvider>
        <JotaiProvider>{children}</JotaiProvider>
      </QueryProvider>
    </NuqsAdapter>
  );
}
