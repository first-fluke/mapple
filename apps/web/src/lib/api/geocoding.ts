import { api } from './client';

export interface ReverseGeocodeResult {
  country: string | null;
  city: string | null;
  display_name: string | null;
}

export const geocodingApi = {
  reverse: (lat: number, lng: number) => api.get<ReverseGeocodeResult>(`/geocoding/reverse?lat=${lat}&lng=${lng}`),
};
