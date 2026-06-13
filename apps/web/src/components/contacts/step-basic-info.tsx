'use client';

import { useMemo } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useTranslations } from '@/hooks/use-translations';
import { createValidation } from '@/lib/validation';
import type { WizardForm } from './add-contact-wizard';

export function StepBasicInfo({ form }: { form: WizardForm }) {
  const d = useTranslations();
  const { emailSchema, phoneSchema } = useMemo(() => createValidation(d), [d]);

  return (
    <div className="flex flex-col gap-4">
      <form.Field
        name="name"
        validators={{
          onChange: ({ value }: { value: string }) =>
            !value.trim() ? d.contacts.basicInfo.validationNameRequired : undefined,
        }}
      >
        {(field) => (
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="wizard-name">
              {d.contacts.basicInfo.nameLabel} <span aria-hidden="true">*</span>
            </Label>
            <Input
              id="wizard-name"
              placeholder={d.contacts.basicInfo.namePlaceholder}
              value={field.state.value}
              onChange={(e) => field.handleChange(e.target.value)}
              onBlur={field.handleBlur}
              aria-required="true"
              aria-invalid={field.state.meta.errors.length > 0}
              aria-describedby={field.state.meta.errors.length > 0 ? 'wizard-name-error' : undefined}
            />
            {field.state.meta.errors.length > 0 && (
              <p id="wizard-name-error" className="text-xs text-destructive" role="alert">
                {field.state.meta.errors[0]}
              </p>
            )}
          </div>
        )}
      </form.Field>

      <form.Field
        name="email"
        validators={{
          onBlur: ({ value }: { value: string }) => {
            const result = emailSchema.safeParse(value);
            return result.success ? undefined : result.error.issues[0]?.message;
          },
        }}
      >
        {(field) => (
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="wizard-email">{d.contacts.basicInfo.emailLabel}</Label>
            <Input
              id="wizard-email"
              type="email"
              placeholder="example@email.com"
              value={field.state.value}
              onChange={(e) => field.handleChange(e.target.value)}
              onBlur={field.handleBlur}
              aria-invalid={field.state.meta.errors.length > 0}
              aria-describedby={field.state.meta.errors.length > 0 ? 'wizard-email-error' : undefined}
            />
            {field.state.meta.errors.length > 0 && (
              <p id="wizard-email-error" className="text-xs text-destructive" role="alert">
                {field.state.meta.errors[0]}
              </p>
            )}
          </div>
        )}
      </form.Field>

      <form.Field
        name="phone"
        validators={{
          onBlur: ({ value }: { value: string }) => {
            const result = phoneSchema.safeParse(value);
            return result.success ? undefined : result.error.issues[0]?.message;
          },
        }}
      >
        {(field) => (
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="wizard-phone">{d.contacts.basicInfo.phoneLabel}</Label>
            <Input
              id="wizard-phone"
              type="tel"
              placeholder={d.contacts.basicInfo.phonePlaceholder}
              value={field.state.value}
              onChange={(e) => field.handleChange(e.target.value)}
              onBlur={field.handleBlur}
              aria-invalid={field.state.meta.errors.length > 0}
              aria-describedby={field.state.meta.errors.length > 0 ? 'wizard-phone-error' : undefined}
            />
            {field.state.meta.errors.length > 0 && (
              <p id="wizard-phone-error" className="text-xs text-destructive" role="alert">
                {field.state.meta.errors[0]}
              </p>
            )}
          </div>
        )}
      </form.Field>
    </div>
  );
}
