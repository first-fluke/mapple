'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { type ContactCreateInput, contactsApi } from '@/lib/api/contacts';

export function useContacts() {
  return useQuery({
    queryKey: ['contacts'],
    queryFn: async () => {
      const res = await contactsApi.list();
      return res.data;
    },
  });
}

export function useCreateContact() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: ContactCreateInput) => {
      const res = await contactsApi.create(data);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
    },
  });
}
