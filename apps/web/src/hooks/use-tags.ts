'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { tagsApi } from '@/lib/api/tags';

export function useTags() {
  return useQuery({
    queryKey: ['tags'],
    queryFn: async () => {
      const res = await tagsApi.list();
      return res.data;
    },
  });
}

export function useCreateTag() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (name: string) => {
      const res = await tagsApi.create(name);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] });
    },
  });
}
