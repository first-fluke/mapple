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

const API_BASE_URL = '/api/proxy';

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

export const api = {
  async get<T>(path: string, init?: RequestInit): Promise<ApiResponse<T>> {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      method: 'GET',
      headers: { 'Content-Type': 'application/json', ...init?.headers },
    });
    return handleResponse<T>(response);
  },

  async post<T>(path: string, body?: unknown, init?: RequestInit): Promise<ApiResponse<T>> {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...init?.headers },
      body: body != null ? JSON.stringify(body) : undefined,
    });
    return handleResponse<T>(response);
  },

  async put<T>(path: string, body?: unknown, init?: RequestInit): Promise<ApiResponse<T>> {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...init?.headers },
      body: body != null ? JSON.stringify(body) : undefined,
    });
    return handleResponse<T>(response);
  },

  async patch<T>(path: string, body?: unknown, init?: RequestInit): Promise<ApiResponse<T>> {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', ...init?.headers },
      body: body != null ? JSON.stringify(body) : undefined,
    });
    return handleResponse<T>(response);
  },

  async delete<T>(path: string, init?: RequestInit): Promise<ApiResponse<T>> {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json', ...init?.headers },
    });
    return handleResponse<T>(response);
  },
};
