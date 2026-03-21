import { importJobs, importMappings, importRows } from '@globe-crm/db';
import type {
  CreateImportResponse,
  ImportListResponse,
  ImportProgressResponse,
  SetMappingsRequest,
} from '@globe-crm/types';
import { ImportEntityType, ImportStatus, TARGET_FIELDS } from '@globe-crm/types';
import { desc, eq, sql } from 'drizzle-orm';
import { Hono } from 'hono';
import { db } from '../db.js';
import { parseCsvBuffer } from '../services/csv-parser.js';
import { processImport } from '../services/import-processor.js';

export const importRoutes = new Hono();

const VALID_ENTITY_TYPES = Object.values(ImportEntityType);
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

importRoutes.post('/upload', async (c) => {
  const body = await c.req.parseBody();
  const file = body.file;
  const entityType = body.entityType as string;

  if (!file || !(file instanceof File)) {
    return c.json({ error: 'No file provided' }, 400);
  }

  if (!entityType || !VALID_ENTITY_TYPES.includes(entityType as ImportEntityType)) {
    return c.json({ error: `Invalid entityType. Must be one of: ${VALID_ENTITY_TYPES.join(', ')}` }, 400);
  }

  if (file.size > MAX_FILE_SIZE) {
    return c.json({ error: 'File exceeds maximum size of 10MB' }, 400);
  }

  if (!file.name.endsWith('.csv')) {
    return c.json({ error: 'Only CSV files are supported' }, 400);
  }

  const buffer = Buffer.from(await file.arrayBuffer());
  const { columns, rows } = parseCsvBuffer(buffer);

  if (rows.length === 0) {
    return c.json({ error: 'CSV file is empty or has no data rows' }, 400);
  }

  const [job] = await db
    .insert(importJobs)
    .values({
      entityType: entityType as ImportEntityType,
      status: ImportStatus.Mapping,
      fileName: file.name,
      totalRows: rows.length,
    })
    .returning();

  await db.insert(importRows).values(
    rows.map((data, index) => ({
      importId: job.id,
      rowNumber: index + 1,
      data,
    })),
  );

  const response: CreateImportResponse = {
    import: {
      ...job,
      errorLog: job.errorLog as string[] | null,
    },
    detectedColumns: columns,
  };

  return c.json(response, 201);
});

importRoutes.get('/', async (c) => {
  const limit = Math.min(Number(c.req.query('limit') ?? 20), 100);
  const offset = Number(c.req.query('offset') ?? 0);

  const [jobs, countResult] = await Promise.all([
    db.select().from(importJobs).orderBy(desc(importJobs.createdAt)).limit(limit).offset(offset),
    db.select({ count: sql<number>`count(*)` }).from(importJobs),
  ]);

  const response: ImportListResponse = {
    imports: jobs.map((j) => ({ ...j, errorLog: j.errorLog as string[] | null })),
    total: Number(countResult[0].count),
  };

  return c.json(response);
});

importRoutes.get('/:id', async (c) => {
  const id = c.req.param('id');

  const [job] = await db.select().from(importJobs).where(eq(importJobs.id, id));
  if (!job) {
    return c.json({ error: 'Import not found' }, 404);
  }

  const mappings = await db.select().from(importMappings).where(eq(importMappings.importId, id));

  const response: ImportProgressResponse & { mappings: typeof mappings } = {
    import: { ...job, errorLog: job.errorLog as string[] | null },
    mappings,
  };

  return c.json(response);
});

importRoutes.get('/:id/fields', async (c) => {
  const id = c.req.param('id');

  const [job] = await db.select().from(importJobs).where(eq(importJobs.id, id));
  if (!job) {
    return c.json({ error: 'Import not found' }, 404);
  }

  return c.json({ targetFields: TARGET_FIELDS[job.entityType] });
});

importRoutes.post('/:id/mappings', async (c) => {
  const id = c.req.param('id');

  const [job] = await db.select().from(importJobs).where(eq(importJobs.id, id));
  if (!job) {
    return c.json({ error: 'Import not found' }, 404);
  }

  if (job.status !== ImportStatus.Mapping) {
    return c.json({ error: `Cannot set mappings when import status is "${job.status}"` }, 400);
  }

  const body = (await c.req.json()) as SetMappingsRequest;
  if (!body.mappings || !Array.isArray(body.mappings) || body.mappings.length === 0) {
    return c.json({ error: 'At least one mapping is required' }, 400);
  }

  const validTargetFields = TARGET_FIELDS[job.entityType];
  for (const mapping of body.mappings) {
    if (!mapping.sourceColumn || !mapping.targetField) {
      return c.json({ error: 'Each mapping must have sourceColumn and targetField' }, 400);
    }
    if (!validTargetFields.includes(mapping.targetField)) {
      return c.json(
        { error: `Invalid target field "${mapping.targetField}" for entity type "${job.entityType}"` },
        400,
      );
    }
  }

  await db.delete(importMappings).where(eq(importMappings.importId, id));

  await db.insert(importMappings).values(
    body.mappings.map((m) => ({
      importId: id,
      sourceColumn: m.sourceColumn,
      targetField: m.targetField,
    })),
  );

  return c.json({ message: 'Mappings saved' });
});

importRoutes.post('/:id/process', async (c) => {
  const id = c.req.param('id');

  const [job] = await db.select().from(importJobs).where(eq(importJobs.id, id));
  if (!job) {
    return c.json({ error: 'Import not found' }, 404);
  }

  if (job.status !== ImportStatus.Mapping) {
    return c.json({ error: `Cannot process import with status "${job.status}"` }, 400);
  }

  const mappings = await db.select().from(importMappings).where(eq(importMappings.importId, id));
  if (mappings.length === 0) {
    return c.json({ error: 'No column mappings defined. Set mappings before processing.' }, 400);
  }

  processImport(db, id).catch((err) => {
    console.error(`Import ${id} failed:`, err);
  });

  return c.json({ message: 'Import processing started', importId: id }, 202);
});

importRoutes.delete('/:id', async (c) => {
  const id = c.req.param('id');

  const [job] = await db.select().from(importJobs).where(eq(importJobs.id, id));
  if (!job) {
    return c.json({ error: 'Import not found' }, 404);
  }

  if (job.status === ImportStatus.Processing) {
    return c.json({ error: 'Cannot delete an import that is currently processing' }, 400);
  }

  await db.delete(importJobs).where(eq(importJobs.id, id));
  return c.json({ message: 'Import deleted' });
});
