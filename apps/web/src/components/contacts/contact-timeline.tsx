'use client';

import { Briefcase, GraduationCap, Pencil, Plus, Trash2 } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { useDeleteExperience } from '@/hooks/use-contact';
import { useToast } from '@/hooks/use-toast';
import { useTranslations } from '@/hooks/use-translations';
import type { Experience } from '@/lib/api/contacts';
import { ExperienceFormDialog } from './experience-form-dialog';

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'short',
  });
}

function getOrgIcon(type: string) {
  if (type === 'school' || type === 'university') {
    return GraduationCap;
  }
  return Briefcase;
}

interface ContactTimelineProps {
  contactId: number;
  experiences: Experience[];
}

export function ContactTimeline({ contactId, experiences }: ContactTimelineProps) {
  const [addOpen, setAddOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<Experience | null>(null);
  const deleteExperience = useDeleteExperience(contactId);
  const { success, error } = useToast();
  const d = useTranslations();

  const handleDelete = async (exp: Experience) => {
    try {
      await deleteExperience.mutateAsync(exp.id);
      success(d.contacts.experience.toastDeleted);
    } catch {
      error(d.contacts.experience.toastDeleteFailed);
    }
  };

  const sorted = [...experiences].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

  return (
    <>
      <div className="mb-3 flex items-center justify-between">
        <span className="text-sm text-muted-foreground">
          {experiences.length > 0
            ? d.contacts.experience.count.replace('{{count}}', String(experiences.length))
            : d.contacts.experience.empty}
        </span>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => setAddOpen(true)}
          className="h-7 gap-1 text-xs"
          aria-label={d.contacts.experience.addLabel}
        >
          <Plus className="size-3.5" aria-hidden="true" />
          {d.contacts.detail.addButton}
        </Button>
      </div>

      {sorted.length === 0 ? (
        <p className="text-sm text-muted-foreground">{d.contacts.experience.empty}</p>
      ) : (
        <div className="relative space-y-0">
          {sorted.map((exp, idx) => {
            const Icon = getOrgIcon(exp.organization.type);
            const isLast = idx === sorted.length - 1;

            return (
              <div key={exp.id} className="flex gap-4">
                <div className="flex flex-col items-center">
                  <div className="flex size-8 shrink-0 items-center justify-center rounded-full border bg-background">
                    <Icon className="size-4 text-muted-foreground" aria-hidden="true" />
                  </div>
                  {!isLast ? <Separator orientation="vertical" className="my-1 h-full min-h-6" /> : null}
                </div>

                <Card className="mb-3 flex-1">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0 flex-1">
                        <p className="truncate font-medium">{exp.organization.name}</p>
                        {exp.role ? <p className="text-sm text-muted-foreground">{exp.role}</p> : null}
                        {exp.major ? <p className="text-sm text-muted-foreground">{exp.major}</p> : null}
                      </div>
                      <div className="flex shrink-0 items-center gap-1">
                        <span className="text-xs text-muted-foreground">{formatDate(exp.created_at)}</span>
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          className="size-7"
                          aria-label={d.contacts.experience.editLabel.replace('{{name}}', exp.organization.name)}
                          onClick={() => setEditTarget(exp)}
                        >
                          <Pencil className="size-3.5" aria-hidden="true" />
                        </Button>
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          className="size-7 text-destructive hover:text-destructive"
                          aria-label={d.contacts.experience.deleteLabel.replace('{{name}}', exp.organization.name)}
                          disabled={deleteExperience.isPending}
                          onClick={() => handleDelete(exp)}
                        >
                          <Trash2 className="size-3.5" aria-hidden="true" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            );
          })}
        </div>
      )}

      <ExperienceFormDialog contactId={contactId} open={addOpen} onOpenChange={setAddOpen} />

      <ExperienceFormDialog
        contactId={contactId}
        experience={editTarget ?? undefined}
        open={editTarget !== null}
        onOpenChange={(open) => {
          if (!open) setEditTarget(null);
        }}
      />
    </>
  );
}
