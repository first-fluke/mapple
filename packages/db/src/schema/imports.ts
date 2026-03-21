import { integer, jsonb, pgEnum, pgTable, text, timestamp, uuid, varchar } from 'drizzle-orm/pg-core';

export const importStatusEnum = pgEnum('import_status', ['pending', 'mapping', 'processing', 'completed', 'failed']);

export const importEntityTypeEnum = pgEnum('import_entity_type', ['contacts', 'companies', 'deals']);

export const importJobs = pgTable('import_jobs', {
  id: uuid('id').defaultRandom().primaryKey(),
  entityType: importEntityTypeEnum('entity_type').notNull(),
  status: importStatusEnum('status').notNull().default('pending'),
  fileName: varchar('file_name', { length: 255 }).notNull(),
  totalRows: integer('total_rows').notNull().default(0),
  processedRows: integer('processed_rows').notNull().default(0),
  failedRows: integer('failed_rows').notNull().default(0),
  errorLog: jsonb('error_log').$type<string[]>(),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
});

export const importMappings = pgTable('import_mappings', {
  id: uuid('id').defaultRandom().primaryKey(),
  importId: uuid('import_id')
    .notNull()
    .references(() => importJobs.id, { onDelete: 'cascade' }),
  sourceColumn: varchar('source_column', { length: 255 }).notNull(),
  targetField: varchar('target_field', { length: 255 }).notNull(),
});

export const importRows = pgTable('import_rows', {
  id: uuid('id').defaultRandom().primaryKey(),
  importId: uuid('import_id')
    .notNull()
    .references(() => importJobs.id, { onDelete: 'cascade' }),
  rowNumber: integer('row_number').notNull(),
  data: jsonb('data').notNull().$type<Record<string, string>>(),
  error: text('error'),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
});
