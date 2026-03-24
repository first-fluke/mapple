'use client';

import { useAtom } from 'jotai';
import { useCallback, useEffect, useRef } from 'react';
import ReactGlobe, { type GlobeMethods } from 'react-globe.gl';
import { type CameraPosition, cameraAtom } from '@/atoms/camera';

export interface GlobePin {
  id: string;
  lat: number;
  lng: number;
  name: string;
  avatarUrl?: string;
}

interface GlobeViewProps {
  pins?: GlobePin[];
  width?: number;
  height?: number;
  onPinClick?: (pin: GlobePin) => void;
}

const GLOBE_IMAGE_URL = '//unpkg.com/three-globe/example/img/earth-blue-marble.jpg';
const BUMP_IMAGE_URL = '//unpkg.com/three-globe/example/img/earth-topology.png';

function createPinElement(pin: GlobePin): HTMLElement {
  const container = document.createElement('div');
  container.className = 'globe-pin';
  container.style.cssText =
    'display:flex;flex-direction:column;align-items:center;pointer-events:auto;cursor:pointer;transform:translate(-50%,-100%);';

  const avatar = document.createElement('div');
  avatar.style.cssText =
    'width:32px;height:32px;border-radius:50%;border:2px solid white;overflow:hidden;background:#374151;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(0,0,0,0.3);';

  if (pin.avatarUrl) {
    const img = document.createElement('img');
    img.src = pin.avatarUrl;
    img.alt = pin.name;
    img.style.cssText = 'width:100%;height:100%;object-fit:cover;';
    img.onerror = () => {
      img.remove();
      avatar.textContent = pin.name.charAt(0).toUpperCase();
      avatar.style.color = 'white';
      avatar.style.fontSize = '14px';
      avatar.style.fontWeight = '600';
    };
    avatar.appendChild(img);
  } else {
    avatar.textContent = pin.name.charAt(0).toUpperCase();
    avatar.style.color = 'white';
    avatar.style.fontSize = '14px';
    avatar.style.fontWeight = '600';
  }

  const label = document.createElement('span');
  label.textContent = pin.name;
  label.style.cssText =
    'margin-top:4px;font-size:11px;color:white;background:rgba(0,0,0,0.6);padding:1px 6px;border-radius:4px;white-space:nowrap;max-width:100px;overflow:hidden;text-overflow:ellipsis;';

  container.appendChild(avatar);
  container.appendChild(label);

  return container;
}

export function GlobeView({ pins = [], width, height, onPinClick }: GlobeViewProps) {
  const globeRef = useRef<GlobeMethods | undefined>(undefined);
  const [camera, setCamera] = useAtom(cameraAtom);
  const initializedRef = useRef(false);

  const handleGlobeReady = useCallback(() => {
    if (!globeRef.current || initializedRef.current) return;
    initializedRef.current = true;

    globeRef.current.pointOfView(camera, 0);

    const controls = globeRef.current.controls();
    controls.enableDamping = true;
    controls.dampingFactor = 0.1;
    controls.rotateSpeed = 0.5;
    controls.zoomSpeed = 0.8;
    controls.minDistance = 101;
    controls.maxDistance = 500;
  }, [camera]);

  useEffect(() => {
    if (!globeRef.current || !initializedRef.current) return;

    const controls = globeRef.current.controls();
    const handleChange = () => {
      if (!globeRef.current) return;
      const pov = globeRef.current.pointOfView();
      setCamera((prev: CameraPosition) => {
        if (
          Math.abs(prev.lat - pov.lat) < 0.001 &&
          Math.abs(prev.lng - pov.lng) < 0.001 &&
          Math.abs(prev.altitude - pov.altitude) < 0.001
        ) {
          return prev;
        }
        return { lat: pov.lat, lng: pov.lng, altitude: pov.altitude };
      });
    };

    controls.addEventListener('end', handleChange);
    return () => {
      controls.removeEventListener('end', handleChange);
    };
  }, [setCamera]);

  const handlePinClick = useCallback(
    (d: object) => {
      const pin = d as GlobePin;
      onPinClick?.(pin);
      if (globeRef.current) {
        globeRef.current.pointOfView({ lat: pin.lat, lng: pin.lng, altitude: 1.5 }, 800);
      }
    },
    [onPinClick],
  );

  return (
    <ReactGlobe
      ref={globeRef}
      width={width}
      height={height}
      globeImageUrl={GLOBE_IMAGE_URL}
      bumpImageUrl={BUMP_IMAGE_URL}
      backgroundColor="rgba(0,0,0,0)"
      showAtmosphere={true}
      atmosphereColor="#3a86ff"
      atmosphereAltitude={0.15}
      htmlElementsData={pins}
      htmlLat="lat"
      htmlLng="lng"
      htmlAltitude={0.01}
      htmlElement={(d: object) => {
        const pin = d as GlobePin;
        const el = createPinElement(pin);
        el.addEventListener('click', () => handlePinClick(d));
        return el;
      }}
      onGlobeReady={handleGlobeReady}
    />
  );
}
