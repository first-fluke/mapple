import { api } from './client';

export interface Contact {
  id: number;
  name: string;
  email: string | null;
  phone: string | null;
  avatar_url: string | null;
  sns: ContactSns | null;
  created_at: string;
  updated_at: string;
}

export interface ContactSns {
  linkedin?: string;
  twitter?: string;
  github?: string;
  instagram?: string;
}

export interface Organization {
  id: number;
  name: string;
  type: string;
}

export interface Experience {
  id: number;
  contact_id: number;
  organization_id: number;
  organization: Organization;
  role: string | null;
  major: string | null;
  created_at: string;
  updated_at: string;
}

export interface Meeting {
  id: number;
  contact_id: number;
  title: string;
  date: string;
  location: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface Tag {
  id: number;
  name: string;
  color: string | null;
}

export const contactsApi = {
  getContact(contactId: number) {
    return api.get<Contact>(`/contacts/${contactId}`);
  },

  getExperiences(contactId: number) {
    return api.get<Experience[]>(`/contacts/${contactId}/experiences`);
  },

  getMeetings(contactId: number) {
    return api.get<Meeting[]>(`/contacts/${contactId}/meetings`);
  },

  getTags(contactId: number) {
    return api.get<Tag[]>(`/contacts/${contactId}/tags`);
  },

  addTag(contactId: number, tagId: number) {
    return api.post<void>(`/contacts/${contactId}/tags`, { tag_id: tagId });
  },

  removeTag(contactId: number, tagId: number) {
    return api.delete<void>(`/contacts/${contactId}/tags/${tagId}`);
  },
export interface ContactTag {
export interface ContactExperience {
  user_id: number;
  latitude: number | null;
  longitude: number | null;
  country: string | null;
  city: string | null;
  tags: ContactTag[];
  experiences: ContactExperience[];
export interface ContactCreateInput {
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
  list: () => api.get<Contact[]>('/contacts'),
  get: (id: number) => api.get<Contact>(`/contacts/${id}`),
  create: (data: ContactCreateInput) => api.post<Contact>('/contacts', data),
  delete: (id: number) => api.delete<void>(`/contacts/${id}`),
};
