import { useQuery } from '@tanstack/react-query';
import { fetchGraphData } from '@/lib/api/graph';

export function useGraphData(filters: { search?: string; type?: string }) {
  return useQuery({
    queryKey: ['graph', filters],
    queryFn: () => fetchGraphData(filters),
  });
}
