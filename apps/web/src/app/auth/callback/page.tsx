'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { Suspense, useEffect, useRef, useState } from 'react';
import { api } from '@/lib/api';
import type { TokenResponse } from '@/lib/auth';
import { setTokens } from '@/lib/auth';

function CallbackHandler() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const exchanged = useRef(false);

  useEffect(() => {
    if (exchanged.current) return;
    exchanged.current = true;

    const code = searchParams.get('code');
    const state = searchParams.get('state');

    if (!code || !state) {
      setError('Missing authorization code or state');
      return;
    }

    const provider = state === 'google' || state === 'github' ? state : null;
    if (!provider) {
      setError('Invalid OAuth provider');
      return;
    }

    const callbackUrl = `${window.location.origin}/auth/callback`;

    api
      .post<TokenResponse>('/auth/token', {
        provider,
        code,
        redirect_uri: callbackUrl,
      })
      .then((result) => {
        setTokens(result.data.access_token, result.data.refresh_token, result.data.expires_in);
        router.replace('/');
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : 'Authentication failed');
      });
  }, [searchParams, router]);

  if (error) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-4">
        <p className="text-destructive">{error}</p>
        <a href="/login" className="text-sm text-muted-foreground underline">
          Back to login
        </a>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen items-center justify-center">
      <p className="text-muted-foreground">Signing in...</p>
    </main>
  );
}

export default function CallbackPage() {
  return (
    <Suspense
      fallback={
        <main className="flex min-h-screen items-center justify-center">
          <p className="text-muted-foreground">Loading...</p>
        </main>
      }
    >
      <CallbackHandler />
    </Suspense>
  );
}
