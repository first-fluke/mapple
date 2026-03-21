'use client';

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
];

export default function GraphPage() {
  const [selectedId, setSelectedId] = useState<string>();

  return (
    <div className="flex h-full flex-col">
      <h1 className="sr-only">Relationship Graph</h1>
      <RelationshipGraph
        nodes={DEMO_NODES}
        edges={DEMO_EDGES}
        onSelectNode={setSelectedId}
        selectedNodeId={selectedId}
      />
    </div>
  );
}
