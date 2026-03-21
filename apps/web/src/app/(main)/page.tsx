'use client';

import { useState } from 'react';
import { type Contact, GlobeView } from '@/components/globe';

const DEMO_CONTACTS: Contact[] = [
  {
    id: '1',
    name: 'Alice Johnson',
    email: 'alice@example.com',
    location: 'New York, US',
    relationships: [
      { contactName: 'Bob Smith', type: 'business' },
      { contactName: 'Carol Lee', type: 'friend' },
    ],
  },
  {
    id: '2',
    name: 'Bob Smith',
    email: 'bob@example.com',
    location: 'London, UK',
    relationships: [{ contactName: 'Alice Johnson', type: 'business' }],
  },
  {
    id: '3',
    name: 'Carol Lee',
    email: 'carol@example.com',
    location: 'Tokyo, JP',
    relationships: [
      { contactName: 'Alice Johnson', type: 'friend' },
      { contactName: 'David Kim', type: 'family' },
    ],
  },
  {
    id: '4',
    name: 'David Kim',
    email: 'david@example.com',
    location: 'Seoul, KR',
    relationships: [{ contactName: 'Carol Lee', type: 'family' }],
  },
];

export default function HomePage() {
  const [selectedId, setSelectedId] = useState<string>();

  return (
    <div className="flex h-full flex-col">
      <h1 className="sr-only">Globe CRM — Contact Map</h1>
      <GlobeView contacts={DEMO_CONTACTS} onSelectContact={setSelectedId} selectedContactId={selectedId} />
    </div>
  );
}
