import type { SearchParams } from 'nuqs/server';
import { GraphView } from '@/components/graph-view';
import { graphSearchParamsCache } from './search-params';

type GraphPageProps = {
  searchParams: Promise<SearchParams>;
};

export default async function GraphPage({ searchParams }: GraphPageProps) {
  const { focus } = await graphSearchParamsCache.parse(searchParams);

  return <GraphView initialFocus={focus} />;
}
