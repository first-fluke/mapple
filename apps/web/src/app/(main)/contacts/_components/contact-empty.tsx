'use client';

import { Contact } from 'lucide-react';
import { useTranslations } from '@/hooks/use-translations';

interface ContactEmptyProps {
  hasFilters: boolean;
}

export function ContactEmpty({ hasFilters }: ContactEmptyProps) {
  const t = useTranslations();
  const empty = hasFilters ? t.contacts.emptyFiltered : t.contacts.emptyNoFilter;

  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-3 rounded-lg border border-dashed p-12">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted">
        <Contact className="h-6 w-6 text-muted-foreground" />
      </div>
      <h3 className="font-medium text-sm">{empty.title}</h3>
      <p className="text-center text-muted-foreground text-sm">{empty.description}</p>
    </div>
  );
}
