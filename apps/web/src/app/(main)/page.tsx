'use client';

import { useAtom } from 'jotai';
import { OnboardingOverlay } from '@/components/onboarding-overlay';
import { onboardingCompletedAtom } from '@/lib/atoms/onboarding';

export default function HomePage() {
  const [completed] = useAtom(onboardingCompletedAtom);

  if (!completed) {
    return <OnboardingOverlay />;
  }

  return (
    <div className="flex min-h-full flex-col items-center justify-center">
      <h1 className="text-4xl font-bold">Globe CRM</h1>
      <p className="mt-4 text-muted-foreground">Customer relationship management with geospatial capabilities</p>
    </div>
  );
}
