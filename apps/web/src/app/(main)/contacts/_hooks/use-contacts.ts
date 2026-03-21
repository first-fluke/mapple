'use client';

import { useInfiniteQuery } from '@tanstack/react-query';
import { api, type CursorMeta } from '@/lib/api';

export interface Contact {
  id: number;
  name: string;
  email: string | null;
  phone: string | null;
  created_at: string;
  updated_at: string;
}

interface ContactFilters {
  search: string;
  sort: string;
  has_email: boolean | null;
  has_phone: boolean | null;
}

export function useContacts(filters: ContactFilters) {
  return useInfiniteQuery({
    queryKey: ['contacts', filters],
    queryFn: async ({ pageParam }) => {
      const params = new URLSearchParams();
      if (pageParam) params.set('cursor', pageParam);
      params.set('per_page', '20');
      if (filters.search) params.set('search', filters.search);
      if (filters.sort) params.set('sort', filters.sort);
      if (filters.has_email != null) params.set('has_email', String(filters.has_email));
      if (filters.has_phone != null) params.set('has_phone', String(filters.has_phone));

      const res = await api.get<Contact[]>(`/contacts?${params.toString()}`);
      return res;
    },
    initialPageParam: null as string | null,
    getNextPageParam: (lastPage) => {
      const meta = lastPage.meta as CursorMeta | undefined;
      return meta?.has_more ? meta.next_cursor : undefined;
    },
  });
}
