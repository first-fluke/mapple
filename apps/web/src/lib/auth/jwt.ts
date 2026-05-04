interface AccessClaims {
  sub: string;
  exp: number;
  iat: number;
  jti: string;
}

function base64UrlDecode(input: string): string {
  const padding = '='.repeat((4 - (input.length % 4)) % 4);
  const base64 = (input + padding).replace(/-/g, '+').replace(/_/g, '/');
  if (typeof window === 'undefined') {
    return Buffer.from(base64, 'base64').toString('utf-8');
  }
  return atob(base64);
}

export function decodeAccessClaims(jws: string): AccessClaims | null {
  const parts = jws.split('.');
  if (parts.length !== 3) return null;
  try {
    const json = base64UrlDecode(parts[1]);
    const payload = JSON.parse(json) as Partial<AccessClaims>;
    if (typeof payload.sub !== 'string' || typeof payload.exp !== 'number') return null;
    return payload as AccessClaims;
  } catch {
    return null;
  }
}

export function decodeAccessExp(jws: string): number | null {
  return decodeAccessClaims(jws)?.exp ?? null;
}
