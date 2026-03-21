import { api } from './client';

export interface Tag {
  id: number;
  name: string;
  created_at: string;
}

export const tagsApi = {
  list: () => api.get<Tag[]>('/tags'),
  create: (name: string) => api.post<Tag>('/tags', { name }),
  delete: (id: number) => api.delete<void>(`/tags/${id}`),
};
