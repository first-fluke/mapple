import type { GraphResponse } from '@/types/graph';
import { api } from './client';

export async function fetchGraphData(params?: { search?: string; type?: string }): Promise<GraphResponse> {
  const searchParams = new URLSearchParams();
  if (params?.search) searchParams.set('search', params.search);
  if (params?.type) searchParams.set('type', params.type);
  const query = searchParams.toString();
  const path = `/graph/data${query ? `?${query}` : ''}`;
  const response = await api.get<GraphResponse>(path);
  return response.data;
}
