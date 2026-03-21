'use client';

import dynamic from 'next/dynamic';
import { Suspense, useCallback, useEffect, useRef, useState } from 'react';
import { GraphEmptyState } from '@/components/graph/graph-empty-state';
import { GraphFilters, useGraphFilters } from '@/components/graph/graph-filters';
import { useGraphData } from '@/hooks/use-graph-data';

const ForceGraphView = dynamic(() => import('@/components/graph/force-graph'), { ssr: false });

export default function GraphPage() {
  const { search, type, focus } = useGraphFilters();
  const { data, isLoading, isError } = useGraphData({
    search: search || undefined,
    type: type || undefined,
  });

  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  const updateDimensions = useCallback(() => {
    if (!containerRef.current) return;
    const { width, height } = containerRef.current.getBoundingClientRect();
    setDimensions({ width, height });
  }, []);

  useEffect(() => {
    updateDimensions();
    const observer = new ResizeObserver(updateDimensions);
    if (containerRef.current) observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, [updateDimensions]);

  const isEmpty = !isLoading && !isError && (!data || data.nodes.length === 0);

  return (
    <div className="flex h-full flex-col gap-3">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold">Network Graph</h1>
        <Suspense>
          <GraphFilters />
        </Suspense>
      </div>
      <div ref={containerRef} className="relative flex-1 overflow-hidden rounded-lg border bg-card">
        {isLoading && (
          <div className="flex h-full items-center justify-center text-muted-foreground">
            <p className="text-sm">Loading graph...</p>
          </div>
        )}
        {isEmpty && <GraphEmptyState />}
        {data && data.nodes.length > 0 && dimensions.width > 0 && (
          <ForceGraphView
            nodes={data.nodes}
            links={data.links}
            focusNodeId={focus}
            width={dimensions.width}
            height={dimensions.height}
          />
        )}
      </div>
    </div>
  );
import { useState } from 'react';
import { type GraphEdge, type GraphNode, RelationshipGraph } from '@/components/graph';
const DEMO_NODES: GraphNode[] = [
  { id: '1', label: 'Alice Johnson', x: 150, y: 100 },
  { id: '2', label: 'Bob Smith', x: 450, y: 100 },
  { id: '3', label: 'Carol Lee', x: 300, y: 250 },
  { id: '4', label: 'David Kim', x: 150, y: 350 },
];
const DEMO_EDGES: GraphEdge[] = [
  { id: 'e1', source: '1', target: '2', type: 'business' },
  { id: 'e2', source: '1', target: '3', type: 'friend' },
  { id: 'e3', source: '3', target: '4', type: 'family' },
  { id: 'e4', source: '2', target: '3', type: 'acquaintance' },
  const [selectedId, setSelectedId] = useState<string>();
    <div className="flex h-full flex-col">
      <h1 className="sr-only">Relationship Graph</h1>
      <RelationshipGraph
        nodes={DEMO_NODES}
        edges={DEMO_EDGES}
        onSelectNode={setSelectedId}
        selectedNodeId={selectedId}
      />
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
