import { GlobeView } from '@/components/globe-view';
import { OnboardingOverlay } from '@/components/onboarding-overlay';

export default function GlobePage() {
  return (
    <div className="relative h-full">
      <GlobeView />
      <OnboardingOverlay />
    </div>
  );
}
