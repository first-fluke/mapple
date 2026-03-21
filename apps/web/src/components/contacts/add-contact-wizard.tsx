'use client';

import type { FieldComponent } from '@tanstack/react-form';
import { useForm } from '@tanstack/react-form';
import { ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { useCreateContact } from '@/hooks/use-contacts';
import { organizationsApi } from '@/lib/api/organizations';
import { StepBasicInfo } from './step-basic-info';
import { StepLocation } from './step-location';
import { StepTagsExperience } from './step-tags-experience';

export interface ExperienceFormValue {
  _key: string;
  organizationName: string;
  organizationType: string;
  organizationId: number | null;
  role: string;
  major: string;
}

export interface WizardFormValues {
  name: string;
  email: string;
  phone: string;
  latitude: number | null;
  longitude: number | null;
  country: string;
  city: string;
  tagIds: number[];
  experiences: ExperienceFormValue[];
}

export interface WizardForm {
  // biome-ignore lint/suspicious/noExplicitAny: TanStack Form's Field component has complex generics
  Field: FieldComponent<WizardFormValues, any, any, any, any, any, any, any, any, any, any, any>;
  getFieldValue: <K extends keyof WizardFormValues>(name: K) => WizardFormValues[K];
  // biome-ignore lint/suspicious/noExplicitAny: TanStack Form uses Updater type internally
  setFieldValue: (name: keyof WizardFormValues, value: any) => void;
  handleSubmit: () => void;
  reset: () => void;
}

const STEPS = ['Basic Info', 'Location', 'Tags & Experience'] as const;

export function AddContactWizard({ open, onOpenChange }: { open: boolean; onOpenChange: (open: boolean) => void }) {
  const [step, setStep] = useState(0);
  const createContact = useCreateContact();

  const form = useForm({
    defaultValues: {
      name: '',
      email: '',
      phone: '',
      latitude: null as number | null,
      longitude: null as number | null,
      country: '',
      city: '',
      tagIds: [] as number[],
      experiences: [] as ExperienceFormValue[],
    },
    onSubmit: async ({ value }) => {
      const experiencePayloads = await Promise.all(
        value.experiences
          .filter((exp) => exp.organizationName.trim())
          .map(async (exp) => {
            let orgId = exp.organizationId;
            if (!orgId && exp.organizationName.trim()) {
              const res = await organizationsApi.create(exp.organizationName.trim(), exp.organizationType || 'company');
              orgId = res.data.id;
            }
            return {
              organization_id: orgId as number,
              role: exp.role || null,
              major: exp.major || null,
            };
          }),
      );

      await createContact.mutateAsync({
        name: value.name,
        email: value.email || null,
        phone: value.phone || null,
        latitude: value.latitude,
        longitude: value.longitude,
        country: value.country || null,
        city: value.city || null,
        tag_ids: value.tagIds,
        experiences: experiencePayloads,
      });

      handleClose();
    },
  });

  const wizardForm: WizardForm = {
    Field: form.Field,
    getFieldValue: (name) => form.getFieldValue(name),
    setFieldValue: (name, value) => form.setFieldValue(name, value as never),
    handleSubmit: () => form.handleSubmit(),
    reset: () => form.reset(),
  };

  const handleClose = () => {
    onOpenChange(false);
    setStep(0);
    form.reset();
  };

  const canProceed = () => {
    if (step === 0) {
      return form.getFieldValue('name').trim().length > 0;
    }
    return true;
  };

  const handleNext = () => {
    if (step < STEPS.length - 1) {
      setStep(step + 1);
    } else {
      form.handleSubmit();
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Add Contact</DialogTitle>
          <DialogDescription>
            Step {step + 1} of {STEPS.length}: {STEPS[step]}
          </DialogDescription>
        </DialogHeader>

        <div className="flex gap-1 px-0.5">
          {STEPS.map((label) => (
            <div
              key={label}
              className={`h-1 flex-1 rounded-full transition-colors ${STEPS.indexOf(label) <= step ? 'bg-primary' : 'bg-muted'}`}
            />
          ))}
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleNext();
          }}
        >
          {step === 0 && <StepBasicInfo form={wizardForm} />}
          {step === 1 && <StepLocation form={wizardForm} />}
          {step === 2 && <StepTagsExperience form={wizardForm} />}

          <DialogFooter className="mt-4">
            {step > 0 && (
              <Button type="button" variant="outline" onClick={() => setStep(step - 1)}>
                <ChevronLeft className="mr-1 h-4 w-4" />
                Back
              </Button>
            )}
            <Button type="submit" disabled={!canProceed() || createContact.isPending}>
              {createContact.isPending ? (
                <Loader2 className="mr-1 h-4 w-4 animate-spin" />
              ) : step < STEPS.length - 1 ? (
                <>
                  Next
                  <ChevronRight className="ml-1 h-4 w-4" />
                </>
              ) : (
                'Create Contact'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
