'use client';

import { Pencil, Trash2 } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { useDeleteMeeting } from '@/hooks/use-contact';
import { useToast } from '@/hooks/use-toast';
import { useTranslations } from '@/hooks/use-translations';
import type { Meeting } from '@/lib/api/contacts';
import { MeetingFormDialog } from './meeting-form-dialog';

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

interface ContactMeetingsProps {
  contactId: number;
  meetings: Meeting[];
}

export function ContactMeetings({ contactId, meetings }: ContactMeetingsProps) {
  const [editTarget, setEditTarget] = useState<Meeting | null>(null);
  const deleteMeeting = useDeleteMeeting(contactId);
  const { success, error } = useToast();
  const d = useTranslations();

  const handleDelete = async (meeting: Meeting) => {
    try {
      await deleteMeeting.mutateAsync(meeting.id);
      success(d.contacts.meeting.toastDeleted);
    } catch {
      error(d.contacts.meeting.toastDeleteFailed);
    }
  };

  if (meetings.length === 0) {
    return <p className="text-sm text-muted-foreground">{d.contacts.meeting.empty}</p>;
  }

  return (
    <>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>{d.contacts.meeting.colTitle}</TableHead>
            <TableHead>{d.contacts.meeting.colDate}</TableHead>
            <TableHead>{d.contacts.meeting.colLocation}</TableHead>
            <TableHead className="hidden md:table-cell">{d.contacts.meeting.colNotes}</TableHead>
            <TableHead className="w-20 text-right">{d.contacts.meeting.colManage}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {meetings.map((meeting) => (
            <TableRow key={meeting.id}>
              <TableCell className="font-medium">{meeting.title}</TableCell>
              <TableCell>{formatDate(meeting.date)}</TableCell>
              <TableCell>{meeting.location ?? '—'}</TableCell>
              <TableCell className="hidden max-w-48 truncate md:table-cell">{meeting.notes ?? '—'}</TableCell>
              <TableCell className="text-right">
                <div className="flex items-center justify-end gap-1">
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="size-7"
                    aria-label={d.contacts.meeting.editLabel.replace('{{name}}', meeting.title)}
                    onClick={() => setEditTarget(meeting)}
                  >
                    <Pencil className="size-3.5" aria-hidden="true" />
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="size-7 text-destructive hover:text-destructive"
                    aria-label={d.contacts.meeting.deleteLabel.replace('{{name}}', meeting.title)}
                    disabled={deleteMeeting.isPending}
                    onClick={() => handleDelete(meeting)}
                  >
                    <Trash2 className="size-3.5" aria-hidden="true" />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <MeetingFormDialog
        contactId={contactId}
        meeting={editTarget ?? undefined}
        open={editTarget !== null}
        onOpenChange={(open) => {
          if (!open) setEditTarget(null);
        }}
      />
    </>
  );
}
