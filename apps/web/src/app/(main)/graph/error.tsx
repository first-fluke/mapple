'use client';

import { AlertTriangle } from 'lucide-react';

export default function GraphError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-4 text-muted-foreground">
      <AlertTriangle className="h-10 w-10 text-destructive opacity-60" />
      <div className="text-center">
        <p className="text-lg font-medium text-foreground">Something went wrong</p>
        <p className="mt-1 text-sm">{error.message || 'Failed to load the network graph.'}</p>
      </div>
      <button
        type="button"
        onClick={reset}
        className="rounded-md border border-input bg-background px-4 py-2 text-sm font-medium hover:bg-accent"
      >
        Try again
      </button>
    </div>
  );
}
