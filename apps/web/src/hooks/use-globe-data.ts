'use client';

import { useQuery } from '@tanstack/react-query';
import type { GlobeData } from '@/lib/api/globe';
import { apiFetch } from '@/lib/auth/api-client';

interface ApiEnvelope {
  data: GlobeData;
}

export function useGlobeData(limit = 200) {
  return useQuery({
    queryKey: ['globe-data', limit],
    queryFn: async () => {
      const res = await apiFetch(`/globe/data?limit=${limit}`);
      if (!res.ok) throw new Error('failed to load globe data');
      const body = (await res.json()) as ApiEnvelope;
      return body.data;
    },
  });
}
