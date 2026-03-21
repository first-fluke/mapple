import { type Database, importJobs, importMappings, importRows } from '@globe-crm/db';
import { eq } from 'drizzle-orm';

interface MappingEntry {
  sourceColumn: string;
  targetField: string;
}

export async function processImport(db: Database, importId: string): Promise<void> {
  await db.update(importJobs).set({ status: 'processing', updatedAt: new Date() }).where(eq(importJobs.id, importId));

  const mappings = await db.select().from(importMappings).where(eq(importMappings.importId, importId));

  const rows = await db.select().from(importRows).where(eq(importRows.importId, importId));

  const errors: string[] = [];
  let processed = 0;
  let failed = 0;

  for (const row of rows) {
    try {
      const mapped = applyMappings(row.data, mappings);
      validateMappedRow(mapped);
      processed++;
    } catch (err) {
      failed++;
      const message = err instanceof Error ? err.message : String(err);
      errors.push(`Row ${row.rowNumber}: ${message}`);

      await db.update(importRows).set({ error: message }).where(eq(importRows.id, row.id));
    }

    if ((processed + failed) % 100 === 0) {
      await db
        .update(importJobs)
        .set({ processedRows: processed, failedRows: failed, updatedAt: new Date() })
        .where(eq(importJobs.id, importId));
    }
  }

  await db
    .update(importJobs)
    .set({
      status: failed === rows.length ? 'failed' : 'completed',
      processedRows: processed,
      failedRows: failed,
      errorLog: errors.length > 0 ? errors : null,
      updatedAt: new Date(),
    })
    .where(eq(importJobs.id, importId));
}

function applyMappings(data: Record<string, string>, mappings: MappingEntry[]): Record<string, string> {
  const result: Record<string, string> = {};
  for (const mapping of mappings) {
    const value = data[mapping.sourceColumn];
    if (value !== undefined) {
      result[mapping.targetField] = value;
    }
  }
  return result;
}

function validateMappedRow(row: Record<string, string>): void {
  const hasAnyValue = Object.values(row).some((v) => v.trim().length > 0);
  if (!hasAnyValue) {
    throw new Error('Row has no non-empty mapped values');
  }
}
