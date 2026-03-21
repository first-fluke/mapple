export const ImportStatus = {
  Pending: 'pending',
  Mapping: 'mapping',
  Processing: 'processing',
  Completed: 'completed',
  Failed: 'failed',
} as const;

export type ImportStatus = (typeof ImportStatus)[keyof typeof ImportStatus];

export const ImportEntityType = {
  Contacts: 'contacts',
  Companies: 'companies',
  Deals: 'deals',
} as const;

export type ImportEntityType = (typeof ImportEntityType)[keyof typeof ImportEntityType];

export interface ImportJob {
  id: string;
  entityType: ImportEntityType;
  status: ImportStatus;
  fileName: string;
  totalRows: number;
  processedRows: number;
  failedRows: number;
  errorLog: string[] | null;
  createdAt: Date;
  updatedAt: Date;
}

export interface ImportMapping {
  id: string;
  importId: string;
  sourceColumn: string;
  targetField: string;
}

export interface CreateImportRequest {
  entityType: ImportEntityType;
}

export interface CreateImportResponse {
  import: ImportJob;
  detectedColumns: string[];
}

export interface SetMappingsRequest {
  mappings: Array<{
    sourceColumn: string;
    targetField: string;
  }>;
}

export interface ImportProgressResponse {
  import: ImportJob;
}

export interface ImportListResponse {
  imports: ImportJob[];
  total: number;
}

export const TARGET_FIELDS: Record<ImportEntityType, string[]> = {
  contacts: ['firstName', 'lastName', 'email', 'phone', 'company', 'title', 'address', 'city', 'country', 'notes'],
  companies: ['name', 'domain', 'industry', 'size', 'address', 'city', 'country', 'phone', 'notes'],
  deals: ['title', 'value', 'currency', 'stage', 'contactEmail', 'companyName', 'expectedCloseDate', 'notes'],
};
