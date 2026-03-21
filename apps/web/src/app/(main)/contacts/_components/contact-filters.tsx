'use client';

import { Mail, Phone, Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group';
import { useContactFilters } from '../_hooks/use-contact-filters';

const sortOptions = [
  { value: 'created_at_desc', label: 'Newest' },
  { value: 'created_at_asc', label: 'Oldest' },
  { value: 'name_asc', label: 'Name A-Z' },
  { value: 'name_desc', label: 'Name Z-A' },
] as const;

export function ContactFilters() {
  const [filters, setFilters] = useContactFilters();

  const toggleValues: string[] = [];
  if (filters.has_email) toggleValues.push('has_email');
  if (filters.has_phone) toggleValues.push('has_phone');

  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
      <div className="relative flex-1">
        <Search className="absolute top-1/2 left-2.5 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search contacts..."
          value={filters.search}
          onChange={(e) => setFilters({ search: e.target.value || null })}
          className="pl-9"
        />
      </div>
      <div className="flex items-center gap-2">
        <Select value={filters.sort} onValueChange={(value: string) => setFilters({ sort: value || null })}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {sortOptions.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <ToggleGroup
          type="multiple"
          variant="outline"
          size="sm"
          value={toggleValues}
          onValueChange={(value: string[]) => {
            setFilters({
              has_email: value.includes('has_email') || null,
              has_phone: value.includes('has_phone') || null,
            });
          }}
        >
          <ToggleGroupItem value="has_email" aria-label="Has email">
            <Mail className="h-4 w-4" />
          </ToggleGroupItem>
          <ToggleGroupItem value="has_phone" aria-label="Has phone">
            <Phone className="h-4 w-4" />
          </ToggleGroupItem>
        </ToggleGroup>
      </div>
    </div>
  );
}
