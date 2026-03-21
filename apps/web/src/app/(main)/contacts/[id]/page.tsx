import { ContactDetail } from '@/components/contacts/contact-detail';

export default async function ContactDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const contactId = Number(id);

  if (Number.isNaN(contactId)) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <p className="text-muted-foreground">Invalid contact ID.</p>
      </div>
    );
  }

  return <ContactDetail contactId={contactId} />;
}
