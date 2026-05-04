import type { TokenSet } from './atoms';

export type AuthBroadcastEvent = { type: 'tokens'; tokens: TokenSet } | { type: 'logout' };

const CHANNEL_NAME = 'globe-crm.auth';

let channel: BroadcastChannel | null = null;

function getChannel(): BroadcastChannel | null {
  if (typeof window === 'undefined' || typeof BroadcastChannel === 'undefined') {
    return null;
  }
  if (!channel) {
    channel = new BroadcastChannel(CHANNEL_NAME);
  }
  return channel;
}

export function publishAuthEvent(event: AuthBroadcastEvent): void {
  getChannel()?.postMessage(event);
}

export function subscribeAuthEvents(handler: (event: AuthBroadcastEvent) => void): () => void {
  const ch = getChannel();
  if (!ch) return () => {};
  const listener = (e: MessageEvent<AuthBroadcastEvent>) => handler(e.data);
  ch.addEventListener('message', listener);
  return () => ch.removeEventListener('message', listener);
}
