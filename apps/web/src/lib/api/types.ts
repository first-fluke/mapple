export interface ErrorDetail {
  code: string;
  message: string;
  details?: unknown;
}

export interface ApiResponse<T> {
  data: T;
  meta?: Record<string, unknown>;
  errors?: ErrorDetail[];
}

export interface ErrorResponse {
  error: ErrorDetail;
}

export interface PaginationMeta {
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
}

export interface CursorMeta {
  per_page: number;
  next_cursor: string | null;
  has_more: boolean;
}
