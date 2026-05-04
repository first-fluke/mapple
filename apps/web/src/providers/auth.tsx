'use client';

import type { ReactNode } from 'react';
import { AuthBootstrap } from '@/components/auth/auth-bootstrap';

export function AuthProvider({ children }: { children: ReactNode }) {
  return (
    <>
      <AuthBootstrap />
      {children}
    </>
  );
}
