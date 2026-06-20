'use client';

import { getDefaultStore, Provider as JotaiProvider } from 'jotai';
import { NuqsAdapter } from 'nuqs/adapters/next/app';
import type { ReactNode } from 'react';
import { AuthProvider } from './auth';
import { QueryProvider } from './query';
import { ThemeProvider } from './theme';

export function Providers({ children }: { children: ReactNode }) {
  return (
    <NuqsAdapter>
      <QueryProvider>
        <JotaiProvider store={getDefaultStore()}>
          <ThemeProvider>
            <AuthProvider>{children}</AuthProvider>
          </ThemeProvider>
        </JotaiProvider>
      </QueryProvider>
    </NuqsAdapter>
  );
}
