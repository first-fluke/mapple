'use client';

import { Briefcase, GraduationCap } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import type { Experience } from '@/lib/api/contacts';

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString(undefined, {
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

export function ContactTimeline({ experiences }: { experiences: Experience[] }) {
  if (experiences.length === 0) {
    return <p className="text-sm text-muted-foreground">No experiences yet.</p>;
  }

  const sorted = [...experiences].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

  return (
    <div className="relative space-y-0">
      {sorted.map((exp, idx) => {
        const Icon = getOrgIcon(exp.organization.type);
        const isLast = idx === sorted.length - 1;

        return (
          <div key={exp.id} className="flex gap-4">
            <div className="flex flex-col items-center">
              <div className="flex size-8 shrink-0 items-center justify-center rounded-full border bg-background">
                <Icon className="size-4 text-muted-foreground" />
              </div>
              {!isLast ? <Separator orientation="vertical" className="my-1 h-full min-h-6" /> : null}
            </div>

            <Card className="mb-3 flex-1">
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-medium">{exp.organization.name}</p>
                    {exp.role ? <p className="text-sm text-muted-foreground">{exp.role}</p> : null}
                    {exp.major ? <p className="text-sm text-muted-foreground">{exp.major}</p> : null}
                  </div>
                  <span className="shrink-0 text-xs text-muted-foreground">{formatDate(exp.created_at)}</span>
                </div>
              </CardContent>
            </Card>
          </div>
        );
      })}
    </div>
  );
}
