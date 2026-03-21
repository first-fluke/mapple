'use client';

import { useQuery } from '@tanstack/react-query';
import { geocodingApi } from '@/lib/api/geocoding';

export function useReverseGeocode(lat: number | null, lng: number | null) {
  return useQuery({
    queryKey: ['geocoding', 'reverse', lat, lng],
    queryFn: async () => {
      const res = await geocodingApi.reverse(lat as number, lng as number);
      return res.data;
    },
    enabled: lat != null && lng != null,
  });
}
