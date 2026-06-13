'use client';

import { useForm } from '@tanstack/react-form';
import { Loader2 } from 'lucide-react';
import { useMemo, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useCreateExperience, useUpdateExperience } from '@/hooks/use-contact';
import { useOrganizationSearch } from '@/hooks/use-organizations';
import { useToast } from '@/hooks/use-toast';
import { useTranslations } from '@/hooks/use-translations';
import type { Experience } from '@/lib/api/contacts';
import { organizationsApi } from '@/lib/api/organizations';
import { createValidation } from '@/lib/validation';

interface ExperienceFormDialogProps {
  contactId: number;
  experience?: Experience;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ExperienceFormDialog({ contactId, experience, open, onOpenChange }: ExperienceFormDialogProps) {
  const isEdit = Boolean(experience);
  const createExperience = useCreateExperience(contactId);
  const updateExperience = useUpdateExperience(contactId);
  const { success, error } = useToast();
  const d = useTranslations();
  const { experienceSchema } = useMemo(() => createValidation(d), [d]);

  const [orgQuery, setOrgQuery] = useState('');
  const [selectedOrgId, setSelectedOrgId] = useState<number | null>(experience?.organization_id ?? null);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const { data: orgResults } = useOrganizationSearch(orgQuery);

  const form = useForm({
    defaultValues: {
      organizationName: experience?.organization?.name ?? '',
      role: experience?.role ?? '',
      major: experience?.major ?? '',
    },
    validators: {
      onSubmit: ({ value }) => {
        const result = experienceSchema.safeParse(value);
        if (!result.success) {
          return result.error.issues[0]?.message ?? d.contacts.experience.validationInputCheck;
        }
        return undefined;
      },
    },
    onSubmit: async ({ value }) => {
      try {
        if (isEdit && experience) {
          await updateExperience.mutateAsync({
            expId: experience.id,
            data: {
              role: value.role || null,
              major: value.major || null,
            },
          });
          success(d.contacts.experience.toastEdited);
        } else {
          let orgId = selectedOrgId;
          if (!orgId && value.organizationName.trim()) {
            const res = await organizationsApi.create(value.organizationName.trim(), 'company');
            orgId = res.data.id;
          }
          if (!orgId) {
            error(d.contacts.experience.validationInputCheck);
            return;
          }
          await createExperience.mutateAsync({
            organization_id: orgId,
            role: value.role || null,
            major: value.major || null,
          });
          success(d.contacts.experience.toastAdded);
        }
        onOpenChange(false);
        form.reset();
        setSelectedOrgId(null);
        setOrgQuery('');
      } catch {
        error(isEdit ? d.contacts.experience.toastEditFailed : d.contacts.experience.toastAddFailed);
      }
    },
  });

  const isPending = createExperience.isPending || updateExperience.isPending;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{isEdit ? d.contacts.experience.editTitle : d.contacts.experience.addTitle}</DialogTitle>
        </DialogHeader>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            form.handleSubmit();
          }}
          className="flex flex-col gap-4"
          noValidate
        >
          {/* Organization name — editable only on create */}
          <form.Field
            name="organizationName"
            validators={{
              onChange: ({ value }) =>
                !isEdit && !value.trim() ? d.contacts.experience.validationOrgRequired : undefined,
            }}
          >
            {(field) => (
              <div className="relative flex flex-col gap-1.5">
                <Label htmlFor="exp-org-name">
                  {d.contacts.experience.orgNameLabel} {!isEdit && <span aria-hidden="true">*</span>}
                </Label>
                <Input
                  id="exp-org-name"
                  placeholder={d.contacts.experience.orgNamePlaceholder}
                  value={field.state.value}
                  disabled={isEdit}
                  onChange={(e) => {
                    const val = e.target.value;
                    field.handleChange(val);
                    setOrgQuery(val);
                    setSelectedOrgId(null);
                    setShowSuggestions(true);
                  }}
                  onFocus={() => setShowSuggestions(true)}
                  onBlur={() => {
                    field.handleBlur();
                    setTimeout(() => setShowSuggestions(false), 150);
                  }}
                  aria-required={!isEdit}
                  aria-invalid={field.state.meta.errors.length > 0}
                  aria-describedby={field.state.meta.errors.length > 0 ? 'exp-org-name-error' : undefined}
                  aria-autocomplete="list"
                  aria-controls={showSuggestions ? 'exp-org-suggestions' : undefined}
                />
                {showSuggestions && orgResults && orgResults.length > 0 && (
                  <ul
                    id="exp-org-suggestions"
                    aria-label={d.contacts.experience.orgSuggestionsLabel}
                    className="absolute top-full z-10 mt-1 w-full rounded-md border bg-popover p-1 shadow-md"
                  >
                    {orgResults.map((org) => (
                      <li key={org.id}>
                        <button
                          type="button"
                          aria-pressed={selectedOrgId === org.id}
                          className="flex w-full items-center rounded-sm px-2 py-1.5 text-sm hover:bg-accent focus-visible:bg-accent focus-visible:outline-none"
                          onMouseDown={(e) => {
                            e.preventDefault();
                            field.handleChange(org.name);
                            setSelectedOrgId(org.id);
                            setShowSuggestions(false);
                            setOrgQuery('');
                          }}
                        >
                          <span>{org.name}</span>
                          <span className="ml-auto text-xs text-muted-foreground">{org.type}</span>
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
                {field.state.meta.errors.length > 0 && (
                  <p id="exp-org-name-error" className="text-xs text-destructive" role="alert">
                    {field.state.meta.errors[0]}
                  </p>
                )}
              </div>
            )}
          </form.Field>

          <div className="grid grid-cols-2 gap-3">
            <form.Field name="role">
              {(field) => (
                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="exp-role">{d.contacts.experience.roleLabel}</Label>
                  <Input
                    id="exp-role"
                    placeholder={d.contacts.experience.rolePlaceholder}
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                  />
                </div>
              )}
            </form.Field>

            <form.Field name="major">
              {(field) => (
                <div className="flex flex-col gap-1.5">
                  <Label htmlFor="exp-major">{d.contacts.experience.majorLabel}</Label>
                  <Input
                    id="exp-major"
                    placeholder={d.contacts.experience.majorPlaceholder}
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                  />
                </div>
              )}
            </form.Field>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              {d.contacts.experience.cancelButton}
            </Button>
            <Button type="submit" disabled={isPending}>
              {isPending && <Loader2 className="mr-1 size-4 animate-spin" aria-hidden="true" />}
              {isEdit ? d.contacts.experience.editButton : d.contacts.experience.addButton}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
