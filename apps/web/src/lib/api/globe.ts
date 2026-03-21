export interface GlobePin {
  id: string;
  name: string;
  avatar_url: string | null;
  lat: number;
  lng: number;
}

export interface GlobeArc {
  id: string;
  start_lat: number;
  start_lng: number;
  end_lat: number;
  end_lng: number;
  type: string;
  frequency: number;
}

export interface GlobeCluster {
  lat: number;
  lng: number;
  count: number;
  contact_ids: string[];
}

export interface GlobeData {
  pins: GlobePin[];
  arcs: GlobeArc[];
  clusters: GlobeCluster[];
}
