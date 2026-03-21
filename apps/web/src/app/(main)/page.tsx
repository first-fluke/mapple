'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { ProfileCard } from '@/components/profile-card';
import { type BboxParams, useGlobeData } from '@/hooks/use-globe-data';
import type { GlobePin } from '@/lib/api/globe';

const DEFAULT_BBOX: BboxParams = {
  swLat: -90,
  swLng: -180,
  neLat: 90,
  neLng: 180,
};

export default function GlobePage() {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [bbox, setBbox] = useState<BboxParams>(DEFAULT_BBOX);
  const [selectedPin, setSelectedPin] = useState<GlobePin | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const { data } = useGlobeData(bbox);

  // Send data to globe iframe
  useEffect(() => {
    const iframe = iframeRef.current?.contentWindow;
    if (!iframe || !data) return;

    iframe.postMessage(
      {
        type: 'SET_PINS',
        payload: {
          pins: data.pins.map((p) => ({
            id: p.id,
            name: p.name,
            avatarUrl: p.avatar_url,
            lat: p.lat,
            lng: p.lng,
          })),
        },
      },
      '*',
    );

    iframe.postMessage(
      {
        type: 'SET_ARCS',
        payload: {
          arcs: data.arcs.map((a) => ({
            id: a.id,
            startLat: a.start_lat,
            startLng: a.start_lng,
            endLat: a.end_lat,
            endLng: a.end_lng,
            type: a.type,
            frequency: a.frequency,
          })),
        },
      },
      '*',
    );
  }, [data]);

  // Listen for messages from globe iframe
  useEffect(() => {
    function handleMessage(event: MessageEvent) {
      const msg = event.data;
      if (!msg?.type) return;

      switch (msg.type) {
        case 'PIN_TAPPED': {
          const tappedPin = data?.pins.find((p) => p.id === msg.payload.contactId);
          if (tappedPin) {
            setSelectedPin(tappedPin);
            setDrawerOpen(true);
          }
          break;
        }
        case 'VIEWPORT_CHANGED': {
          if (msg.payload?.bbox) {
            setBbox({
              swLat: msg.payload.bbox.swLat,
              swLng: msg.payload.bbox.swLng,
              neLat: msg.payload.bbox.neLat,
              neLng: msg.payload.bbox.neLng,
            });
          }
          break;
        }
      }
    }

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [data]);

  const handleDrawerChange = useCallback((open: boolean) => {
    setDrawerOpen(open);
    if (!open) setSelectedPin(null);
  }, []);

  return (
    <div className="-m-4 -mb-20 relative h-[calc(100vh-theme(spacing.20))] md:-mb-4 md:h-[calc(100vh)]">
      <iframe ref={iframeRef} src="/globe/index.html" className="h-full w-full border-0" title="Globe" />
      <ProfileCard pin={selectedPin} open={drawerOpen} onOpenChange={handleDrawerChange} />
    </div>
  );
}
