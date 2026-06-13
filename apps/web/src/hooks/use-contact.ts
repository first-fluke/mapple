import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  contactsApi,
  type ExperienceCreateInput,
  type ExperienceUpdateInput,
  type MeetingCreateInput,
} from '@/lib/api/contacts';

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

export function useAddContactTag(contactId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (tagId: number) => contactsApi.addTag(contactId, tagId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['contacts', contactId, 'tags'] });
    },
  });
}

export function useRemoveContactTag(contactId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (tagId: number) => contactsApi.removeTag(contactId, tagId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['contacts', contactId, 'tags'] });
    },
  });
}

export function useCreateMeeting(contactId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: MeetingCreateInput) => contactsApi.createMeeting(contactId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['contacts', contactId, 'meetings'] });
    },
  });
}

export function useUpdateMeeting(contactId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ meetingId, data }: { meetingId: number; data: Partial<MeetingCreateInput> }) =>
      contactsApi.updateMeeting(contactId, meetingId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['contacts', contactId, 'meetings'] });
    },
  });
}

export function useDeleteMeeting(contactId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (meetingId: number) => contactsApi.deleteMeeting(contactId, meetingId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['contacts', contactId, 'meetings'] });
    },
  });
}

export function useCreateExperience(contactId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: ExperienceCreateInput) => contactsApi.createExperience(contactId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['contacts', contactId, 'experiences'] });
    },
  });
}

export function useUpdateExperience(contactId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ expId, data }: { expId: number; data: ExperienceUpdateInput }) =>
      contactsApi.updateExperience(contactId, expId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['contacts', contactId, 'experiences'] });
    },
  });
}

export function useDeleteExperience(contactId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (expId: number) => contactsApi.deleteExperience(contactId, expId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['contacts', contactId, 'experiences'] });
    },
  });
}

export function useAvatarUpload(contactId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (file: File) => {
      const presignRes = await contactsApi.getAvatarPresignUrl(contactId);
      const { upload_url, avatar_url } = presignRes.data;

      await fetch(upload_url, {
        method: 'PUT',
        headers: { 'Content-Type': file.type },
        body: file,
      });

      const confirmRes = await contactsApi.confirmAvatar(contactId, avatar_url);
      return confirmRes.data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['contacts', contactId] });
    },
  });
}
