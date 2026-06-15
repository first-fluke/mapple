import { atom } from 'jotai';

export type GlobeMode = 'explore' | 'select_location' | 'view_connections';

export const globeModeAtom = atom<GlobeMode>('explore');
