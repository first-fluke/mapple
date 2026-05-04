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
