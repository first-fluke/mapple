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
}
