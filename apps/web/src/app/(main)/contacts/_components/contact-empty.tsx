import { Contact } from 'lucide-react';

interface ContactEmptyProps {
  hasFilters: boolean;
}

export function ContactEmpty({ hasFilters }: ContactEmptyProps) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-3 rounded-lg border border-dashed p-12">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted">
        <Contact className="h-6 w-6 text-muted-foreground" />
      </div>
      {hasFilters ? (
        <>
          <h3 className="font-medium text-sm">No contacts found</h3>
          <p className="text-center text-muted-foreground text-sm">Try adjusting your search or filters.</p>
        </>
      ) : (
        <>
          <h3 className="font-medium text-sm">No contacts yet</h3>
          <p className="text-center text-muted-foreground text-sm">Your contacts will appear here once added.</p>
        </>
      )}
    </div>
  );
}
