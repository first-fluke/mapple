import { api } from './client';

export interface ContactTag {
  id: number;
  name: string;
}

export interface ContactExperience {
  id: number;
  organization_id: number;
  role: string | null;
  major: string | null;
}

export interface Contact {
  id: number;
  user_id: number;
  name: string;
  email: string | null;
  phone: string | null;
  latitude: number | null;
  longitude: number | null;
  country: string | null;
  city: string | null;
  created_at: string;
  updated_at: string;
  tags: ContactTag[];
  experiences: ContactExperience[];
}

export interface ContactCreateInput {
  name: string;
  email?: string | null;
  phone?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  country?: string | null;
  city?: string | null;
  tag_ids?: number[];
  experiences?: {
    organization_id: number;
    role?: string | null;
    major?: string | null;
  }[];
}

export const contactsApi = {
  list: () => api.get<Contact[]>('/contacts'),
  get: (id: number) => api.get<Contact>(`/contacts/${id}`),
  create: (data: ContactCreateInput) => api.post<Contact>('/contacts', data),
  delete: (id: number) => api.delete<void>(`/contacts/${id}`),
};
