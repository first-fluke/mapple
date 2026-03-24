<<<<<<< HEAD
import { atom } from 'jotai';

export interface User {
  id: string;
  email: string;
  name: string;
  image: string | null;
}

export const userAtom = atom<User | null>(null);
export const authLoadingAtom = atom(true);
=======
export {};
>>>>>>> 2c83c4e (feat(web,api): integrate better-auth for authentication)
