'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type { ForceGraphMethods, NodeObject } from 'react-force-graph-2d';
import ForceGraph2D from 'react-force-graph-2d';
import { useLayoutCache } from '@/hooks/use-layout-cache';
import { useTranslations } from '@/hooks/use-translations';
import type { GraphLink, GraphNode, LinkType } from '@/types/graph';

// ── Terrazzo chart palette — WCAG 1.4.1: unique color + unique dash ──────────
const LINK_STYLES: Record<LinkType, { color: string; dash: number[] | null }> = {
  colleague: { color: '#f97316', dash: null }, // Coral, solid
  classmate: { color: '#0d9488', dash: [6, 3] }, // Teal, dashed
  friend: { color: '#d97706', dash: [2, 2] }, // Amber, dotted
  other: { color: '#6366f1', dash: [10, 4] }, // Indigo, long-dash
};

// Cluster node-fill colors in chart palette order
const CLUSTER_COLORS = ['#f97316', '#0d9488', '#d97706', '#6366f1', '#e11d48'] as const;

const NODE_BASE_RADIUS = 18;
/** Only draw text labels when zoomed in past this threshold */
const LABEL_ZOOM_THRESHOLD = 1.2;

const AVATAR_CACHE = new Map<string, HTMLImageElement>();

function getAvatarImage(url: string): HTMLImageElement | null {
  const cached = AVATAR_CACHE.get(url);
  if (cached?.complete && cached.naturalWidth > 0) return cached;
  if (!cached) {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.src = url;
    img.onload = () => AVATAR_CACHE.set(url, img);
    AVATAR_CACHE.set(url, img);
  }
  return null;
}

function drawInitials(ctx: CanvasRenderingContext2D, name: string, x: number, y: number, r: number) {
  const initials = name
    .split(' ')
    .map((s) => s[0] ?? '')
    .join('')
    .slice(0, 2)
    .toUpperCase();
  ctx.fillStyle = '#faf8f5';
  ctx.font = `600 ${r * 0.9}px system-ui,-apple-system,sans-serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(initials, x, y);
}

// Extended node type: carries simulation coords and optional cluster id
type SimNode = GraphNode & { x?: number; y?: number; cluster?: string };

interface ForceGraphViewProps {
  nodes: GraphNode[];
  links: GraphLink[];
  focusNodeId?: string | null;
  width: number;
  height: number;
  onNodeClick?: (nodeId: string) => void;
  reducedMotion?: boolean;
}

export default function ForceGraphView({
  nodes,
  links,
  focusNodeId,
  width,
  height,
  onNodeClick,
  reducedMotion = false,
}: ForceGraphViewProps) {
  const fgRef = useRef<ForceGraphMethods | undefined>(undefined);
  const { load, applyPositions, save } = useLayoutCache();
  const d = useTranslations();

  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);
  // zoomRef drives label rendering inside the canvas draw callback without causing re-renders
  const zoomRef = useRef(1);

  // ── Derived maps (memoised to avoid re-computation on every render) ───────

  /** neighbor set per node — used to dim non-adjacent nodes on hover */
  const neighborMap = useMemo(() => {
    const map = new Map<string, Set<string>>();
    for (const link of links) {
      const src = typeof link.source === 'object' ? (link.source as SimNode).id : link.source;
      const tgt = typeof link.target === 'object' ? (link.target as SimNode).id : link.target;
      if (!map.has(src)) map.set(src, new Set());
      if (!map.has(tgt)) map.set(tgt, new Set());
      map.get(src)?.add(tgt);
      map.get(tgt)?.add(src);
    }
    return map;
  }, [links]);

  /** cluster id → chart-palette hex */
  const clusterColorMap = useMemo(() => {
    const map = new Map<string, string>();
    let idx = 0;
    for (const node of nodes) {
      const cluster = (node as SimNode).cluster;
      if (cluster && !map.has(cluster)) {
        map.set(cluster, CLUSTER_COLORS[idx % CLUSTER_COLORS.length]);
        idx++;
      }
    }
    return map;
  }, [nodes]);

  /** edge-degree per node — drives node radius */
  const degreeMap = useMemo(() => {
    const map = new Map<string, number>();
    for (const link of links) {
      const src = typeof link.source === 'object' ? (link.source as SimNode).id : link.source;
      const tgt = typeof link.target === 'object' ? (link.target as SimNode).id : link.target;
      map.set(src, (map.get(src) ?? 0) + 1);
      map.set(tgt, (map.get(tgt) ?? 0) + 1);
    }
    return map;
  }, [links]);

  // ── Layout cache ─────────────────────────────────────────────────────────
  useEffect(() => {
    load();
  }, [load]);

  const graphData = useMemo(() => {
    const positionedNodes = applyPositions(nodes);
    return { nodes: positionedNodes, links };
  }, [nodes, links, applyPositions]);

  // ── Zoom-to-fit after first engine stop ──────────────────────────────────
  const fitDone = useRef(false);
  const handleEngineStop = useCallback(() => {
    if (!fgRef.current) return;
    save(graphData.nodes);
    if (!fitDone.current) {
      fitDone.current = true;
      fgRef.current.zoomToFit(400, 40);
    }
  }, [graphData.nodes, save]);

  // ── Focus animation when focusNodeId changes ──────────────────────────────
  useEffect(() => {
    if (!focusNodeId || !fgRef.current) return;
    const node = graphData.nodes.find((n) => n.id === focusNodeId) as SimNode | undefined;
    if (node?.x != null && node?.y != null) {
      fgRef.current.centerAt(node.x, node.y, 800);
      fgRef.current.zoom(2.5, 800);
    }
  }, [focusNodeId, graphData.nodes]);

  // ── Canvas node painter ───────────────────────────────────────────────────
  const drawNode = useCallback(
    (rawNode: NodeObject, ctx: CanvasRenderingContext2D, globalScale: number) => {
      const node = rawNode as SimNode;
      const x = node.x ?? 0;
      const y = node.y ?? 0;

      const degree = degreeMap.get(node.id) ?? 0;
      const r = (NODE_BASE_RADIUS + Math.min(degree * 1.5, 10)) / globalScale;

      const isHovered = node.id === hoveredNodeId;
      const isFocused = node.id === focusNodeId;
      const isNeighbor = hoveredNodeId ? (neighborMap.get(hoveredNodeId)?.has(node.id) ?? false) : false;
      const isDimmed = hoveredNodeId !== null && !isHovered && !isNeighbor;

      const cluster = node.cluster;
      const nodeColor = cluster ? (clusterColorMap.get(cluster) ?? '#f97316') : '#f97316';

      ctx.save();
      ctx.globalAlpha = isDimmed ? 0.18 : 1;

      // Glow for hovered / focused node
      if (isHovered || isFocused) {
        ctx.shadowColor = isFocused ? '#f97316' : '#d97706';
        ctx.shadowBlur = 14 / globalScale;
      }

      // Base fill (warm stone fallback so clip shows through on avatar path)
      ctx.beginPath();
      ctx.arc(x, y, r, 0, 2 * Math.PI);
      ctx.fillStyle = '#44403c';
      ctx.fill();

      // Avatar image or cluster-colored initials
      if (node.avatarUrl) {
        const img = getAvatarImage(node.avatarUrl);
        if (img) {
          ctx.save();
          ctx.beginPath();
          ctx.arc(x, y, r, 0, 2 * Math.PI);
          ctx.clip();
          ctx.drawImage(img, x - r, y - r, r * 2, r * 2);
          ctx.restore();
        } else {
          // Image not yet loaded — draw cluster color + initials as placeholder
          ctx.beginPath();
          ctx.arc(x, y, r, 0, 2 * Math.PI);
          ctx.fillStyle = nodeColor;
          ctx.fill();
          drawInitials(ctx, node.name, x, y, r);
        }
      } else {
        ctx.beginPath();
        ctx.arc(x, y, r, 0, 2 * Math.PI);
        ctx.fillStyle = nodeColor;
        ctx.fill();
        drawInitials(ctx, node.name, x, y, r);
      }

      // Border ring
      ctx.beginPath();
      ctx.arc(x, y, r, 0, 2 * Math.PI);
      ctx.strokeStyle = isFocused ? '#f97316' : isHovered ? '#d97706' : '#78716c';
      ctx.lineWidth = (isFocused ? 2.5 : 1.5) / globalScale;
      ctx.stroke();

      ctx.shadowBlur = 0;
      ctx.restore();

      // Text label — only at sufficient zoom
      if (zoomRef.current >= LABEL_ZOOM_THRESHOLD) {
        const fontSize = 12 / globalScale;
        ctx.save();
        ctx.globalAlpha = isDimmed ? 0.12 : 1;
        ctx.font = `500 ${fontSize}px system-ui,-apple-system,sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        const labelY = y + r + 3 / globalScale;
        const textWidth = ctx.measureText(node.name).width;
        // Dark backdrop pill
        ctx.fillStyle = 'rgba(28,25,23,0.75)';
        ctx.beginPath();
        ctx.roundRect(
          x - textWidth / 2 - 3 / globalScale,
          labelY - 1 / globalScale,
          textWidth + 6 / globalScale,
          fontSize + 2 / globalScale,
          3 / globalScale,
        );
        ctx.fill();
        ctx.fillStyle = '#faf8f5';
        ctx.fillText(node.name, x, labelY, 120 / globalScale);
        ctx.restore();
      }
    },
    [hoveredNodeId, focusNodeId, neighborMap, degreeMap, clusterColorMap],
  );

  // ── Hit area (larger than visual for easier clicking) ────────────────────
  const nodePointerAreaPaint = useCallback(
    (rawNode: NodeObject, color: string, ctx: CanvasRenderingContext2D, globalScale: number) => {
      const node = rawNode as SimNode;
      const x = node.x ?? 0;
      const y = node.y ?? 0;
      const degree = degreeMap.get(node.id) ?? 0;
      const r = (NODE_BASE_RADIUS + Math.min(degree * 1.5, 10)) / globalScale;
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(x, y, r + 4 / globalScale, 0, 2 * Math.PI);
      ctx.fill();
    },
    [degreeMap],
  );

  // ── Link styling ─────────────────────────────────────────────────────────
  const getLinkColor = useCallback(
    (link: object) => {
      const l = link as GraphLink;
      const style = LINK_STYLES[l.type] ?? LINK_STYLES.other;
      if (hoveredNodeId === null) return style.color;
      const src = typeof l.source === 'object' ? (l.source as SimNode).id : l.source;
      const tgt = typeof l.target === 'object' ? (l.target as SimNode).id : l.target;
      const connected = src === hoveredNodeId || tgt === hoveredNodeId;
      return connected ? style.color : `${style.color}33`; // ~20 % opacity when dimmed
    },
    [hoveredNodeId],
  );

  const getLinkDash = useCallback((link: object) => {
    const l = link as GraphLink;
    return LINK_STYLES[l.type]?.dash ?? null;
  }, []);

  const getLinkWidth = useCallback(
    (link: object) => {
      const l = link as GraphLink;
      const src = typeof l.source === 'object' ? (l.source as SimNode).id : l.source;
      const tgt = typeof l.target === 'object' ? (l.target as SimNode).id : l.target;
      const connected = hoveredNodeId !== null && (src === hoveredNodeId || tgt === hoveredNodeId);
      return connected ? 2.5 : 1.2;
    },
    [hoveredNodeId],
  );

  const getLinkLabel = useCallback(
    (link: object) => {
      const l = link as GraphLink;
      const labelMap: Record<LinkType, string> = {
        colleague: d.graph.colleague,
        classmate: d.graph.classmate,
        friend: d.graph.friend,
        other: d.graph.other,
      };
      return labelMap[l.type] ?? l.type;
    },
    [d.graph.colleague, d.graph.classmate, d.graph.friend, d.graph.other],
  );

  // ── Interaction handlers ──────────────────────────────────────────────────
  const handleNodeHover = useCallback((rawNode: NodeObject | null) => {
    setHoveredNodeId((rawNode as SimNode | null)?.id ?? null);
  }, []);

  const handleNodeClick = useCallback(
    (rawNode: NodeObject) => {
      onNodeClick?.((rawNode as SimNode).id);
    },
    [onNodeClick],
  );

  const handleZoom = useCallback(({ k }: { k: number }) => {
    zoomRef.current = k;
  }, []);

  // ── Simulation tuning (reduced-motion: skip animation, pre-settle) ───────
  const cooldownTicks = reducedMotion ? 0 : 120;
  const alphaDecay = reducedMotion ? 1 : 0.02;
  const velocityDecay = reducedMotion ? 1 : 0.4;

  return (
    <ForceGraph2D
      ref={fgRef}
      graphData={graphData}
      width={width}
      height={height}
      backgroundColor="#1c1917"
      nodeCanvasObject={drawNode}
      nodeCanvasObjectMode={() => 'replace'}
      nodePointerAreaPaint={nodePointerAreaPaint}
      linkColor={getLinkColor}
      linkLineDash={getLinkDash}
      linkWidth={getLinkWidth}
      linkLabel={getLinkLabel}
      cooldownTicks={cooldownTicks}
      d3AlphaDecay={alphaDecay}
      d3VelocityDecay={velocityDecay}
      onEngineStop={handleEngineStop}
      enableNodeDrag={true}
      onNodeHover={handleNodeHover}
      onNodeClick={handleNodeClick}
      onZoom={handleZoom}
      minZoom={0.3}
      maxZoom={10}
    />
  );
}
