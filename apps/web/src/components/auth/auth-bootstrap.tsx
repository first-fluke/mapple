'use client';

import { getDefaultStore } from 'jotai';
import { useEffect } from 'react';
import { clearTokens, setTokens } from '@/lib/auth/api-client';
import { authBootstrappedAtom, tokenAtom } from '@/lib/auth/atoms';
import { subscribeAuthEvents } from '@/lib/auth/broadcast';
import { decodeAccessExp } from '@/lib/auth/jwt';
import { loadRefresh, REFRESH_STORAGE_KEY } from '@/lib/auth/storage';

const store = getDefaultStore();

function readFragmentTokens(): { access: string; refresh: string; exp: number } | null {
  if (typeof window === 'undefined') return null;
  const raw = window.location.hash.slice(1);
  if (!raw) return null;
  const params = new URLSearchParams(raw);
  const access = params.get('access');
  const refresh = params.get('refresh');
  if (!access || !refresh) return null;
  const expParam = params.get('exp');
  const exp = expParam ? Number(expParam) : (decodeAccessExp(access) ?? 0);
  return { access, refresh, exp };
}

function clearLocationHash(): void {
  if (typeof window === 'undefined') return;
  const url = window.location.pathname + window.location.search;
  window.history.replaceState({}, '', url);
}

async function tryRestoreFromRefresh(): Promise<void> {
  const refresh = loadRefresh();
  if (!refresh) return;
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    });
    if (!res.ok) {
      clearTokens({ broadcast: false });
      return;
    }
    const data = (await res.json()) as { access: string; refresh: string; exp: number };
    setTokens(data, { broadcast: false });
  } catch {
    clearTokens({ broadcast: false });
  }
}

export function AuthBootstrap() {
  useEffect(() => {
    const fragment = readFragmentTokens();
    if (fragment) {
      setTokens(fragment, { broadcast: true });
      clearLocationHash();
      store.set(authBootstrappedAtom, true);
    } else if (!store.get(tokenAtom)) {
      void tryRestoreFromRefresh().finally(() => {
        store.set(authBootstrappedAtom, true);
      });
    } else {
      store.set(authBootstrappedAtom, true);
    }

    const unsubscribe = subscribeAuthEvents((event) => {
      if (event.type === 'tokens') {
        setTokens(event.tokens, { broadcast: false });
      } else if (event.type === 'logout') {
        clearTokens({ broadcast: false });
      }
    });

    const onStorage = (e: StorageEvent) => {
      if (e.key !== REFRESH_STORAGE_KEY) return;
      if (!e.newValue) clearTokens({ broadcast: false });
    };
    window.addEventListener('storage', onStorage);

    return () => {
      unsubscribe();
      window.removeEventListener('storage', onStorage);
    };
  }, []);

  return null;
}
