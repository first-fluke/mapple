'use client';

import { useCallback, useEffect, useMemo, useRef } from 'react';
import type { ForceGraphMethods } from 'react-force-graph-2d';
import ForceGraph2D from 'react-force-graph-2d';
import { useLayoutCache } from '@/hooks/use-layout-cache';
import type { GraphLink, GraphNode, LinkType } from '@/types/graph';

/**
 * WCAG 1.4.1 — each link type has a unique color AND dash pattern.
 * Colors chosen for ≥ 3:1 contrast ratio against white (#fff).
 */
const LINK_STYLES: Record<LinkType, { color: string; dash: number[] | null }> = {
  colleague: { color: '#2563eb', dash: null }, // blue-600, solid
  classmate: { color: '#16a34a', dash: [6, 3] }, // green-600, dashed
  friend: { color: '#ea580c', dash: [2, 2] }, // orange-600, dotted
  other: { color: '#6b7280', dash: [10, 4] }, // gray-500, long-dash
};

const NODE_RADIUS = 18;
const AVATAR_CACHE = new Map<string, HTMLImageElement>();

function getAvatarImage(url: string): HTMLImageElement | null {
  const cached = AVATAR_CACHE.get(url);
  if (cached?.complete) return cached;
  if (!cached) {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.src = url;
    AVATAR_CACHE.set(url, img);
  }
  return null;
}

interface ForceGraphViewProps {
  nodes: GraphNode[];
  links: GraphLink[];
  focusNodeId?: string | null;
  width: number;
  height: number;
}

export default function ForceGraphView({ nodes, links, focusNodeId, width, height }: ForceGraphViewProps) {
  const fgRef = useRef<ForceGraphMethods | undefined>(undefined);
  const { load, applyPositions, save } = useLayoutCache();

  // Load cached positions on mount
  useEffect(() => {
    load();
  }, [load]);

  // Apply cached positions to nodes
  const graphData = useMemo(() => {
    const positionedNodes = applyPositions(nodes);
    return { nodes: positionedNodes, links };
  }, [nodes, links, applyPositions]);

  // Focus on a specific node
  useEffect(() => {
    if (!focusNodeId || !fgRef.current) return;
    const node = graphData.nodes.find((n) => n.id === focusNodeId);
    if (node && node.x != null && node.y != null) {
      fgRef.current.centerAt(node.x, node.y, 800);
      fgRef.current.zoom(2, 800);
    }
  }, [focusNodeId, graphData.nodes]);

  const handleEngineStop = useCallback(() => {
    if (!fgRef.current) return;
    save(graphData.nodes);
  }, [graphData.nodes, save]);

  const drawNode = useCallback(
    (node: GraphNode & { x?: number; y?: number }, ctx: CanvasRenderingContext2D, globalScale: number) => {
      const x = node.x ?? 0;
      const y = node.y ?? 0;
      const r = NODE_RADIUS / globalScale;
      const fontSize = 12 / globalScale;

      // Circle clip for avatar
      ctx.save();
      ctx.beginPath();
      ctx.arc(x, y, r, 0, 2 * Math.PI);
      ctx.closePath();

      // Fill background
      ctx.fillStyle = '#e5e7eb';
      ctx.fill();

      // Draw avatar image if available
      if (node.avatarUrl) {
        const img = getAvatarImage(node.avatarUrl);
        if (img) {
          ctx.clip();
          ctx.drawImage(img, x - r, y - r, r * 2, r * 2);
        } else {
          // Draw initials as fallback while image loads
          drawInitials(ctx, node.name, x, y, r);
        }
      } else {
        drawInitials(ctx, node.name, x, y, r);
      }

      ctx.restore();

      // Circle border
      ctx.beginPath();
      ctx.arc(x, y, r, 0, 2 * Math.PI);
      ctx.strokeStyle = '#d1d5db';
      ctx.lineWidth = 1.5 / globalScale;
      ctx.stroke();

      // Highlight focused node
      if (node.id === focusNodeId) {
        ctx.beginPath();
        ctx.arc(x, y, r + 3 / globalScale, 0, 2 * Math.PI);
        ctx.strokeStyle = '#2563eb';
        ctx.lineWidth = 2 / globalScale;
        ctx.stroke();
      }

      // Name label below node
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      ctx.font = `${fontSize}px sans-serif`;
      ctx.fillStyle = '#1f2937';
      ctx.fillText(node.name, x, y + r + 3 / globalScale, 100 / globalScale);
    },
    [focusNodeId],
  );

  const nodePointerAreaPaint = useCallback(
    (
      node: GraphNode & { x?: number; y?: number },
      color: string,
      ctx: CanvasRenderingContext2D,
      globalScale: number,
    ) => {
      const x = node.x ?? 0;
      const y = node.y ?? 0;
      const r = NODE_RADIUS / globalScale;
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(x, y, r + 4 / globalScale, 0, 2 * Math.PI);
      ctx.fill();
    },
    [],
  );

  const getLinkColor = useCallback((link: GraphLink) => {
    return LINK_STYLES[link.type]?.color ?? LINK_STYLES.other.color;
  }, []);

  const getLinkDash = useCallback((link: GraphLink) => {
    return LINK_STYLES[link.type]?.dash ?? null;
  }, []);

  return (
    <ForceGraph2D
      // @ts-expect-error -- library ref types double-wrap NodeObject, incompatible with React 19
      ref={fgRef}
      graphData={graphData}
      width={width}
      height={height}
      nodeCanvasObject={drawNode}
      nodeCanvasObjectMode={() => 'replace'}
      nodePointerAreaPaint={nodePointerAreaPaint}
      linkColor={getLinkColor}
      linkLineDash={getLinkDash}
      linkWidth={1.5}
      linkLabel={(link: GraphLink) => link.label ?? link.type}
      cooldownTicks={100}
      onEngineStop={handleEngineStop}
      enableNodeDrag={true}
      minZoom={0.5}
      maxZoom={8}
    />
  );
}

function drawInitials(ctx: CanvasRenderingContext2D, name: string, x: number, y: number, r: number) {
  const initials = name
    .split(' ')
    .map((s) => s[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();
  ctx.fillStyle = '#6b7280';
  ctx.font = `bold ${r * 1.1}px sans-serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(initials, x, y);
}
