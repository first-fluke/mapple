'use client';

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import type { Meeting } from '@/lib/api/contacts';

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export function ContactMeetings({ meetings }: { meetings: Meeting[] }) {
  if (meetings.length === 0) {
    return <p className="text-sm text-muted-foreground">No meetings recorded.</p>;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Title</TableHead>
          <TableHead>Date</TableHead>
          <TableHead>Location</TableHead>
          <TableHead className="hidden md:table-cell">Notes</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {meetings.map((meeting) => (
          <TableRow key={meeting.id}>
            <TableCell className="font-medium">{meeting.title}</TableCell>
            <TableCell>{formatDate(meeting.date)}</TableCell>
            <TableCell>{meeting.location ?? '—'}</TableCell>
            <TableCell className="hidden max-w-48 truncate md:table-cell">{meeting.notes ?? '—'}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
