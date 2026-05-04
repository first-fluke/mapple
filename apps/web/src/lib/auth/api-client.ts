import { getDefaultStore } from 'jotai';
import { type TokenSet, tokenAtom } from './atoms';
import { publishAuthEvent } from './broadcast';
import { decodeAccessExp } from './jwt';
import { clearRefresh, loadRefresh, saveRefresh } from './storage';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? '';

const store = getDefaultStore();

let refreshInflight: Promise<TokenSet | null> | null = null;

function tokensToSet(access: string, refresh: string, exp?: number): TokenSet {
  const resolvedExp = exp ?? decodeAccessExp(access) ?? Math.floor(Date.now() / 1000) + 900;
  return { access, refresh, exp: resolvedExp };
}

export function setTokens(tokens: TokenSet, opts?: { broadcast?: boolean }): void {
  store.set(tokenAtom, tokens);
  saveRefresh(tokens.refresh);
  if (opts?.broadcast !== false) {
    publishAuthEvent({ type: 'tokens', tokens });
  }
}

export function clearTokens(opts?: { broadcast?: boolean }): void {
  store.set(tokenAtom, null);
  clearRefresh();
  if (opts?.broadcast !== false) {
    publishAuthEvent({ type: 'logout' });
  }
}

async function callRefresh(refresh: string): Promise<TokenSet | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    });
    if (!res.ok) return null;
    const data = (await res.json()) as { access: string; refresh: string; exp: number };
    return tokensToSet(data.access, data.refresh, data.exp);
  } catch {
    return null;
  }
}

async function ensureFreshTokens(): Promise<TokenSet | null> {
  const current = store.get(tokenAtom);
  if (current && current.exp * 1000 > Date.now() + 5000) return current;

  const refresh = current?.refresh ?? loadRefresh();
  if (!refresh) return current;

  if (!refreshInflight) {
    refreshInflight = callRefresh(refresh).finally(() => {
      refreshInflight = null;
    });
  }
  const fresh = await refreshInflight;
  if (fresh) {
    setTokens(fresh);
    return fresh;
  }
  clearTokens();
  return null;
}

function buildUrl(input: RequestInfo | URL): RequestInfo | URL {
  if (typeof input === 'string' && input.startsWith('/')) {
    return `${API_BASE_URL}${input}`;
  }
  return input;
}

export async function apiFetch(input: RequestInfo | URL, init: RequestInit = {}): Promise<Response> {
  let tokens = await ensureFreshTokens();

  const headers = new Headers(init.headers);
  if (tokens?.access) {
    headers.set('Authorization', `Bearer ${tokens.access}`);
  }
  if (init.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  let response = await fetch(buildUrl(input), { ...init, headers });

  if (response.status === 401 && tokens) {
    clearTokens();
    tokens = await ensureFreshTokens();
    if (tokens?.access) {
      headers.set('Authorization', `Bearer ${tokens.access}`);
      response = await fetch(buildUrl(input), { ...init, headers });
    }
  }
  return response;
}

export function getApiBaseUrl(): string {
  return API_BASE_URL;
}
