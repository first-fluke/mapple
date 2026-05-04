const REFRESH_KEY = 'globe-crm.auth.refresh';

export function loadRefresh(): string | null {
  if (typeof window === 'undefined') return null;
  try {
    return window.localStorage.getItem(REFRESH_KEY);
  } catch {
    return null;
  }
}

export function saveRefresh(token: string): void {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(REFRESH_KEY, token);
  } catch {
    // Storage may be full or disabled (private mode)
  }
}

export function clearRefresh(): void {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.removeItem(REFRESH_KEY);
  } catch {
    // ignore
  }
}

export const REFRESH_STORAGE_KEY = REFRESH_KEY;
