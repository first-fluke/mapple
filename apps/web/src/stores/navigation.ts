import { atom } from 'jotai';

/** Contact ID that the Globe should fly-to when navigating back from Graph */
export const globeFlyToAtom = atom<string | null>(null);

/** Whether a cross-tab transition animation is in progress */
export const crossTabTransitionAtom = atom<boolean>(false);
