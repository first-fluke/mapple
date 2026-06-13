'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api/client';
import type { GlobeArcItem } from '@/lib/api/globe';

const MAX_ARCS = 200;

/**
 * Fetches relationship arcs from GET /globe/arcs.
 * Returns an empty array gracefully when the endpoint is unavailable (404/error),
 * so the globe renders pins even before the backend lands.
 */
export function useGlobeArcs(enabled = true) {
  return useQuery({
    queryKey: ['globe-arcs'],
    enabled,
    retry: false,
    queryFn: async (): Promise<GlobeArcItem[]> => {
      try {
        const res = await api.get<GlobeArcItem[]>(`/globe/arcs?limit=${MAX_ARCS}`);
        const items = res.data ?? [];
        // Sort by strength desc, cap at MAX_ARCS
        return [...items].sort((a, b) => b.strength - a.strength).slice(0, MAX_ARCS);
      } catch {
        // Endpoint not yet available — return empty list so the UI degrades gracefully
        return [];
      }
    },
  });
}
