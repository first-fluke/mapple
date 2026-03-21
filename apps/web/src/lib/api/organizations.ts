import { api } from './client';

export interface Organization {
  id: number;
  name: string;
  type: string;
}

export const organizationsApi = {
  search: (q: string) => api.get<Organization[]>(`/organizations?q=${encodeURIComponent(q)}`),
  create: (name: string, type: string) => api.post<Organization>('/organizations', { name, type }),
};
