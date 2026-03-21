'use client';

import { ArrowLeft, Globe, Loader2, Network } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useContact, useExperiences, useMeetings, useTags } from '@/hooks/use-contact';
import { ContactMeetings } from './contact-meetings';
import { ContactProfile } from './contact-profile';
import { ContactTags } from './contact-tags';
import { ContactTimeline } from './contact-timeline';

export function ContactDetail({ contactId }: { contactId: number }) {
  const { data: contact, isLoading, error } = useContact(contactId);
  const { data: experiences = [] } = useExperiences(contactId);
  const { data: meetings = [] } = useMeetings(contactId);
  const { data: tags = [] } = useTags(contactId);

  if (isLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <Loader2 className="size-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error || !contact) {
    return (
      <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4">
        <p className="text-muted-foreground">Contact not found.</p>
        <Button variant="outline" render={<Link href="/contacts" />}>
          Back to Contacts
        </Button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <Button variant="ghost" size="sm" render={<Link href="/contacts" />} className="gap-1">
          <ArrowLeft className="size-4" />
          Back
        </Button>

        <div className="flex gap-2">
          <Button variant="outline" size="sm" className="gap-1">
            <Globe className="size-4" />
            Globe View
          </Button>
          <Button variant="outline" size="sm" className="gap-1">
            <Network className="size-4" />
            Relationship View
          </Button>
        </div>
      </div>

      <Card>
        <CardContent className="pt-6">
          <ContactProfile contact={contact} />
        </CardContent>
      </Card>

      <Separator />

      <Tabs defaultValue="timeline">
        <TabsList>
          <TabsTrigger value="timeline">Timeline</TabsTrigger>
          <TabsTrigger value="meetings">Meetings</TabsTrigger>
          <TabsTrigger value="tags">Tags</TabsTrigger>
        </TabsList>

        <TabsContent value="timeline" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Career Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              <ContactTimeline experiences={experiences} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="meetings" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Meetings</CardTitle>
            </CardHeader>
            <CardContent>
              <ContactMeetings meetings={meetings} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tags" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Tags</CardTitle>
            </CardHeader>
            <CardContent>
              <ContactTags tags={tags} />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
