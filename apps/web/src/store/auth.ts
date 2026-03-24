import { atom } from 'jotai';

export interface User {
  id: string;
  email: string;
  name: string;
  image: string | null;
}

export const userAtom = atom<User | null>(null);
export const authLoadingAtom = atom(true);
