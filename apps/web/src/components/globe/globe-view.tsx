'use client';

import { List, RotateCcw } from 'lucide-react';
import { useScreenReader } from '@/hooks/use-screen-reader';
import { handleKeyboardActivate } from '@/lib/a11y';
import { cn } from '@/lib/utils';
import { type Contact, ContactListView } from './contact-list-view';

interface GlobeViewProps {
  contacts: Contact[];
  onSelectContact?: (id: string) => void;
  selectedContactId?: string;
}

export function GlobeView({ contacts, onSelectContact, selectedContactId }: GlobeViewProps) {
  const { shouldUseListView, prefersListView, reducedMotion, toggleListView } = useScreenReader();

  return (
    <div className="relative flex h-full flex-col">
      {/* View toggle button — always visible for opt-in/opt-out */}
      <div className="flex items-center justify-end gap-2 p-2">
        {reducedMotion && !prefersListView && (
          <output className="text-xs text-muted-foreground">Reduced motion detected — showing list view.</output>
        )}
        <button
          type="button"
          onClick={toggleListView}
          onKeyDown={handleKeyboardActivate(toggleListView)}
          className={cn(
            'inline-flex min-h-12 min-w-12 items-center justify-center gap-2 rounded-lg border px-3 py-2 text-sm transition-colors',
            'hover:bg-accent focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring',
          )}
          aria-pressed={prefersListView}
          aria-label={shouldUseListView ? 'Switch to globe view' : 'Switch to list view'}
        >
          {shouldUseListView ? (
            <>
              <RotateCcw className="h-4 w-4" aria-hidden="true" />
              <span className="hidden sm:inline">Globe View</span>
            </>
          ) : (
            <>
              <List className="h-4 w-4" aria-hidden="true" />
              <span className="hidden sm:inline">List View</span>
            </>
          )}
        </button>
      </div>

      {shouldUseListView ? (
        <ContactListView contacts={contacts} onSelectContact={onSelectContact} selectedContactId={selectedContactId} />
      ) : (
        <div
          className="flex flex-1 items-center justify-center"
          role="img"
          aria-label={`Interactive globe showing ${contacts.length} contacts. Switch to list view for screen reader accessible version.`}
        >
          {/* Globe 3D visualization placeholder — will be replaced by actual globe renderer (e.g. react-globe.gl) */}
          <div className="flex h-64 w-64 items-center justify-center rounded-full border-2 border-dashed border-muted-foreground/30">
            <p className="text-muted-foreground">Globe Visualization</p>
          </div>
        </div>
      )}
    </div>
  );
}
