'use client';

import { useAtom } from 'jotai';
import { Globe } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { onboardingCompletedAtom } from '@/lib/atoms/onboarding';

export function OnboardingOverlay() {
  const [, setCompleted] = useAtom(onboardingCompletedAtom);
  const router = useRouter();

  function handleGetStarted() {
    setCompleted(true);
    router.push('/contacts');
  }

  return (
    <div className="flex min-h-full flex-col items-center justify-center gap-8 px-4 text-center">
      <div className="relative flex items-center justify-center">
        <div className="absolute h-48 w-48 rounded-full bg-primary/5" />
        <div className="absolute h-36 w-36 rounded-full border-2 border-dashed border-primary/20" />
        <Globe className="relative h-20 w-20 text-muted-foreground/40" strokeWidth={1} />
      </div>

      <div className="flex max-w-md flex-col gap-3">
        <h1 className="text-2xl font-semibold tracking-tight">Welcome to Globe CRM</h1>
        <p className="text-muted-foreground">
          Your globe is empty. Add your first contact to start mapping your relationships across the world.
        </p>
      </div>

      <Button size="lg" onClick={handleGetStarted}>
        Add your first contact
      </Button>
    </div>
  );
}
