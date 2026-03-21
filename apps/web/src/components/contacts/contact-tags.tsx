'use client';

import { Plus, X } from 'lucide-react';
import { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import type { Tag } from '@/lib/api/contacts';

export function ContactTags({ tags, onRemove }: { tags: Tag[]; onRemove?: (tagId: number) => void }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="flex flex-wrap items-center gap-2">
      {tags.map((tag) => (
        <Badge key={tag.id} variant="secondary" className="gap-1">
          {tag.color ? <span className="size-2 rounded-full" style={{ backgroundColor: tag.color }} /> : null}
          {tag.name}
          {onRemove ? (
            <button type="button" onClick={() => onRemove(tag.id)} className="ml-0.5 rounded-full p-0.5 hover:bg-muted">
              <X className="size-3" />
            </button>
          ) : null}
        </Badge>
      ))}

      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger render={<Button variant="outline" size="sm" className="h-7 gap-1 text-xs" />}>
          <Plus className="size-3" />
          Add Tag
        </PopoverTrigger>
        <PopoverContent className="w-48 p-3" align="start">
          <p className="text-sm text-muted-foreground">Tag management coming soon.</p>
        </PopoverContent>
      </Popover>
    </div>
  );
}
