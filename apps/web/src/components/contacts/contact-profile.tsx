'use client';

import { Github, Instagram, Linkedin, Mail, Phone, Twitter } from 'lucide-react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import type { Contact } from '@/lib/api/contacts';

function getInitials(name: string) {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();
}

const snsIcons = {
  linkedin: Linkedin,
  twitter: Twitter,
  github: Github,
  instagram: Instagram,
} as const;

export function ContactProfile({ contact }: { contact: Contact }) {
  return (
    <div className="flex flex-col items-center gap-4">
      <Avatar size="lg" className="size-24">
        {contact.avatar_url ? <AvatarImage src={contact.avatar_url} alt={contact.name} /> : null}
        <AvatarFallback className="text-2xl">{getInitials(contact.name)}</AvatarFallback>
      </Avatar>

      <div className="text-center">
        <h1 className="text-2xl font-bold">{contact.name}</h1>

        <div className="mt-2 flex flex-wrap items-center justify-center gap-3 text-sm text-muted-foreground">
          {contact.email ? (
            <a href={`mailto:${contact.email}`} className="flex items-center gap-1 hover:text-foreground">
              <Mail className="size-4" />
              {contact.email}
            </a>
          ) : null}
          {contact.phone ? (
            <a href={`tel:${contact.phone}`} className="flex items-center gap-1 hover:text-foreground">
              <Phone className="size-4" />
              {contact.phone}
            </a>
          ) : null}
        </div>
      </div>

      {contact.sns ? (
        <div className="flex gap-2">
          {(Object.entries(contact.sns) as [keyof typeof snsIcons, string][]).map(([key, url]) => {
            if (!url) return null;
            const Icon = snsIcons[key];
            if (!Icon) return null;
            return (
              <a
                key={key}
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex size-9 items-center justify-center rounded-full border text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
              >
                <Icon className="size-4" />
              </a>
            );
          })}
        </div>
      ) : null}
    </div>
  );
}
