import { useCallback, useRef } from 'react';
import type { GraphNode } from '@/types/graph';

const CACHE_KEY = 'graph-layout-cache';

interface CachedPosition {
  id: string;
  x: number;
  y: number;
}

export function useLayoutCache() {
  const cacheRef = useRef<Map<string, { x: number; y: number }>>(new Map());

  const load = useCallback(() => {
    try {
      const raw = localStorage.getItem(CACHE_KEY);
      if (!raw) return;
      const positions: CachedPosition[] = JSON.parse(raw);
      const map = new Map<string, { x: number; y: number }>();
      for (const p of positions) {
        map.set(p.id, { x: p.x, y: p.y });
      }
      cacheRef.current = map;
    } catch {
      // corrupted cache — ignore
    }
  }, []);

  const applyPositions = useCallback((nodes: GraphNode[]): GraphNode[] => {
    if (cacheRef.current.size === 0) return nodes;
    return nodes.map((node) => {
      const cached = cacheRef.current.get(node.id);
      if (!cached) return node;
      return { ...node, x: cached.x, y: cached.y } as GraphNode;
    });
  }, []);

  const save = useCallback((nodes: Array<{ id?: string | number; x?: number; y?: number }>) => {
    const positions: CachedPosition[] = [];
    for (const n of nodes) {
      if (n.id != null && n.x != null && n.y != null) {
        positions.push({ id: String(n.id), x: n.x, y: n.y });
      }
    }
    try {
      localStorage.setItem(CACHE_KEY, JSON.stringify(positions));
    } catch {
      // storage full — ignore
    }
  }, []);

  return { load, applyPositions, save };
}
