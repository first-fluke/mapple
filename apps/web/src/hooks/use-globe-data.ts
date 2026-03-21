'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import type { GlobeData } from '@/lib/api/globe';

export interface BboxParams {
  swLat: number;
  swLng: number;
  neLat: number;
  neLng: number;
}

export function useGlobeData(bbox: BboxParams | null) {
  return useQuery({
    queryKey: ['globe-data', bbox],
    queryFn: async () => {
      if (!bbox) throw new Error('No bbox');
      const { data } = await api.get<GlobeData>(
        `/globe/data?sw_lat=${bbox.swLat}&sw_lng=${bbox.swLng}&ne_lat=${bbox.neLat}&ne_lng=${bbox.neLng}`,
      );
      return data;
    },
    enabled: bbox !== null,
  });
}
