import { createStore } from 'jotai';
import { describe, expect, it } from 'vitest';
import { authBootstrappedAtom, authGateAtom, tokenAtom } from '@/lib/auth/atoms';

const futureExp = () => Math.floor(Date.now() / 1000) + 900;
const pastExp = () => Math.floor(Date.now() / 1000) - 900;

describe('authGateAtom', () => {
  it('reports "loading" before bootstrap finishes, even with a valid token', () => {
    const store = createStore();
    store.set(tokenAtom, { access: 'a', refresh: 'r', exp: futureExp() });
    expect(store.get(authGateAtom)).toBe('loading');
  });

  it('reports "unauthenticated" once bootstrapped with no token', () => {
    const store = createStore();
    store.set(authBootstrappedAtom, true);
    expect(store.get(authGateAtom)).toBe('unauthenticated');
  });

  it('reports "authenticated" once bootstrapped with a valid token', () => {
    const store = createStore();
    store.set(authBootstrappedAtom, true);
    store.set(tokenAtom, { access: 'a', refresh: 'r', exp: futureExp() });
    expect(store.get(authGateAtom)).toBe('authenticated');
  });

  it('reports "unauthenticated" once bootstrapped with an expired token', () => {
    const store = createStore();
    store.set(authBootstrappedAtom, true);
    store.set(tokenAtom, { access: 'a', refresh: 'r', exp: pastExp() });
    expect(store.get(authGateAtom)).toBe('unauthenticated');
  });
});
