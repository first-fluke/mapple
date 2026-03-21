'use client';

import { useAtom } from 'jotai';
import { Globe } from 'lucide-react';
import { useEffect, useRef } from 'react';
import { CrossTabTransition } from '@/components/cross-tab-transition';
import { useNavigateToGraph } from '@/hooks/use-cross-navigation';
import { crossTabTransitionAtom, globeFlyToAtom } from '@/stores/navigation';

export function GlobeView() {
  const navigateToGraph = useNavigateToGraph();
  const [flyToTarget, setFlyToTarget] = useAtom(globeFlyToAtom);
  const [isTransitioning] = useAtom(crossTabTransitionAtom);
  const flyToProcessed = useRef(false);

  useEffect(() => {
    if (flyToTarget && !flyToProcessed.current) {
      flyToProcessed.current = true;
      // TODO: Integrate with actual Globe component to fly-to the contact's coordinates
      console.log(`[Globe] Flying to contact: ${flyToTarget}`);
      setFlyToTarget(null);
    }
    if (!flyToTarget) {
      flyToProcessed.current = false;
    }
  }, [flyToTarget, setFlyToTarget]);

  const handleContactClick = (contactId: string) => {
    navigateToGraph(contactId);
  };

  return (
    <CrossTabTransition active={isTransitioning}>
      <div className="flex h-full flex-col items-center justify-center gap-6">
        <div className="flex h-48 w-48 items-center justify-center rounded-full bg-muted/50">
          <Globe className="h-24 w-24 text-muted-foreground/50" />
        </div>
        <div className="text-center">
          <h1 className="text-2xl font-semibold">Globe View</h1>
          <p className="mt-2 text-sm text-muted-foreground">Geospatial contact visualization</p>
        </div>
        {/* Placeholder: demo contact buttons for cross-tab navigation */}
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => handleContactClick('contact-1')}
            className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground transition-colors hover:bg-primary/90"
          >
            View in Graph
          </button>
        </div>
      </div>
    </CrossTabTransition>
  );
}
