import { clearTokens, getAccessToken, getRefreshToken, setTokens, type TokenResponse } from '@/lib/auth';

const API_BASE = '/api/proxy';

interface ApiResponse<T> {
  data: T;
  meta?: Record<string, unknown>;
  errors?: Array<{ code: string; message: string; details?: unknown }>;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
  const headers = new Headers(options.headers);
  if (!headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const token = getAccessToken();
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (response.status === 401) {
    const refreshed = await tryRefresh();
    if (refreshed) {
      const newToken = getAccessToken();
      if (newToken) {
        headers.set('Authorization', `Bearer ${newToken}`);
      }
      const retryResponse = await fetch(`${API_BASE}${path}`, { ...options, headers });
      if (!retryResponse.ok) {
        const err = await retryResponse.json().catch(() => null);
        throw new Error(err?.error?.message || `Request failed: ${retryResponse.status}`);
      }
      return retryResponse.json();
    }
    clearTokens();
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    const err = await response.json().catch(() => null);
    throw new Error(err?.error?.message || `Request failed: ${response.status}`);
  }

  return response.json();
}

async function tryRefresh(): Promise<boolean> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return false;

  try {
    const response = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) return false;

    const result: ApiResponse<TokenResponse> = await response.json();
    setTokens(result.data.access_token, result.data.refresh_token, result.data.expires_in);
    return true;
  } catch {
    return false;
  }
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    }),
  delete: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: 'DELETE',
      body: body ? JSON.stringify(body) : undefined,
    }),
};
