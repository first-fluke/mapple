'use client';

import { Search, X } from 'lucide-react';
import { parseAsString, useQueryState } from 'nuqs';
import { cn } from '@/lib/utils';
import type { LinkType } from '@/types/graph';

const LINK_TYPE_OPTIONS: { value: LinkType | ''; label: string }[] = [
  { value: '', label: 'All types' },
  { value: 'colleague', label: 'Colleague' },
  { value: 'classmate', label: 'Classmate' },
  { value: 'friend', label: 'Friend' },
  { value: 'other', label: 'Other' },
];

export function useGraphFilters() {
  const [search, setSearch] = useQueryState('search', parseAsString.withDefault(''));
  const [type, setType] = useQueryState('type', parseAsString.withDefault(''));
  const [focus] = useQueryState('focus', parseAsString);

  return { search, setSearch, type, setType, focus };
}

export function GraphFilters() {
  const { search, setSearch, type, setType } = useGraphFilters();

  return (
    <div className="flex items-center gap-2">
      <div className="relative">
        <Search className="absolute top-1/2 left-2.5 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search contacts..."
          value={search}
          onChange={(e) => setSearch(e.target.value || null)}
          className={cn(
            'h-9 w-48 rounded-md border border-input bg-background py-1 pr-8 pl-8 text-sm',
            'placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring',
          )}
        />
        {search && (
          <button
            type="button"
            onClick={() => setSearch(null)}
            className="absolute top-1/2 right-2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        )}
      </div>
      <select
        value={type}
        onChange={(e) => setType(e.target.value || null)}
        className={cn(
          'h-9 rounded-md border border-input bg-background px-3 text-sm',
          'focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring',
        )}
      >
        {LINK_TYPE_OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}
