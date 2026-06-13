export interface GlobePin {
  id: string;
  name: string;
  avatar_url: string | null;
  lat: number;
  lng: number;
}

/**
 * Relationship arc returned inline by GET /globe/data (GlobeArcOut).
 * strength is 0..1, higher = stronger relationship.
 */
export interface GlobeArcItem {
  id: number;
  start_lat: number;
  start_lng: number;
  end_lat: number;
  end_lng: number;
  type: string;
  frequency: number;
  /** 0..1 relationship strength */
  strength: number;
  contact_ids: string[];
  source_contact_id: number;
  target_contact_id: number;
  source_name: string;
  target_name: string;
}

export interface GlobeData {
  pins: GlobePin[];
  arcs: GlobeArcItem[];
}
