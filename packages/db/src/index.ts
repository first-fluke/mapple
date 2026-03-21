import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as schema from './schema/index.js';

export function createDb(connectionString?: string) {
  const client = postgres(
    connectionString ?? process.env.DATABASE_URL ?? 'postgres://globe:globe@localhost:5432/globe_crm',
  );
  return drizzle(client, { schema });
}

export type Database = ReturnType<typeof createDb>;

export * from './schema/index.js';
