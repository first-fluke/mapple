import { useQuery } from '@tanstack/react-query';
import { contactsApi } from '@/lib/api/contacts';

export function useContact(contactId: number) {
  return useQuery({
    queryKey: ['contacts', contactId],
    queryFn: () => contactsApi.getContact(contactId),
    select: (res) => res.data,
  });
}

export function useExperiences(contactId: number) {
  return useQuery({
    queryKey: ['contacts', contactId, 'experiences'],
    queryFn: () => contactsApi.getExperiences(contactId),
    select: (res) => res.data,
  });
}

export function useMeetings(contactId: number) {
  return useQuery({
    queryKey: ['contacts', contactId, 'meetings'],
    queryFn: () => contactsApi.getMeetings(contactId),
    select: (res) => res.data,
  });
}

export function useTags(contactId: number) {
  return useQuery({
    queryKey: ['contacts', contactId, 'tags'],
    queryFn: () => contactsApi.getTags(contactId),
    select: (res) => res.data,
  });
}
