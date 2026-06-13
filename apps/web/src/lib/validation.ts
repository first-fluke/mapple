import { z } from 'zod';
import type { Messages } from '@/lib/i18n/locales/ko';
import { ko } from '@/lib/i18n/locales/ko';

// ---------------------------------------------------------------------------
// Constants (locale-independent)
// ---------------------------------------------------------------------------
export const AVATAR_MAX_BYTES = 5 * 1024 * 1024; // 5 MB
export const AVATAR_ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp'] as const;

// ---------------------------------------------------------------------------
// Locale-aware schema factory
// ---------------------------------------------------------------------------

/**
 * Returns zod schemas whose validation messages are pulled from the given
 * message dictionary. Call this inside a Client Component after obtaining
 * the dictionary via `useTranslations()`, or in a Server Component with the
 * server dictionary.
 */
export function createValidation(d: Messages) {
  const phoneSchema = z
    .string()
    .trim()
    .refine((val) => val === '' || /^\+?[\d\s\-().]{6,20}$/.test(val), {
      message: d.validation.phoneInvalid,
    });

  const emailSchema = z
    .string()
    .trim()
    .refine((val) => val === '' || z.email().safeParse(val).success, {
      message: d.validation.emailInvalid,
    });

  const contactBasicSchema = z.object({
    name: z.string().min(1, d.contacts.basicInfo.validationNameRequired),
    email: emailSchema,
    phone: phoneSchema,
  });

  const meetingSchema = z.object({
    title: z.string().min(1, d.contacts.meeting.validationTitleRequired),
    starts_at: z.string().min(1, d.contacts.meeting.validationStartsAtRequired),
    ends_at: z.string().min(1, d.contacts.meeting.validationEndsAtRequired),
    location: z.string().optional(),
    notes: z.string().optional(),
  });

  const experienceSchema = z.object({
    organizationName: z.string().min(1, d.contacts.experience.validationOrgRequired),
    role: z.string().optional(),
    major: z.string().optional(),
  });

  function validateAvatarFile(file: File): string | null {
    if (!AVATAR_ACCEPTED_TYPES.includes(file.type as (typeof AVATAR_ACCEPTED_TYPES)[number])) {
      return d.validation.avatarType;
    }
    if (file.size > AVATAR_MAX_BYTES) {
      return d.validation.avatarSize;
    }
    return null;
  }

  return {
    phoneSchema,
    emailSchema,
    contactBasicSchema,
    meetingSchema,
    experienceSchema,
    validateAvatarFile,
  };
}

// ---------------------------------------------------------------------------
// Backward-compatible static exports (use ko catalog as default)
// These are kept so that existing imports and tests continue to compile.
// Prefer createValidation(d) in components where a locale-aware dictionary
// is available.
// ---------------------------------------------------------------------------
const _defaultValidation = createValidation(ko);

export const phoneSchema = _defaultValidation.phoneSchema;
export const emailSchema = _defaultValidation.emailSchema;
export const contactBasicSchema = _defaultValidation.contactBasicSchema;
export const meetingSchema = _defaultValidation.meetingSchema;
export const experienceSchema = _defaultValidation.experienceSchema;
export const validateAvatarFile = _defaultValidation.validateAvatarFile;

export type ContactBasicValues = z.infer<typeof contactBasicSchema>;
export type MeetingValues = z.infer<typeof meetingSchema>;
export type ExperienceValues = z.infer<typeof experienceSchema>;
