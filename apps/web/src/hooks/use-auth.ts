<<<<<<< HEAD
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
=======
import { authClient } from '@/lib/auth-client';

export function useAuth() {
  const session = authClient.useSession();

  const logout = async () => {
    await authClient.signOut({
      fetchOptions: {
        onSuccess: () => {
          window.location.href = '/login';
        },
      },
    });
  };

  return {
    user: session.data?.user ?? null,
    session: session.data?.session ?? null,
    loading: session.isPending,
    logout,
  };
>>>>>>> 2c83c4e (feat(web,api): integrate better-auth for authentication)
}
