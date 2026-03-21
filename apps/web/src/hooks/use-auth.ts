import { useQuery } from '@tanstack/react-query';
import { useAtom } from 'jotai';
import { useEffect } from 'react';
import { api } from '@/lib/api';
import type { User } from '@/lib/auth';
import { clearTokens, getAccessToken } from '@/lib/auth';
import { authLoadingAtom, userAtom } from '@/store/auth';

export function useAuth() {
  const [user, setUser] = useAtom(userAtom);
  const [loading, setLoading] = useAtom(authLoadingAtom);

  const { data, isLoading, error } = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: () => api.get<User>('/auth/me'),
    enabled: !!getAccessToken(),
    retry: false,
    staleTime: 5 * 60 * 1000,
  });

  useEffect(() => {
    if (data?.data) {
      setUser(data.data);
    }
    if (error) {
      setUser(null);
    }
    if (!getAccessToken()) {
      setLoading(false);
    } else {
      setLoading(isLoading);
    }
  }, [data, error, isLoading, setUser, setLoading]);

  const logout = async () => {
    try {
      const refreshToken = document.cookie.match(/(?:^|; )refresh_token=([^;]*)/)?.[1];
      if (refreshToken) {
        await api.delete('/auth/logout', { refresh_token: decodeURIComponent(refreshToken) });
      }
    } catch {
      // Ignore logout API errors
    } finally {
      clearTokens();
      setUser(null);
      window.location.href = '/login';
    }
  };

  return { user, loading, logout };
}
