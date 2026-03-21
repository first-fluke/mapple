'use client';

import { useVirtualizer } from '@tanstack/react-virtual';
import { Loader2, Mail, Phone } from 'lucide-react';
import { useCallback, useEffect, useRef } from 'react';
import { Badge } from '@/components/ui/badge';
import type { Contact } from '../_hooks/use-contacts';

const ROW_HEIGHT = 72;

interface ContactListProps {
  contacts: Contact[];
  hasNextPage: boolean;
  isFetchingNextPage: boolean;
  fetchNextPage: () => void;
}

export function ContactList({ contacts, hasNextPage, isFetchingNextPage, fetchNextPage }: ContactListProps) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: hasNextPage ? contacts.length + 1 : contacts.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => ROW_HEIGHT,
    overscan: 5,
  });

  const virtualItems = virtualizer.getVirtualItems();

  const loadMore = useCallback(() => {
    if (hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  useEffect(() => {
    const lastItem = virtualItems[virtualItems.length - 1];
    if (!lastItem) return;
    if (lastItem.index >= contacts.length - 1 && hasNextPage && !isFetchingNextPage) {
      loadMore();
    }
  }, [virtualItems, contacts.length, hasNextPage, isFetchingNextPage, loadMore]);

  return (
    <div ref={parentRef} className="flex-1 overflow-y-auto rounded-lg border">
      <div className="relative w-full" style={{ height: `${virtualizer.getTotalSize()}px` }}>
        {virtualItems.map((virtualRow) => {
          const isLoaderRow = virtualRow.index >= contacts.length;

          if (isLoaderRow) {
            return (
              <div
                key="loader"
                className="absolute top-0 left-0 flex w-full items-center justify-center"
                style={{
                  height: `${virtualRow.size}px`,
                  transform: `translateY(${virtualRow.start}px)`,
                }}
              >
                <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
              </div>
            );
          }

          const contact = contacts[virtualRow.index];

          return (
            <div
              key={contact.id}
              className="absolute top-0 left-0 flex w-full items-center gap-3 border-b px-4"
              style={{
                height: `${virtualRow.size}px`,
                transform: `translateY(${virtualRow.start}px)`,
              }}
            >
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-muted text-sm font-medium">
                {contact.name.charAt(0).toUpperCase()}
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate font-medium text-sm">{contact.name}</p>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  {contact.email && (
                    <span className="flex items-center gap-1 truncate">
                      <Mail className="h-3 w-3 shrink-0" />
                      {contact.email}
                    </span>
                  )}
                  {contact.phone && (
                    <span className="flex items-center gap-1">
                      <Phone className="h-3 w-3 shrink-0" />
                      {contact.phone}
                    </span>
                  )}
                </div>
              </div>
              {!contact.email && !contact.phone && <Badge variant="secondary">No info</Badge>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
