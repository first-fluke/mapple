import { defineCloudflareConfig } from '@opennextjs/cloudflare';

// Default configuration deploys to Cloudflare Workers with no external cache.
// To enable ISR/SSG incremental cache on Workers KV, import and pass an
// incrementalCache adapter here and bind NEXT_INC_CACHE_KV in wrangler.jsonc.
export default defineCloudflareConfig();
