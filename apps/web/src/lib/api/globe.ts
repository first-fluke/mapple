export interface GlobePin {
  id: string;
  name: string;
  avatar_url: string | null;
  lat: number;
  lng: number;
}

export interface GlobeArc {
  start_lat: number;
  start_lng: number;
  end_lat: number;
  end_lng: number;
  type: string;
  frequency: number;
  contact_ids: string[];
}

export interface GlobeData {
  pins: GlobePin[];
  arcs: GlobeArc[];
}

/**
 * Arc item from the dedicated GET /globe/arcs endpoint.
 * strength is 0..1, higher = stronger relationship.
 */
export interface GlobeArcItem {
  id: string;
  start_lat: number;
  start_lng: number;
  end_lat: number;
  end_lng: number;
  /** 0..1 relationship strength */
  strength: number;
  source_contact_id: string;
  target_contact_id: string;
  source_name: string;
  target_name: string;
}
