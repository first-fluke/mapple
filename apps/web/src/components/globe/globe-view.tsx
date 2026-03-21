'use client';

import { List, RotateCcw } from 'lucide-react';
import { useScreenReader } from '@/hooks/use-screen-reader';
import { handleKeyboardActivate } from '@/lib/a11y';
import { cn } from '@/lib/utils';
import { type Contact, ContactListView } from './contact-list-view';

interface GlobeViewProps {
  contacts: Contact[];
  onSelectContact?: (id: string) => void;
  selectedContactId?: string;
}

export function GlobeView({ contacts, onSelectContact, selectedContactId }: GlobeViewProps) {
  const { shouldUseListView, prefersListView, reducedMotion, toggleListView } = useScreenReader();

  return (
    <div className="relative flex h-full flex-col">
      {/* View toggle button — always visible for opt-in/opt-out */}
      <div className="flex items-center justify-end gap-2 p-2">
        {reducedMotion && !prefersListView && (
          <output className="text-xs text-muted-foreground">Reduced motion detected — showing list view.</output>
        )}
        <button
          type="button"
          onClick={toggleListView}
          onKeyDown={handleKeyboardActivate(toggleListView)}
          className={cn(
            'inline-flex min-h-12 min-w-12 items-center justify-center gap-2 rounded-lg border px-3 py-2 text-sm transition-colors',
            'hover:bg-accent focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring',
          )}
          aria-pressed={prefersListView}
          aria-label={shouldUseListView ? 'Switch to globe view' : 'Switch to list view'}
        >
          {shouldUseListView ? (
            <>
              <RotateCcw className="h-4 w-4" aria-hidden="true" />
              <span className="hidden sm:inline">Globe View</span>
            </>
          ) : (
            <>
              <List className="h-4 w-4" aria-hidden="true" />
              <span className="hidden sm:inline">List View</span>
            </>
          )}
        </button>
      </div>

      {shouldUseListView ? (
        <ContactListView contacts={contacts} onSelectContact={onSelectContact} selectedContactId={selectedContactId} />
      ) : (
        <div
          className="flex flex-1 items-center justify-center"
          role="img"
          aria-label={`Interactive globe showing ${contacts.length} contacts. Switch to list view for screen reader accessible version.`}
        >
          {/* Globe 3D visualization placeholder — will be replaced by actual globe renderer (e.g. react-globe.gl) */}
          <div className="flex h-64 w-64 items-center justify-center rounded-full border-2 border-dashed border-muted-foreground/30">
            <p className="text-muted-foreground">Globe Visualization</p>
          </div>
        </div>
      )}
    </div>
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
  pins?: GlobePin[];
  width?: number;
  height?: number;
  onPinClick?: (pin: GlobePin) => void;
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
    controls.addEventListener('end', handleChange);
    return () => {
      controls.removeEventListener('end', handleChange);
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
