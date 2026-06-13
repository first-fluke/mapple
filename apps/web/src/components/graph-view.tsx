'use client';

import { useAtomValue } from 'jotai';
import dynamic from 'next/dynamic';
import { parseAsString, useQueryState } from 'nuqs';
import { Suspense, useCallback, useEffect, useRef, useState } from 'react';
import { CrossTabTransition } from '@/components/cross-tab-transition';
import { GraphEmptyState } from '@/components/graph/graph-empty-state';
import { GraphFilters } from '@/components/graph/graph-filters';
import { useNavigateToGlobe } from '@/hooks/use-cross-navigation';
import { useGraphData } from '@/hooks/use-graph-data';
import { useTranslations } from '@/hooks/use-translations';
import { crossTabTransitionAtom } from '@/stores/navigation';

const ForceGraphView = dynamic(() => import('@/components/graph/force-graph'), {
  ssr: false,
});

type GraphViewProps = {
  initialFocus: string;
};

/** Detect prefers-reduced-motion once at mount time (SSR-safe). */
function useReducedMotion(): boolean {
  const ref = useRef(false);
  if (typeof window !== 'undefined') {
    ref.current = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }
  return ref.current;
}

/**
 * Read graph filter URL params without importing the component that also exports them.
 * Uses parseAsString directly to avoid coupling to graphSearchParams shape.
 */
function useGraphFiltersLocal() {
  const [search] = useQueryState('search', parseAsString.withDefault(''));
  const [type] = useQueryState('type', parseAsString.withDefault(''));
  const [focus] = useQueryState('focus', parseAsString.withDefault(''));
  return { search, type, focus };
}

export function GraphView({ initialFocus }: GraphViewProps) {
  const navigateToGlobe = useNavigateToGlobe();
  const isTransitioning = useAtomValue(crossTabTransitionAtom);
  const reducedMotion = useReducedMotion();

  const { search, type, focus } = useGraphFiltersLocal();
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

  const handleNodeClick = useCallback(
    (nodeId: string) => {
      navigateToGlobe(nodeId);
    },
    [navigateToGlobe],
  );

  const activeFocus = focus || initialFocus || null;
  const isEmpty = !isLoading && !isError && (!data || data.nodes.length === 0);
  const d = useTranslations();

  return (
    <CrossTabTransition active={isTransitioning}>
      <div className="flex h-full flex-col gap-3">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="text-lg font-semibold tracking-tight" style={{ color: '#292524' }}>
            {d.graph.title}
          </h1>
          <Suspense>
            <GraphFilters />
          </Suspense>
        </div>

        {/* Graph canvas */}
        <div
          ref={containerRef}
          className="relative flex-1 overflow-hidden rounded-xl"
          style={{ background: '#1c1917' }}
          role="img"
          aria-label={d.graph.networkGraphAriaLabel}
        >
          {/* Loading */}
          {isLoading && (
            <div className="flex h-full items-center justify-center text-sm" style={{ color: '#78716c' }}>
              <p>{d.graph.loading}</p>
            </div>
          )}

          {/* Error */}
          {isError && !isLoading && (
            <div className="flex h-full items-center justify-center text-sm" role="alert" style={{ color: '#78716c' }}>
              <p>{d.graph.loadError}</p>
            </div>
          )}

          {/* Empty */}
          {isEmpty && <GraphEmptyState />}

          {/* Real graph */}
          {data && data.nodes.length > 0 && dimensions.width > 0 && (
            <ForceGraphView
              nodes={data.nodes}
              links={data.links}
              focusNodeId={activeFocus}
              width={dimensions.width}
              height={dimensions.height}
              onNodeClick={handleNodeClick}
              reducedMotion={reducedMotion}
            />
          )}

          {/* Screen-reader table fallback */}
          {data && data.nodes.length > 0 && (
            <div className="sr-only">
              <table>
                <caption>{d.graph.connectionListCaption}</caption>
                <thead>
                  <tr>
                    <th scope="col">{d.graph.connectionColSource}</th>
                    <th scope="col">{d.graph.connectionColTarget}</th>
                    <th scope="col">{d.graph.connectionColType}</th>
                  </tr>
                </thead>
                <tbody>
                  {data.links.map((link, i) => {
                    const src = typeof link.source === 'string' ? link.source : String(link.source);
                    const tgt = typeof link.target === 'string' ? link.target : String(link.target);
                    const srcNode = data.nodes.find((n) => n.id === src);
                    const tgtNode = data.nodes.find((n) => n.id === tgt);
                    return (
                      // biome-ignore lint/suspicious/noArrayIndexKey: link list is stable
                      <tr key={i}>
                        <td>{srcNode?.name ?? src}</td>
                        <td>{tgtNode?.name ?? tgt}</td>
                        <td>{link.type}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </CrossTabTransition>
  );
}
