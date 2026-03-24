<<<<<<< HEAD
import { betterFetch } from '@better-fetch/fetch';
import type { Session } from 'better-auth/types';
import { type NextRequest, NextResponse } from 'next/server';

const publicPaths = ['/login', '/api/auth', '/api/webhook'];

function isPublicPath(pathname: string): boolean {
  return publicPaths.some((path) => pathname === path || pathname.startsWith(`${path}/`));
}

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (isPublicPath(pathname)) {
    return NextResponse.next();
  }

  const { data: session } = await betterFetch<Session>('/api/auth/get-session', {
    baseURL: request.nextUrl.origin,
    headers: {
      cookie: request.headers.get('cookie') || '',
    },
  });

  if (!session) {
    return NextResponse.redirect(new URL('/login', request.url));
=======
import { type NextRequest, NextResponse } from 'next/server';

const PUBLIC_PATHS = ['/login', '/api/auth'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (PUBLIC_PATHS.some((p) => pathname.startsWith(p))) {
    return NextResponse.next();
  }

  const sessionCookie =
    request.cookies.get('better-auth.session_token') ?? request.cookies.get('__Secure-better-auth.session_token');

  if (!sessionCookie?.value) {
    const loginUrl = new URL('/login', request.url);
    return NextResponse.redirect(loginUrl);
>>>>>>> 2c83c4e (feat(web,api): integrate better-auth for authentication)
  }

  return NextResponse.next();
}

export const config = {
<<<<<<< HEAD
  matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)'],
=======
  matcher: ['/((?!_next/static|_next/image|favicon.ico|api/proxy).*)'],
>>>>>>> 2c83c4e (feat(web,api): integrate better-auth for authentication)
};
