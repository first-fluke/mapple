'use client';

import { useAtomValue } from 'jotai';
import { useRouter } from 'next/navigation';
import { type ReactNode, useEffect } from 'react';
import { authGateAtom } from '@/lib/auth/atoms';

/**
 * Client-side route guard for protected (main) routes.
 *
 * Token auth lives in memory + localStorage (not cookies), so the proxy is a
 * pure pass-through and gating must happen in the React tree. While the initial
 * token restore is in flight the gate reports `loading` and we render a neutral
 * placeholder — never redirect — so a valid session survives a hard refresh.
 */
export function AuthGuard({ children }: { children: ReactNode }) {
  const router = useRouter();
  const gate = useAtomValue(authGateAtom);

  useEffect(() => {
    if (gate === 'unauthenticated') {
      router.replace('/login');
    }
  }, [gate, router]);

  if (gate !== 'authenticated') {
    return (
      <output aria-busy="true" aria-live="polite" className="flex h-screen items-center justify-center">
        <span className="sr-only">Loading</span>
        <span className="size-6 animate-spin rounded-full border-2 border-muted border-t-foreground" />
      </output>
    );
  }

  return <>{children}</>;
}
