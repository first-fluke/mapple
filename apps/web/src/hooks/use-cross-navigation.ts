'use client';

import { useSetAtom } from 'jotai';
import { useRouter } from 'next/navigation';
import { useCallback } from 'react';
import { crossTabTransitionAtom, globeFlyToAtom } from '@/stores/navigation';

const TRANSITION_DURATION = 300;

/**
 * Navigate from Globe to Graph, setting focus on a specific contact via URL query param.
 */
export function useNavigateToGraph() {
  const router = useRouter();
  const setTransition = useSetAtom(crossTabTransitionAtom);

  return useCallback(
    (contactId: string) => {
      setTransition(true);
      setTimeout(() => {
        router.push(`/graph?focus=${encodeURIComponent(contactId)}`);
        setTimeout(() => setTransition(false), TRANSITION_DURATION);
      }, TRANSITION_DURATION);
    },
    [router, setTransition],
  );
}

/**
 * Navigate from Graph to Globe, triggering a fly-to animation via Jotai atom.
 */
export function useNavigateToGlobe() {
  const router = useRouter();
  const setFlyTo = useSetAtom(globeFlyToAtom);
  const setTransition = useSetAtom(crossTabTransitionAtom);

  return useCallback(
    (contactId: string) => {
      setFlyTo(contactId);
      setTransition(true);
      setTimeout(() => {
        router.push('/');
        setTimeout(() => setTransition(false), TRANSITION_DURATION);
      }, TRANSITION_DURATION);
    },
    [router, setFlyTo, setTransition],
  );
}
