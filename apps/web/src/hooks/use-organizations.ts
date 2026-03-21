'use client';

import { useQuery } from '@tanstack/react-query';
import { organizationsApi } from '@/lib/api/organizations';

export function useOrganizationSearch(query: string) {
  return useQuery({
    queryKey: ['organizations', query],
    queryFn: async () => {
      const res = await organizationsApi.search(query);
      return res.data;
    },
    enabled: query.length > 0,
  });
}
