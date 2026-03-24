'use client';

import { Loader2 } from 'lucide-react';
import { Suspense } from 'react';
import { ContactEmpty } from './_components/contact-empty';
import { ContactFilters } from './_components/contact-filters';
import { ContactList } from './_components/contact-list';
import { useContactFilters } from './_hooks/use-contact-filters';
import { useContacts } from './_hooks/use-contacts';

function ContactsContent() {
  const [filters] = useContactFilters();
  const { data, hasNextPage, isFetchingNextPage, fetchNextPage, isLoading } = useContacts(filters);

  const contacts = data?.pages.flatMap((page) => page.data) ?? [];
  const hasFilters = !!(filters.search || filters.has_email || filters.has_phone);

  return (
    <div className="flex h-full flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="font-semibold text-lg">Contacts</h1>
      </div>
      <ContactFilters />
      {isLoading ? (
        <div className="flex flex-1 items-center justify-center">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : contacts.length === 0 ? (
        <ContactEmpty hasFilters={hasFilters} />
      ) : (
        <ContactList
          contacts={contacts}
          hasNextPage={hasNextPage}
          isFetchingNextPage={isFetchingNextPage}
          fetchNextPage={fetchNextPage}
        />
      )}
    </div>
  );
}

export default function ContactsPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-full items-center justify-center">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      }
    >
      <ContactsContent />
    </Suspense>
  );
}
