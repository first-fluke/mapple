import { useQuery } from '@tanstack/react-query';
import { useAtomValue } from 'jotai';
import { apiFetch } from '@/lib/auth/api-client';
import { isAuthenticatedAtom, tokenAtom } from '@/lib/auth/atoms';
import { logout as performLogout } from '@/lib/auth/logout';

interface MeResponse {
  data: {
    id: string;
    email: string;
    name: string;
    image: string | null;
  };
}

export function useAuth() {
  const tokens = useAtomValue(tokenAtom);
  const isAuthenticated = useAtomValue(isAuthenticatedAtom);

  const { data, isLoading } = useQuery({
    queryKey: ['auth', 'me', tokens?.access ?? null],
    enabled: isAuthenticated,
    queryFn: async () => {
      const res = await apiFetch('/auth/me');
      if (!res.ok) throw new Error('failed to load profile');
      const body = (await res.json()) as MeResponse;
      return body.data;
    },
  });

  return {
    user: data ?? null,
    session: tokens,
    loading: isLoading,
    isAuthenticated,
    logout: performLogout,
  };
}
