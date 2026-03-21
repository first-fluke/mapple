import { atom } from 'jotai';

export interface CameraPosition {
  lat: number;
  lng: number;
  altitude: number;
}

const DEFAULT_CAMERA: CameraPosition = {
  lat: 37.5665,
  lng: 126.978,
  altitude: 2.5,
};

export const cameraAtom = atom<CameraPosition>(DEFAULT_CAMERA);
