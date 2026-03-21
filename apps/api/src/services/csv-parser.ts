import { parse } from 'csv-parse/sync';

export interface ParsedCsv {
  columns: string[];
  rows: Record<string, string>[];
}

export function parseCsvBuffer(buffer: Buffer): ParsedCsv {
  const records = parse(buffer, {
    columns: true,
    skip_empty_lines: true,
    trim: true,
    bom: true,
  }) as Record<string, string>[];

  if (records.length === 0) {
    return { columns: [], rows: [] };
  }

  const columns = Object.keys(records[0]);
  return { columns, rows: records };
}
