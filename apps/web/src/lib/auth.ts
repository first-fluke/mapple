const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface User {
  id: number;
  provider: string;
  email: string;
  name: string | null;
  avatar_url: string | null;
}

function setCookie(name: string, value: string, maxAge: number) {
  // biome-ignore lint/suspicious/noDocumentCookie: Cookie Store API lacks cross-browser support
  document.cookie = `${name}=${encodeURIComponent(value)};path=/;max-age=${maxAge};samesite=lax`;
}

function getCookie(name: string): string | null {
  if (typeof document === 'undefined') return null;
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

function deleteCookie(name: string) {
  // biome-ignore lint/suspicious/noDocumentCookie: Cookie Store API lacks cross-browser support
  document.cookie = `${name}=;path=/;max-age=0`;
}

export function getAccessToken(): string | null {
  return getCookie(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  return getCookie(REFRESH_TOKEN_KEY);
}

export function setTokens(accessToken: string, refreshToken: string, expiresIn: number) {
  setCookie(ACCESS_TOKEN_KEY, accessToken, expiresIn);
  setCookie(REFRESH_TOKEN_KEY, refreshToken, 7 * 24 * 60 * 60);
}

export function clearTokens() {
  deleteCookie(ACCESS_TOKEN_KEY);
  deleteCookie(REFRESH_TOKEN_KEY);
}

export type OAuthProvider = 'google' | 'github';

export function getOAuthUrl(provider: OAuthProvider, callbackUrl: string): string {
  if (provider === 'google') {
    const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID ?? '';
    const params = new URLSearchParams({
      client_id: clientId,
      redirect_uri: callbackUrl,
      response_type: 'code',
      scope: 'email profile',
      state: 'google',
    });
    return `https://accounts.google.com/o/oauth2/v2/auth?${params}`;
  }

  const clientId = process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID ?? '';
  const params = new URLSearchParams({
    client_id: clientId,
    redirect_uri: callbackUrl,
    scope: 'user:email',
    state: 'github',
  });
  return `https://github.com/login/oauth/authorize?${params}`;
}
