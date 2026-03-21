'use client';

import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

type CrossTabTransitionProps = {
  active: boolean;
  children: ReactNode;
};

export function CrossTabTransition({ active, children }: CrossTabTransitionProps) {
  return (
    <div
      className={cn(
        'h-full transition-all duration-300 ease-in-out',
        active ? 'scale-95 opacity-0' : 'scale-100 opacity-100',
      )}
    >
      {children}
    </div>
  );
}
