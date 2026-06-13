import { apiFetch } from '@/lib/auth/api-client';
import type { ApiResponse, ErrorResponse } from './types';

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    public readonly details?: unknown,
  ) {
    super(`[${code}] ${status}`);
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
  if (response.status === 401) {
    window.location.href = '/login';
    throw new ApiError(401, 'UNAUTHORIZED');
  }
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as ErrorResponse | null;
    throw new ApiError(response.status, body?.error?.code ?? 'UNKNOWN_ERROR', body?.error?.details);
  }
  return response.json() as Promise<ApiResponse<T>>;
}

// All data calls go through apiFetch, which targets NEXT_PUBLIC_API_URL directly
// and attaches the Bearer access token (with refresh-on-401). The Next.js
// `/api/proxy` rewrite is a dumb passthrough that cannot forward the in-memory
// access token, so it must NOT be used for authenticated endpoints.
export const api = {
  async get<T>(path: string, init?: RequestInit): Promise<ApiResponse<T>> {
    const response = await apiFetch(path, { ...init, method: 'GET' });
    return handleResponse<T>(response);
  },

  async post<T>(path: string, body?: unknown, init?: RequestInit): Promise<ApiResponse<T>> {
    const response = await apiFetch(path, {
      ...init,
      method: 'POST',
      body: body != null ? JSON.stringify(body) : undefined,
    });
    return handleResponse<T>(response);
  },

  async put<T>(path: string, body?: unknown, init?: RequestInit): Promise<ApiResponse<T>> {
    const response = await apiFetch(path, {
      ...init,
      method: 'PUT',
      body: body != null ? JSON.stringify(body) : undefined,
    });
    return handleResponse<T>(response);
  },

  async patch<T>(path: string, body?: unknown, init?: RequestInit): Promise<ApiResponse<T>> {
    const response = await apiFetch(path, {
      ...init,
      method: 'PATCH',
      body: body != null ? JSON.stringify(body) : undefined,
    });
    return handleResponse<T>(response);
  },

  async delete<T>(path: string, init?: RequestInit): Promise<ApiResponse<T>> {
    const response = await apiFetch(path, { ...init, method: 'DELETE' });
    return handleResponse<T>(response);
  },
};
