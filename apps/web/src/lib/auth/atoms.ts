import { atom } from 'jotai';

export interface TokenSet {
  access: string;
  refresh: string;
  exp: number;
}

export const tokenAtom = atom<TokenSet | null>(null);

export const isAuthenticatedAtom = atom((get) => {
  const t = get(tokenAtom);
  if (!t) return false;
  return t.exp * 1000 > Date.now();
});

// True once AuthBootstrap has finished its initial token-restore attempt
// (fragment parse + refresh-token exchange). Until then route guards must
// not redirect, otherwise a valid session is bounced to /login on every
// hard refresh while the async refresh call is still in flight.
export const authBootstrappedAtom = atom(false);

export type AuthGate = 'loading' | 'authenticated' | 'unauthenticated';

export const authGateAtom = atom<AuthGate>((get) => {
  if (!get(authBootstrappedAtom)) return 'loading';
  return get(isAuthenticatedAtom) ? 'authenticated' : 'unauthenticated';
});
