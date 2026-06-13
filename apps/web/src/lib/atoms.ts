import type { GlobeMode } from '@globe-crm/types';
import { atom } from 'jotai';

export type { GlobeMode };

export const globeModeAtom = atom<GlobeMode>('explore');
