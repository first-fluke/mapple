import { useRouter } from 'next/navigation';
import { useCallback } from 'react';
import { signOut, useSession } from '@/lib/auth-client';

export function useAuth() {
  const router = useRouter();
  const { data: session, isPending } = useSession();

  const logout = useCallback(async () => {
    await signOut();
    router.push('/login');
  }, [router]);

  return {
    user: session?.user ?? null,
    loading: isPending,
    logout,
  };
}
