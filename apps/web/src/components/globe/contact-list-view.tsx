'use client';

import { RELATIONSHIP_STYLES, type RelationshipType } from '@/lib/a11y';
import { cn } from '@/lib/utils';

export interface Contact {
  id: string;
  name: string;
  email?: string;
  location?: string;
  relationships: Array<{
    contactName: string;
    type: RelationshipType;
  }>;
}

interface ContactListViewProps {
  contacts: Contact[];
  onSelectContact?: (id: string) => void;
  selectedContactId?: string;
}

export function ContactListView({ contacts, onSelectContact, selectedContactId }: ContactListViewProps) {
  return (
    <section aria-label="Contacts list view">
      <ul className="divide-y divide-border">
        {contacts.length === 0 && (
          <li className="px-4 py-8 text-center text-muted-foreground">No contacts to display.</li>
        )}
        {contacts.map((contact) => (
          <li key={contact.id}>
            <button
              type="button"
              onClick={() => onSelectContact?.(contact.id)}
              className={cn(
                'flex min-h-12 w-full items-start gap-4 px-4 py-3 text-left transition-colors',
                'hover:bg-accent focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-ring',
                selectedContactId === contact.id && 'bg-accent',
              )}
              aria-current={selectedContactId === contact.id ? 'true' : undefined}
            >
              <div className="flex min-h-12 min-w-12 items-center justify-center rounded-full bg-muted text-sm font-medium">
                {contact.name.charAt(0).toUpperCase()}
              </div>
              <div className="flex-1">
                <p className="font-medium">{contact.name}</p>
                {contact.email && <p className="text-sm text-muted-foreground">{contact.email}</p>}
                {contact.location && <p className="text-sm text-muted-foreground">{contact.location}</p>}
                {contact.relationships.length > 0 && (
                  <div className="mt-1">
                    <p className="sr-only">Relationships:</p>
                    <ul className="flex flex-wrap gap-2">
                      {contact.relationships.map((rel) => {
                        const style = RELATIONSHIP_STYLES[rel.type];
                        return (
                          <li
                            key={`${contact.id}-${rel.contactName}-${rel.type}`}
                            className="inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-xs"
                          >
                            <svg width="16" height="2" aria-hidden="true" className="shrink-0">
                              <line
                                x1="0"
                                y1="1"
                                x2="16"
                                y2="1"
                                stroke={style.color}
                                strokeWidth="2"
                                strokeDasharray={style.dashArray === 'none' ? undefined : style.dashArray}
                              />
                            </svg>
                            <span>
                              {rel.contactName}
                              <span className="sr-only">
                                {' '}
                                ({style.label} — {style.description})
                              </span>
                            </span>
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                )}
              </div>
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
