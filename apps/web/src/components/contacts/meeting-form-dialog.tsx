'use client';

import { useForm } from '@tanstack/react-form';
import { Loader2 } from 'lucide-react';
import { useMemo } from 'react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useCreateMeeting, useUpdateMeeting } from '@/hooks/use-contact';
import { useToast } from '@/hooks/use-toast';
import { useTranslations } from '@/hooks/use-translations';
import type { Meeting } from '@/lib/api/contacts';
import { createValidation } from '@/lib/validation';

interface MeetingFormDialogProps {
  contactId: number;
  meeting?: Meeting;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function MeetingFormDialog({ contactId, meeting, open, onOpenChange }: MeetingFormDialogProps) {
  const isEdit = Boolean(meeting);
  const createMeeting = useCreateMeeting(contactId);
  const updateMeeting = useUpdateMeeting(contactId);
  const { success, error } = useToast();
  const d = useTranslations();
  const { meetingSchema } = useMemo(() => createValidation(d), [d]);

  const toLocalDatetime = (iso: string | undefined) => {
    if (!iso) return '';
    const dt = new Date(iso);
    const pad = (n: number) => String(n).padStart(2, '0');
    return `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())}T${pad(dt.getHours())}:${pad(dt.getMinutes())}`;
  };

  const form = useForm({
    defaultValues: {
      title: meeting?.title ?? '',
      starts_at: toLocalDatetime(meeting?.starts_at ?? meeting?.date),
      ends_at: toLocalDatetime(meeting?.ends_at),
      location: meeting?.location ?? '',
      notes: meeting?.notes ?? '',
    },
    validators: {
      onSubmit: ({ value }) => {
        const result = meetingSchema.safeParse(value);
        if (!result.success) {
          return result.error.issues[0]?.message ?? d.contacts.meeting.validationInputCheck;
        }
        return undefined;
      },
    },
    onSubmit: async ({ value }) => {
      try {
        const payload = {
          title: value.title,
          starts_at: value.starts_at,
          ends_at: value.ends_at,
          location: value.location || null,
          notes: value.notes || null,
        };

        if (isEdit && meeting) {
          await updateMeeting.mutateAsync({ meetingId: meeting.id, data: payload });
          success(d.contacts.meeting.toastEdited);
        } else {
          await createMeeting.mutateAsync(payload);
          success(d.contacts.meeting.toastAdded);
        }
        onOpenChange(false);
        form.reset();
      } catch {
        error(isEdit ? d.contacts.meeting.toastEditFailed : d.contacts.meeting.toastAddFailed);
      }
    },
  });

  const isPending = createMeeting.isPending || updateMeeting.isPending;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{isEdit ? d.contacts.meeting.editTitle : d.contacts.meeting.addTitle}</DialogTitle>
        </DialogHeader>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            form.handleSubmit();
          }}
          className="flex flex-col gap-4"
          noValidate
        >
          <form.Field
            name="title"
            validators={{
              onChange: ({ value }) => (!value.trim() ? d.contacts.meeting.validationTitleRequired : undefined),
            }}
          >
            {(field) => (
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="meeting-title">
                  {d.contacts.meeting.titleLabel} <span aria-hidden="true">*</span>
                </Label>
                <Input
                  id="meeting-title"
                  placeholder={d.contacts.meeting.titlePlaceholder}
                  value={field.state.value}
                  onChange={(e) => field.handleChange(e.target.value)}
                  onBlur={field.handleBlur}
                  aria-required="true"
                  aria-invalid={field.state.meta.errors.length > 0}
                  aria-describedby={field.state.meta.errors.length > 0 ? 'meeting-title-error' : undefined}
                />
                {field.state.meta.errors.length > 0 && (
                  <p id="meeting-title-error" className="text-xs text-destructive" role="alert">
                    {field.state.meta.errors[0]}
                  </p>
                )}
              </div>
            )}
          </form.Field>

          <div className="grid grid-cols-2 gap-3">
            <form.Field
              name="starts_at"
              validators={{
                onChange: ({ value }) => (!value ? d.contacts.meeting.validationStartsAtRequired : undefined),
              }}
            >
              {(field) => (
                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="meeting-starts-at">
                    {d.contacts.meeting.startsAtLabel} <span aria-hidden="true">*</span>
                  </Label>
                  <Input
                    id="meeting-starts-at"
                    type="datetime-local"
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                    aria-required="true"
                    aria-invalid={field.state.meta.errors.length > 0}
                  />
                  {field.state.meta.errors.length > 0 && (
                    <p className="text-xs text-destructive" role="alert">
                      {field.state.meta.errors[0]}
                    </p>
                  )}
                </div>
              )}
            </form.Field>

            <form.Field
              name="ends_at"
              validators={{
                onChange: ({ value }) => (!value ? d.contacts.meeting.validationEndsAtRequired : undefined),
              }}
            >
              {(field) => (
                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="meeting-ends-at">
                    {d.contacts.meeting.endsAtLabel} <span aria-hidden="true">*</span>
                  </Label>
                  <Input
                    id="meeting-ends-at"
                    type="datetime-local"
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                    aria-required="true"
                    aria-invalid={field.state.meta.errors.length > 0}
                  />
                  {field.state.meta.errors.length > 0 && (
                    <p className="text-xs text-destructive" role="alert">
                      {field.state.meta.errors[0]}
                    </p>
                  )}
                </div>
              )}
            </form.Field>
          </div>

          <form.Field name="location">
            {(field) => (
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="meeting-location">{d.contacts.meeting.locationLabel}</Label>
                <Input
                  id="meeting-location"
                  placeholder={d.contacts.meeting.locationPlaceholder}
                  value={field.state.value}
                  onChange={(e) => field.handleChange(e.target.value)}
                />
              </div>
            )}
          </form.Field>

          <form.Field name="notes">
            {(field) => (
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="meeting-notes">{d.contacts.meeting.notesLabel}</Label>
                <Textarea
                  id="meeting-notes"
                  placeholder={d.contacts.meeting.notesPlaceholder}
                  value={field.state.value}
                  onChange={(e) => field.handleChange(e.target.value)}
                  rows={3}
                />
              </div>
            )}
          </form.Field>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              {d.contacts.meeting.cancelButton}
            </Button>
            <Button type="submit" disabled={isPending}>
              {isPending && <Loader2 className="mr-1 size-4 animate-spin" aria-hidden="true" />}
              {isEdit ? d.contacts.meeting.editButton : d.contacts.meeting.addButton}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
