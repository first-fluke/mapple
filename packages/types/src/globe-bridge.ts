// ---------------------------------------------------------------------------
// Globe JS Bridge — Message Schema
// Shared between Web (iframe postMessage) and Flutter (WebView JS channel).
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Common
// ---------------------------------------------------------------------------

export interface GlobeCoords {
  lat: number;
  lng: number;
}

// ---------------------------------------------------------------------------
// Data types
// ---------------------------------------------------------------------------

export interface GlobePin {
  id: string;
  name: string;
  avatarUrl: string;
  lat: number;
  lng: number;
}

/** Arc communication type — each type has a distinct dash pattern (WCAG 1.4.1). */
export type ArcType = 'call' | 'email' | 'meeting' | 'message';

export interface GlobeArc {
  id: string;
  startLat: number;
  startLng: number;
  endLat: number;
  endLng: number;
  /** Communication type — controls dash pattern (solid, short dash, long dash, dot). */
  type: ArcType;
  /** Interaction frequency — controls arc stroke width. */
  frequency: number;
}

export type GlobeTheme = 'light' | 'dark';
export type GlobeMode = 'explore' | 'select_location' | 'view_connections';

// ---------------------------------------------------------------------------
// Inbound messages  (parent → globe)
// ---------------------------------------------------------------------------

export interface FlyToMessage {
  type: 'FLY_TO';
  payload: GlobeCoords & {
    altitude?: number;
    durationMs?: number;
  };
}

export interface HighlightContactMessage {
  type: 'HIGHLIGHT_CONTACT';
  payload: {
    contactId: string;
  };
}

export interface SetThemeMessage {
  type: 'SET_THEME';
  payload: {
    theme: GlobeTheme;
  };
}

export interface SetModeMessage {
  type: 'SET_MODE';
  payload: {
    mode: GlobeMode;
  };
}

export interface SetPinsMessage {
  type: 'SET_PINS';
  payload: {
    pins: GlobePin[];
  };
}

export interface SetArcsMessage {
  type: 'SET_ARCS';
  payload: {
    arcs: GlobeArc[];
  };
}

export type GlobeInboundMessage =
  | FlyToMessage
  | HighlightContactMessage
  | SetThemeMessage
  | SetModeMessage
  | SetPinsMessage
  | SetArcsMessage;

// ---------------------------------------------------------------------------
// Outbound messages  (globe → parent)
// ---------------------------------------------------------------------------

export interface ReadyMessage {
  type: 'READY';
  payload: {
    version: string;
  };
}

export interface PinTappedMessage {
  type: 'PIN_TAPPED';
  payload: GlobeCoords & {
    contactId: string;
  };
}

export interface ClusterTappedMessage {
  type: 'CLUSTER_TAPPED';
  payload: GlobeCoords & {
    contactIds: string[];
    count: number;
  };
}

export interface LocationSelectedMessage {
  type: 'LOCATION_SELECTED';
  payload: GlobeCoords;
}

export type GlobeOutboundMessage =
  | ReadyMessage
  | PinTappedMessage
  | ClusterTappedMessage
  | LocationSelectedMessage;

// ---------------------------------------------------------------------------
// Union of all messages
// ---------------------------------------------------------------------------

export type GlobeBridgeMessage = GlobeInboundMessage | GlobeOutboundMessage;

// ---------------------------------------------------------------------------
// Type guards
// ---------------------------------------------------------------------------

export function isInboundMessage(msg: GlobeBridgeMessage): msg is GlobeInboundMessage {
  return ['FLY_TO', 'HIGHLIGHT_CONTACT', 'SET_THEME', 'SET_MODE', 'SET_PINS', 'SET_ARCS'].includes(msg.type);
}

export function isOutboundMessage(msg: GlobeBridgeMessage): msg is GlobeOutboundMessage {
  return ['READY', 'PIN_TAPPED', 'CLUSTER_TAPPED', 'LOCATION_SELECTED'].includes(msg.type);
}
