'use client';

import { Globe, Mail, MapPin, Phone, Plus } from 'lucide-react';
import { useState } from 'react';
import { AddContactWizard } from '@/components/contacts/add-contact-wizard';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useContacts } from '@/hooks/use-contacts';

export default function ContactsPage() {
  const [wizardOpen, setWizardOpen] = useState(false);
  const { data: contacts, isLoading } = useContacts();

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Contacts</h1>
        <Button onClick={() => setWizardOpen(true)}>
          <Plus className="mr-1 h-4 w-4" />
          Add Contact
        </Button>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <p className="text-muted-foreground">Loading contacts...</p>
        </div>
      )}

      {!isLoading && contacts?.length === 0 && (
        <div className="flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed py-12">
          <Globe className="h-10 w-10 text-muted-foreground/50" />
          <p className="text-muted-foreground">No contacts yet</p>
          <Button variant="outline" size="sm" onClick={() => setWizardOpen(true)}>
            <Plus className="mr-1 h-3 w-3" />
            Add your first contact
          </Button>
        </div>
      )}

      {contacts && contacts.length > 0 && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {contacts.map((contact) => (
            <div
              key={contact.id}
              className="flex flex-col gap-2 rounded-lg border p-4 transition-colors hover:bg-muted/50"
            >
              <div className="flex items-start justify-between">
                <h3 className="font-medium">{contact.name}</h3>
                {contact.country && <span className="text-xs text-muted-foreground">{contact.country}</span>}
              </div>

              <div className="flex flex-col gap-1 text-sm text-muted-foreground">
                {contact.email && (
                  <div className="flex items-center gap-1.5">
                    <Mail className="h-3 w-3" />
                    <span className="truncate">{contact.email}</span>
                  </div>
                )}
                {contact.phone && (
                  <div className="flex items-center gap-1.5">
                    <Phone className="h-3 w-3" />
                    <span>{contact.phone}</span>
                  </div>
                )}
                {contact.city && (
                  <div className="flex items-center gap-1.5">
                    <MapPin className="h-3 w-3" />
                    <span>
                      {contact.city}
                      {contact.country ? `, ${contact.country}` : ''}
                    </span>
                  </div>
                )}
              </div>

              {contact.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 pt-1">
                  {contact.tags.map((tag) => (
                    <Badge key={tag.id} variant="secondary">
                      {tag.name}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <AddContactWizard open={wizardOpen} onOpenChange={setWizardOpen} />
    </div>
  );
}
