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
