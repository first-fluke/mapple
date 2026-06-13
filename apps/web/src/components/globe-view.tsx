'use client';

import { useAtom, useAtomValue } from 'jotai';
import { useCallback, useEffect, useRef } from 'react';
import { CrossTabTransition } from '@/components/cross-tab-transition';
import { GlobeDynamic } from '@/components/globe/globe-dynamic';
import { GlobeEmptyState } from '@/components/globe/globe-empty-state';
import { GlobeErrorBoundary } from '@/components/globe/globe-error-boundary';
import { GlobeSkeleton } from '@/components/globe/globe-skeleton';
import { useNavigateToGraph } from '@/hooks/use-cross-navigation';
import { useGlobeArcs } from '@/hooks/use-globe-arcs';
import { useGlobeData } from '@/hooks/use-globe-data';
import { useTranslations } from '@/hooks/use-translations';
import type { GlobePin as ApiGlobePin } from '@/lib/api/globe';
import { crossTabTransitionAtom, globeFlyToAtom } from '@/stores/navigation';

/** Detect prefers-reduced-motion at mount time (SSR-safe). */
function useReducedMotion(): boolean {
  const ref = useRef(false);
  if (typeof window !== 'undefined') {
    ref.current = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }
  return ref.current;
}

export function GlobeView() {
  const navigateToGraph = useNavigateToGraph();
  const [flyToTarget, setFlyToTarget] = useAtom(globeFlyToAtom);
  const isTransitioning = useAtomValue(crossTabTransitionAtom);
  const reducedMotion = useReducedMotion();
  const d = useTranslations();

  // ── Data ─────────────────────────────────────────────────────────────────
  const { data: globeData, isLoading, isError } = useGlobeData();
  const { data: arcs = [] } = useGlobeArcs(!isLoading);

  const pins: ApiGlobePin[] = globeData?.pins ?? [];
  const hasLocatedContacts = pins.length > 0;

  // ── flyTo handling ───────────────────────────────────────────────────────
  // The flyToTarget is passed as a prop to GlobeView (inner). After consuming
  // it we clear the atom so it doesn't re-trigger.
  const currentFlyTo = flyToTarget;
  useEffect(() => {
    if (flyToTarget) {
      // Small delay to let the globe mount before flying
      const t = setTimeout(() => setFlyToTarget(null), 1200);
      return () => clearTimeout(t);
    }
  }, [flyToTarget, setFlyToTarget]);

  const handlePinClick = useCallback(
    (pin: ApiGlobePin) => {
      navigateToGraph(pin.id);
    },
    [navigateToGraph],
  );

  // ── Render ───────────────────────────────────────────────────────────────
  return (
    <CrossTabTransition active={isTransitioning}>
      {/* Screen-reader accessible list of located contacts */}
      <nav aria-label={d.globe.locationNavLabel} className="sr-only">
        <ul>
          {pins.map((pin) => (
            <li key={pin.id}>
              <button type="button" onClick={() => navigateToGraph(pin.id)}>
                {pin.name} — {d.globe.viewInNetwork}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      <div className="relative h-full w-full overflow-hidden rounded-xl" style={{ background: '#1c1917' }}>
        {/* Loading state */}
        {isLoading && <GlobeSkeleton />}

        {/* Error state */}
        {isError && !isLoading && (
          <div
            className="flex h-full w-full items-center justify-center"
            style={{ background: '#1c1917', color: '#a8a29e' }}
            role="alert"
          >
            <p className="text-sm">{d.globe.loadError}</p>
          </div>
        )}

        {/* Empty state */}
        {!isLoading && !isError && !hasLocatedContacts && <GlobeEmptyState />}

        {/* Real globe — rendered even with no arcs yet */}
        {!isLoading && !isError && hasLocatedContacts && (
          <GlobeErrorBoundary>
            <GlobeDynamic
              pins={pins}
              arcs={arcs}
              onPinClick={handlePinClick}
              flyToContactId={currentFlyTo}
              autoRotate={!reducedMotion}
            />
          </GlobeErrorBoundary>
        )}
      </div>
    </CrossTabTransition>
  );
}
