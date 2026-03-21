// ---------------------------------------------------------------------------
// Graph JS Bridge — Message Schema
// Shared between Web (iframe postMessage) and Flutter (WebView JS channel).
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Data types
// ---------------------------------------------------------------------------

export interface GraphNode {
  id: string;
  name: string;
  avatarUrl?: string;
  /** Grouping key — nodes in the same group share a color. */
  group?: string;
}

export interface GraphEdge {
  id: string;
  /** Source node id. */
  source: string;
  /** Target node id. */
  target: string;
}

export type GraphTheme = 'light' | 'dark';

// ---------------------------------------------------------------------------
// Inbound messages  (parent → graph)
// ---------------------------------------------------------------------------

export interface SetNodesMessage {
  type: 'SET_NODES';
  payload: {
    nodes: GraphNode[];
  };
}

export interface SetEdgesMessage {
  type: 'SET_EDGES';
  payload: {
    edges: GraphEdge[];
  };
}

export interface SetGraphThemeMessage {
  type: 'SET_THEME';
  payload: {
    theme: GraphTheme;
  };
}

export interface HighlightNodeMessage {
  type: 'HIGHLIGHT_NODE';
  payload: {
    nodeId: string;
  };
}

export type GraphInboundMessage =
  | SetNodesMessage
  | SetEdgesMessage
  | SetGraphThemeMessage
  | HighlightNodeMessage;

// ---------------------------------------------------------------------------
// Outbound messages  (graph → parent)
// ---------------------------------------------------------------------------

export interface GraphReadyMessage {
  type: 'READY';
  payload: {
    version: string;
  };
}

export interface NodeTappedMessage {
  type: 'NODE_TAPPED';
  payload: {
    nodeId: string;
    name: string;
    group?: string;
    avatarUrl?: string;
  };
}

export type GraphOutboundMessage = GraphReadyMessage | NodeTappedMessage;

// ---------------------------------------------------------------------------
// Union of all messages
// ---------------------------------------------------------------------------

export type GraphBridgeMessage = GraphInboundMessage | GraphOutboundMessage;

// ---------------------------------------------------------------------------
// Type guards
// ---------------------------------------------------------------------------

export function isGraphInboundMessage(msg: GraphBridgeMessage): msg is GraphInboundMessage {
  return ['SET_NODES', 'SET_EDGES', 'SET_THEME', 'HIGHLIGHT_NODE'].includes(msg.type);
}

export function isGraphOutboundMessage(msg: GraphBridgeMessage): msg is GraphOutboundMessage {
  return ['READY', 'NODE_TAPPED'].includes(msg.type);
}
