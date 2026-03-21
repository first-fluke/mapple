'use client';

import { useAtomValue } from 'jotai';
import { Network } from 'lucide-react';
import { useQueryState } from 'nuqs';
import { useEffect } from 'react';
import { graphSearchParams } from '@/app/(main)/graph/search-params';
import { CrossTabTransition } from '@/components/cross-tab-transition';
import { useNavigateToGlobe } from '@/hooks/use-cross-navigation';
import { crossTabTransitionAtom } from '@/stores/navigation';

type GraphViewProps = {
  initialFocus: string;
};

export function GraphView({ initialFocus }: GraphViewProps) {
  const navigateToGlobe = useNavigateToGlobe();
  const isTransitioning = useAtomValue(crossTabTransitionAtom);
  const [focus, setFocus] = useQueryState('focus', graphSearchParams.focus);

  useEffect(() => {
    if (initialFocus) {
      // TODO: Integrate with actual Graph component to highlight/center the focused contact
      console.log(`[Graph] Focusing on contact: ${initialFocus}`);
    }
  }, [initialFocus]);

  const handleContactClick = (contactId: string) => {
    navigateToGlobe(contactId);
  };

  return (
    <CrossTabTransition active={isTransitioning}>
      <div className="flex h-full flex-col items-center justify-center gap-6">
        <div className="flex h-48 w-48 items-center justify-center rounded-full bg-muted/50">
          <Network className="h-24 w-24 text-muted-foreground/50" />
        </div>
        <div className="text-center">
          <h1 className="text-2xl font-semibold">Graph View</h1>
          <p className="mt-2 text-sm text-muted-foreground">Relationship network visualization</p>
          {focus && <p className="mt-1 text-xs text-primary">Focused: {focus}</p>}
        </div>
        {/* Placeholder: demo contact button for cross-tab navigation */}
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => handleContactClick(focus || 'contact-1')}
            className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground transition-colors hover:bg-primary/90"
          >
            View on Globe
          </button>
          {focus && (
            <button
              type="button"
              onClick={() => setFocus('')}
              className="rounded-md bg-muted px-4 py-2 text-sm text-foreground transition-colors hover:bg-muted/80"
            >
              Clear Focus
            </button>
          )}
        </div>
      </div>
    </CrossTabTransition>
  );
}
