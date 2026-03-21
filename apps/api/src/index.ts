import { serve } from '@hono/node-server';
import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { logger } from 'hono/logger';
import { importRoutes } from './routes/imports.js';

const app = new Hono();

app.use('*', logger());
app.use('*', cors());

app.get('/health', (c) => c.json({ status: 'ok' }));

app.route('/api/imports', importRoutes);

const port = Number(process.env.PORT ?? 3000);
console.log(`Globe CRM API running on port ${port}`);

serve({ fetch: app.fetch, port });

export default app;
