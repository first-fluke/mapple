import { getDefaultStore } from 'jotai';
import { clearTokens, getApiBaseUrl } from './api-client';
import { tokenAtom } from './atoms';
import { loadRefresh } from './storage';

const store = getDefaultStore();

export async function logout(): Promise<void> {
  const current = store.get(tokenAtom);
  const refresh = current?.refresh ?? loadRefresh();

  if (refresh) {
    try {
      await fetch(`${getApiBaseUrl()}/auth/logout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh }),
      });
    } catch {
      // best effort — clear local tokens regardless
    }
  }

  clearTokens();
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
  }
}
