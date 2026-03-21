import { atom } from 'jotai';
import type { User } from '@/lib/auth';

export const userAtom = atom<User | null>(null);
export const authLoadingAtom = atom(true);
