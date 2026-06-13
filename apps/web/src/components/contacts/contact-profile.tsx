'use client';

import { Camera, Github, Instagram, Linkedin, Loader2, Mail, Phone, Twitter } from 'lucide-react';
import { useMemo, useRef } from 'react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { useAvatarUpload } from '@/hooks/use-contact';
import { useToast } from '@/hooks/use-toast';
import { useTranslations } from '@/hooks/use-translations';
import type { Contact } from '@/lib/api/contacts';
import { AVATAR_ACCEPTED_TYPES, createValidation } from '@/lib/validation';

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

interface ContactProfileProps {
  contact: Contact;
}

export function ContactProfile({ contact }: ContactProfileProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const avatarUpload = useAvatarUpload(contact.id);
  const { success, error } = useToast();
  const d = useTranslations();
  const { validateAvatarFile } = useMemo(() => createValidation(d), [d]);

  const handleAvatarClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const validationError = validateAvatarFile(file);
    if (validationError) {
      error(validationError);
      // reset so the same file can be re-selected after fixing
      e.target.value = '';
      return;
    }

    try {
      await avatarUpload.mutateAsync(file);
      success(d.contacts.profile.uploadSuccess);
    } catch {
      error(d.contacts.profile.uploadError);
    }
    e.target.value = '';
  };

  return (
    <div className="flex flex-col items-center gap-4">
      {/* Avatar with upload trigger */}
      <div className="relative">
        <Avatar size="lg" className="size-24">
          {contact.avatar_url ? <AvatarImage src={contact.avatar_url} alt={contact.name} /> : null}
          <AvatarFallback className="text-2xl">{getInitials(contact.name)}</AvatarFallback>
        </Avatar>

        <button
          type="button"
          onClick={handleAvatarClick}
          disabled={avatarUpload.isPending}
          aria-label={d.contacts.profile.changeAvatarLabel}
          className="absolute bottom-0 right-0 flex size-7 items-center justify-center rounded-full border-2 border-background bg-primary text-primary-foreground shadow-sm transition-opacity hover:opacity-90 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:pointer-events-none disabled:opacity-50"
        >
          {avatarUpload.isPending ? (
            <Loader2 className="size-3.5 animate-spin" aria-hidden="true" />
          ) : (
            <Camera className="size-3.5" aria-hidden="true" />
          )}
        </button>

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept={AVATAR_ACCEPTED_TYPES.join(',')}
          aria-label={d.contacts.profile.fileInputLabel}
          className="sr-only"
          onChange={handleFileChange}
        />
      </div>

      {/* Uploading indicator for screen readers */}
      {avatarUpload.isPending && (
        <p className="sr-only" aria-live="polite" aria-atomic="true">
          {d.contacts.profile.uploadingText}
        </p>
      )}

      <div className="text-center">
        <h1 className="text-2xl font-bold">{contact.name}</h1>

        <div className="mt-2 flex flex-wrap items-center justify-center gap-3 text-sm text-muted-foreground">
          {contact.email ? (
            <a href={`mailto:${contact.email}`} className="flex items-center gap-1 hover:text-foreground">
              <Mail className="size-4" aria-hidden="true" />
              {contact.email}
            </a>
          ) : null}
          {contact.phone ? (
            <a href={`tel:${contact.phone}`} className="flex items-center gap-1 hover:text-foreground">
              <Phone className="size-4" aria-hidden="true" />
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
                aria-label={d.contacts.profile.snsProfileLabel.replace('{{platform}}', key)}
                className="flex size-9 items-center justify-center rounded-full border text-muted-foreground transition-colors hover:bg-accent hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
              >
                <Icon className="size-4" aria-hidden="true" />
              </a>
            );
          })}
        </div>
      ) : null}
    </div>
  );
}
