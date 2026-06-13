'use client';

import { useAtom } from 'jotai';
import { useCallback, useEffect, useMemo, useRef } from 'react';
import ReactGlobe, { type GlobeMethods } from 'react-globe.gl';
import { type CameraPosition, cameraAtom } from '@/atoms/camera';
import { useTranslations } from '@/hooks/use-translations';
import type { GlobePin as ApiGlobePin, GlobeArcItem } from '@/lib/api/globe';

// ── Re-export so consumers don't need to import from lib/api directly ─────────
export type { ApiGlobePin as GlobePin };

// ── Visual constants (Terrazzo palette) ─────────────────────────────────────
/** Dark-Earth background — warm stone-950 */
const BG_COLOR = '#1c1917';
/** Warm atmosphere — ember/burnt amber instead of cold blue */
const ATMOSPHERE_COLOR = '#d97706';
/** Chart palette indexed by arc strength quintile */
const ARC_COLORS = ['#f97316', '#0d9488', '#d97706', '#6366f1', '#e11d48'] as const;
/** Coral for pins */
const PIN_COLOR = '#f97316';

// ── Helpers ──────────────────────────────────────────────────────────────────

function arcColor(strength: number): string {
  const idx = Math.min(Math.floor(strength * ARC_COLORS.length), ARC_COLORS.length - 1);
  return ARC_COLORS[idx];
}

function arcAltitude(item: GlobeArcItem): number {
  // Great-circle distance proxy via |Δlat| + |Δlng|; altitude 0.1..0.5
  const dist = (Math.abs(item.end_lat - item.start_lat) + Math.abs(item.end_lng - item.start_lng)) / 360;
  return 0.1 + dist * 0.4;
}

function createPinElement(pin: ApiGlobePin, onClick: () => void): HTMLElement {
  const root = document.createElement('div');
  root.setAttribute('role', 'button');
  root.setAttribute('tabindex', '0');
  root.setAttribute('aria-label', pin.name);
  root.style.cssText =
    'display:flex;flex-direction:column;align-items:center;pointer-events:auto;cursor:pointer;transform:translate(-50%,-100%);';

  // Pulse ring
  const ring = document.createElement('div');
  ring.style.cssText =
    `position:absolute;width:40px;height:40px;border-radius:50%;` +
    `background:${PIN_COLOR};opacity:0.25;transform:scale(1);` +
    `animation:globe-pin-pulse 2s ease-out infinite;top:-4px;left:-4px;`;

  // Avatar circle
  const avatar = document.createElement('div');
  avatar.style.cssText =
    `width:32px;height:32px;border-radius:50%;border:2px solid ${PIN_COLOR};` +
    `overflow:hidden;background:#44403c;display:flex;align-items:center;` +
    `justify-content:center;box-shadow:0 2px 8px rgba(249,115,22,0.35);position:relative;`;

  if (pin.avatar_url) {
    const img = document.createElement('img');
    img.src = pin.avatar_url;
    img.alt = pin.name;
    img.style.cssText = 'width:100%;height:100%;object-fit:cover;';
    img.onerror = () => {
      img.remove();
      avatar.textContent = pin.name.charAt(0).toUpperCase();
      Object.assign(avatar.style, {
        color: '#faf8f5',
        fontSize: '14px',
        fontWeight: '600',
      });
    };
    avatar.appendChild(img);
  } else {
    avatar.textContent = pin.name.charAt(0).toUpperCase();
    Object.assign(avatar.style, {
      color: '#faf8f5',
      fontSize: '14px',
      fontWeight: '600',
    });
  }

  // Name label
  const label = document.createElement('span');
  label.textContent = pin.name;
  label.style.cssText =
    'margin-top:4px;font-size:11px;color:#faf8f5;background:rgba(28,25,23,0.8);' +
    'padding:1px 6px;border-radius:4px;white-space:nowrap;max-width:120px;' +
    'overflow:hidden;text-overflow:ellipsis;pointer-events:none;';

  const wrapper = document.createElement('div');
  wrapper.style.cssText = 'position:relative;display:flex;align-items:center;justify-content:center;';
  wrapper.appendChild(ring);
  wrapper.appendChild(avatar);

  root.appendChild(wrapper);
  root.appendChild(label);

  root.addEventListener('click', (e) => {
    e.stopPropagation();
    onClick();
  });
  root.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onClick();
    }
  });

  return root;
}

// ── Component types ───────────────────────────────────────────────────────────

export interface GlobeViewProps {
  pins?: ApiGlobePin[];
  arcs?: GlobeArcItem[];
  width?: number;
  height?: number;
  onPinClick?: (pin: ApiGlobePin) => void;
  flyToContactId?: string | null;
  /** Whether auto-rotate is desired; callers can pass prefers-reduced-motion */
  autoRotate?: boolean;
}

// ── Component ─────────────────────────────────────────────────────────────────

export function GlobeView({
  pins = [],
  arcs = [],
  width,
  height,
  onPinClick,
  flyToContactId,
  autoRotate = true,
}: GlobeViewProps) {
  const globeRef = useRef<GlobeMethods | undefined>(undefined);
  const [camera, setCamera] = useAtom(cameraAtom);
  const initializedRef = useRef(false);
  const idleTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const dict = useTranslations();

  // ── Stable arc data (avoid identity churn) ────────────────────────────────
  const arcData = useMemo(() => arcs, [arcs]);
  const pinData = useMemo(() => pins, [pins]);

  // ── Globe ready: restore camera, configure controls, auto-rotate ──────────
  const handleGlobeReady = useCallback(() => {
    if (!globeRef.current || initializedRef.current) return;
    initializedRef.current = true;

    globeRef.current.pointOfView(camera, 0);

    const controls = globeRef.current.controls();
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.rotateSpeed = 0.5;
    controls.zoomSpeed = 0.8;
    controls.minDistance = 101;
    controls.maxDistance = 600;
    controls.autoRotate = autoRotate;
    controls.autoRotateSpeed = 0.4;
  }, [camera, autoRotate]);

  // ── Pause auto-rotate on pointer interaction; resume after 3s idle ────────
  useEffect(() => {
    if (!globeRef.current || !initializedRef.current) return;
    const globe = globeRef.current;
    const controls = globe.controls();

    const pause = () => {
      controls.autoRotate = false;
      if (idleTimerRef.current) clearTimeout(idleTimerRef.current);
      if (autoRotate) {
        idleTimerRef.current = setTimeout(() => {
          controls.autoRotate = true;
        }, 3000);
      }
    };

    controls.addEventListener('start', pause);
    return () => {
      controls.removeEventListener('start', pause);
      if (idleTimerRef.current) clearTimeout(idleTimerRef.current);
    };
  }, [autoRotate]);

  // ── Persist camera position to Jotai atom ─────────────────────────────────
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
    return () => controls.removeEventListener('end', handleChange);
  }, [setCamera]);

  // ── Fly-to on contact navigation ─────────────────────────────────────────
  useEffect(() => {
    if (!flyToContactId || !globeRef.current) return;
    const pin = pinData.find((p) => p.id === flyToContactId);
    if (!pin) return;
    globeRef.current.pointOfView({ lat: pin.lat, lng: pin.lng, altitude: 1.5 }, 900);
  }, [flyToContactId, pinData]);

  // ── Accessors (stable references) ─────────────────────────────────────────
  const htmlElement = useCallback(
    (d: object) => {
      const pin = d as ApiGlobePin;
      return createPinElement(pin, () => {
        onPinClick?.(pin);
        globeRef.current?.pointOfView({ lat: pin.lat, lng: pin.lng, altitude: 1.5 }, 800);
      });
    },
    [onPinClick],
  );

  const arcStartLat = useCallback((d: object) => (d as GlobeArcItem).start_lat, []);
  const arcStartLng = useCallback((d: object) => (d as GlobeArcItem).start_lng, []);
  const arcEndLat = useCallback((d: object) => (d as GlobeArcItem).end_lat, []);
  const arcEndLng = useCallback((d: object) => (d as GlobeArcItem).end_lng, []);
  const arcColorFn = useCallback((d: object) => arcColor((d as GlobeArcItem).strength), []);
  const arcAltitudeFn = useCallback((d: object) => arcAltitude(d as GlobeArcItem), []);
  const arcDashLengthFn = useCallback(() => (autoRotate ? 0.3 : 1), [autoRotate]);
  const arcDashGapFn = useCallback(() => (autoRotate ? 0.15 : 0), [autoRotate]);
  const arcDashAnimateTimeFn = useCallback(() => (autoRotate ? 2000 : 0), [autoRotate]);
  const arcStroke = useCallback((d: object) => Math.max(0.5, (d as GlobeArcItem).strength * 2), []);

  return (
    <>
      {/* Inject keyframe for pin pulse animation */}
      <style>{`
        @keyframes globe-pin-pulse {
          0%   { transform: scale(1);   opacity: 0.35; }
          70%  { transform: scale(1.6); opacity: 0; }
          100% { transform: scale(1.6); opacity: 0; }
        }
        @media (prefers-reduced-motion: reduce) {
          @keyframes globe-pin-pulse {
            0%, 100% { opacity: 0; }
          }
        }
      `}</style>

      <div
        role="img"
        aria-label={dict.globe.globeAriaLabel}
        style={{ width: width ?? '100%', height: height ?? '100%' }}
      >
        <ReactGlobe
          ref={globeRef}
          width={width}
          height={height}
          // ── Globe appearance (warm earth, no cold blue NASA texture) ──────
          globeImageUrl="//unpkg.com/three-globe/example/img/earth-night.jpg"
          bumpImageUrl="//unpkg.com/three-globe/example/img/earth-topology.png"
          backgroundColor={BG_COLOR}
          showAtmosphere={true}
          atmosphereColor={ATMOSPHERE_COLOR}
          atmosphereAltitude={0.18}
          // ── Pins ──────────────────────────────────────────────────────────
          htmlElementsData={pinData}
          htmlLat="lat"
          htmlLng="lng"
          htmlAltitude={0.01}
          htmlElement={htmlElement}
          // ── Arcs ─────────────────────────────────────────────────────────
          arcsData={arcData}
          arcStartLat={arcStartLat}
          arcStartLng={arcStartLng}
          arcEndLat={arcEndLat}
          arcEndLng={arcEndLng}
          arcColor={arcColorFn}
          arcAltitude={arcAltitudeFn}
          arcDashLength={arcDashLengthFn}
          arcDashGap={arcDashGapFn}
          arcDashAnimateTime={arcDashAnimateTimeFn}
          arcStroke={arcStroke}
          // ── Lifecycle ────────────────────────────────────────────────────
          onGlobeReady={handleGlobeReady}
        />
      </div>
    </>
  );
}
