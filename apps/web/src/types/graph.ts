export interface GraphNode {
  id: string;
  name: string;
  avatarUrl?: string;
  /** Mutated by force-graph simulation / restored from layout cache */
  x?: number;
  y?: number;
}

/**
 * WCAG 1.4.1: Each type uses both a distinct color AND a distinct dash pattern,
 * so the information is never conveyed by color alone.
 */
export type LinkType = 'colleague' | 'classmate' | 'friend' | 'other';

export interface GraphLink {
  source: string;
  target: string;
  type: LinkType;
  label?: string;
}

export interface GraphResponse {
  nodes: GraphNode[];
  links: GraphLink[];
}
