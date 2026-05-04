import { type NextRequest, NextResponse } from 'next/server';

// Auth gating moved to client (AuthBootstrap + tokenAtom). The proxy is a
// pure pass-through now; protected route guards live in the React tree
// because tokens are in memory + localStorage, not cookies.
//
// rule 6 (.claude/rules/frontend.md): NEVER convert this back to middleware.ts.

export function proxy(_request: NextRequest) {
  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)'],
};
