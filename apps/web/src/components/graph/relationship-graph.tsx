'use client';

import { handleKeyboardActivate, MIN_TOUCH_TARGET, RELATIONSHIP_STYLES, type RelationshipType } from '@/lib/a11y';
import { cn } from '@/lib/utils';

export interface GraphNode {
  id: string;
  label: string;
  x: number;
  y: number;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: RelationshipType;
}

interface RelationshipGraphProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onSelectNode?: (id: string) => void;
  selectedNodeId?: string;
  width?: number;
  height?: number;
}

function RelationshipLegend() {
  return (
    <ul className="flex flex-wrap gap-4 p-3" aria-label="Relationship type legend">
      {(
        Object.entries(RELATIONSHIP_STYLES) as Array<[RelationshipType, (typeof RELATIONSHIP_STYLES)[RelationshipType]]>
      ).map(([type, style]) => (
        <li key={type} className="flex items-center gap-2 text-sm">
          <svg width="24" height="4" aria-hidden="true">
            <line
              x1="0"
              y1="2"
              x2="24"
              y2="2"
              stroke={style.color}
              strokeWidth="2"
              strokeDasharray={style.dashArray === 'none' ? undefined : style.dashArray}
            />
          </svg>
          <span>
            {style.label}
            <span className="sr-only"> — {style.description}</span>
          </span>
        </li>
      ))}
    </ul>
  );
}

export function RelationshipGraph({
  nodes,
  edges,
  onSelectNode,
  selectedNodeId,
  width = 600,
  height = 400,
}: RelationshipGraphProps) {
  const nodeMap = new Map(nodes.map((n) => [n.id, n]));

  return (
    <section aria-label="Relationship graph">
      <RelationshipLegend />

      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full"
        aria-label={`Relationship graph with ${nodes.length} contacts and ${edges.length} connections`}
      >
        <title>Relationship Graph</title>
        <desc>
          Visual graph showing connections between contacts. Each relationship type uses a distinct line pattern: solid
          for family, dashed for friend, dotted for business, and dash-dot for acquaintance.
        </desc>

        {/* Edges */}
        <g aria-label="Connections">
          {edges.map((edge) => {
            const source = nodeMap.get(edge.source);
            const target = nodeMap.get(edge.target);
            if (!source || !target) return null;
            const style = RELATIONSHIP_STYLES[edge.type];

            return (
              <line
                key={edge.id}
                x1={source.x}
                y1={source.y}
                x2={target.x}
                y2={target.y}
                stroke={style.color}
                strokeWidth="2"
                strokeDasharray={style.dashArray === 'none' ? undefined : style.dashArray}
                aria-label={`${style.label} connection: ${source.label} to ${target.label}`}
              />
            );
          })}
        </g>

        {/* Nodes — minimum 48px touch targets */}
        <g aria-label="Contacts">
          {nodes.map((node) => {
            const isSelected = node.id === selectedNodeId;
            const nodeEdges = edges.filter((e) => e.source === node.id || e.target === node.id);

            return (
              // biome-ignore lint/a11y/useSemanticElements: <button> cannot be used inside SVG; <g role="button"> is the correct pattern
              <g
                key={node.id}
                role="button"
                tabIndex={0}
                aria-label={`${node.label}${isSelected ? ' (selected)' : ''}. ${nodeEdges.length} connection${nodeEdges.length !== 1 ? 's' : ''}.`}
                onClick={() => onSelectNode?.(node.id)}
                onKeyDown={handleKeyboardActivate(() => onSelectNode?.(node.id))}
                className="cursor-pointer outline-none"
              >
                {/* Invisible hit area for 48dp touch target */}
                <rect
                  x={node.x - MIN_TOUCH_TARGET / 2}
                  y={node.y - MIN_TOUCH_TARGET / 2}
                  width={MIN_TOUCH_TARGET}
                  height={MIN_TOUCH_TARGET}
                  fill="transparent"
                />
                {/* Visual node */}
                <circle
                  cx={node.x}
                  cy={node.y}
                  r="16"
                  className={cn(
                    'fill-primary stroke-background stroke-2 transition-all',
                    isSelected && 'stroke-ring stroke-[3]',
                  )}
                />
                {/* Focus ring */}
                <circle
                  cx={node.x}
                  cy={node.y}
                  r="22"
                  fill="none"
                  className="stroke-transparent stroke-2 [g:focus-visible>&]:stroke-ring"
                />
                {/* Label */}
                <text x={node.x} y={node.y + 32} textAnchor="middle" className="fill-foreground text-xs">
                  {node.label}
                </text>
              </g>
            );
          })}
        </g>
      </svg>

      {/* Screen reader table fallback for the graph */}
      <div className="sr-only">
        <table>
          <caption>Relationship connections</caption>
          <thead>
            <tr>
              <th scope="col">From</th>
              <th scope="col">To</th>
              <th scope="col">Relationship</th>
            </tr>
          </thead>
          <tbody>
            {edges.map((edge) => {
              const source = nodeMap.get(edge.source);
              const target = nodeMap.get(edge.target);
              if (!source || !target) return null;
              const style = RELATIONSHIP_STYLES[edge.type];
              return (
                <tr key={edge.id}>
                  <td>{source.label}</td>
                  <td>{target.label}</td>
                  <td>{style.label}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
