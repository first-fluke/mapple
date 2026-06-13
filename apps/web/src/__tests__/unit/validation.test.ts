import { describe, expect, it } from 'vitest';
import { en } from '@/lib/i18n/locales/en';
import { ko } from '@/lib/i18n/locales/ko';
import {
  AVATAR_ACCEPTED_TYPES,
  AVATAR_MAX_BYTES,
  contactBasicSchema,
  createValidation,
  emailSchema,
  experienceSchema,
  meetingSchema,
  phoneSchema,
  validateAvatarFile,
} from '@/lib/validation';

// ---------------------------------------------------------------------------
// emailSchema (backward-compat static export — uses ko catalog)
// ---------------------------------------------------------------------------
describe('emailSchema', () => {
  it('accepts a valid email', () => {
    expect(emailSchema.safeParse('user@example.com').success).toBe(true);
  });

  it('accepts empty string (optional field)', () => {
    expect(emailSchema.safeParse('').success).toBe(true);
  });

  it('accepts email with subdomain', () => {
    expect(emailSchema.safeParse('admin@mail.co.kr').success).toBe(true);
  });

  it('rejects an address without @', () => {
    const result = emailSchema.safeParse('notanemail');
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0]?.message).toBe(ko.validation.emailInvalid);
    }
  });

  it('rejects an address without domain', () => {
    expect(emailSchema.safeParse('user@').success).toBe(false);
  });

  it('rejects an address with spaces', () => {
    expect(emailSchema.safeParse('user @example.com').success).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// phoneSchema (backward-compat static export — uses ko catalog)
// ---------------------------------------------------------------------------
describe('phoneSchema', () => {
  it('accepts a standard E.164 number', () => {
    expect(phoneSchema.safeParse('+82 10-1234-5678').success).toBe(true);
  });

  it('accepts digits only', () => {
    expect(phoneSchema.safeParse('0101234567').success).toBe(true);
  });

  it('accepts number with parens', () => {
    expect(phoneSchema.safeParse('+1 (555) 123-4567').success).toBe(true);
  });

  it('accepts empty string (optional field)', () => {
    expect(phoneSchema.safeParse('').success).toBe(true);
  });

  it('rejects a number that is too short (< 6 chars)', () => {
    const result = phoneSchema.safeParse('12345');
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0]?.message).toBe(ko.validation.phoneInvalid);
    }
  });

  it('rejects a number that is too long (> 20 chars)', () => {
    expect(phoneSchema.safeParse('+1234567890123456789012').success).toBe(false);
  });

  it('rejects a number with invalid characters', () => {
    expect(phoneSchema.safeParse('abc-def-ghij').success).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// contactBasicSchema (backward-compat static export — uses ko catalog)
// ---------------------------------------------------------------------------
describe('contactBasicSchema', () => {
  it('accepts a complete valid contact', () => {
    const result = contactBasicSchema.safeParse({
      name: 'Hong Gildong',
      email: 'hong@example.com',
      phone: '+82 10-1234-5678',
    });
    expect(result.success).toBe(true);
  });

  it('accepts contact with empty email and phone', () => {
    const result = contactBasicSchema.safeParse({
      name: 'Hong Gildong',
      email: '',
      phone: '',
    });
    expect(result.success).toBe(true);
  });

  it('rejects empty name', () => {
    const result = contactBasicSchema.safeParse({ name: '', email: '', phone: '' });
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0]?.message).toBe(ko.contacts.basicInfo.validationNameRequired);
    }
  });

  it('rejects invalid email within composite schema', () => {
    const result = contactBasicSchema.safeParse({
      name: 'Hong Gildong',
      email: 'bad-email',
      phone: '',
    });
    expect(result.success).toBe(false);
  });

  it('rejects invalid phone within composite schema', () => {
    const result = contactBasicSchema.safeParse({
      name: 'Hong Gildong',
      email: '',
      phone: '999',
    });
    expect(result.success).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// meetingSchema (backward-compat static export — uses ko catalog)
// ---------------------------------------------------------------------------
describe('meetingSchema', () => {
  it('accepts a valid meeting', () => {
    const result = meetingSchema.safeParse({
      title: 'Weekly meeting',
      starts_at: '2026-01-01T09:00',
      ends_at: '2026-01-01T10:00',
    });
    expect(result.success).toBe(true);
  });

  it('accepts optional location and notes', () => {
    const result = meetingSchema.safeParse({
      title: 'Meeting',
      starts_at: '2026-01-01T09:00',
      ends_at: '2026-01-01T10:00',
      location: 'Seoul Gangnam',
      notes: 'Key discussion points',
    });
    expect(result.success).toBe(true);
  });

  it('rejects missing title', () => {
    const result = meetingSchema.safeParse({
      title: '',
      starts_at: '2026-01-01T09:00',
      ends_at: '2026-01-01T10:00',
    });
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0]?.message).toBe(ko.contacts.meeting.validationTitleRequired);
    }
  });

  it('rejects missing starts_at', () => {
    const result = meetingSchema.safeParse({
      title: 'Meeting',
      starts_at: '',
      ends_at: '2026-01-01T10:00',
    });
    expect(result.success).toBe(false);
  });

  it('rejects missing ends_at', () => {
    const result = meetingSchema.safeParse({
      title: 'Meeting',
      starts_at: '2026-01-01T09:00',
      ends_at: '',
    });
    expect(result.success).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// experienceSchema (backward-compat static export — uses ko catalog)
// ---------------------------------------------------------------------------
describe('experienceSchema', () => {
  it('accepts a valid experience', () => {
    const result = experienceSchema.safeParse({
      organizationName: 'Acme Inc.',
      role: 'Software Engineer',
      major: '',
    });
    expect(result.success).toBe(true);
  });

  it('rejects empty organizationName', () => {
    const result = experienceSchema.safeParse({ organizationName: '' });
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0]?.message).toBe(ko.contacts.experience.validationOrgRequired);
    }
  });

  it('accepts without optional role and major', () => {
    const result = experienceSchema.safeParse({ organizationName: 'Seoul National University' });
    expect(result.success).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// validateAvatarFile (backward-compat static export — uses ko catalog)
// ---------------------------------------------------------------------------
describe('validateAvatarFile', () => {
  const makeFile = (name: string, type: string, size: number): File => {
    const blob = new Blob([new Uint8Array(size)], { type });
    return new File([blob], name, { type });
  };

  it('returns null for valid jpeg under 5MB', () => {
    const file = makeFile('photo.jpg', 'image/jpeg', 1024);
    expect(validateAvatarFile(file)).toBeNull();
  });

  it('returns null for valid png under 5MB', () => {
    const file = makeFile('photo.png', 'image/png', 1024);
    expect(validateAvatarFile(file)).toBeNull();
  });

  it('returns null for valid webp under 5MB', () => {
    const file = makeFile('photo.webp', 'image/webp', 1024);
    expect(validateAvatarFile(file)).toBeNull();
  });

  it('rejects file exceeding 5MB', () => {
    const file = makeFile('big.jpg', 'image/jpeg', AVATAR_MAX_BYTES + 1);
    expect(validateAvatarFile(file)).toBe(ko.validation.avatarSize);
  });

  it('accepts file exactly at 5MB limit', () => {
    const file = makeFile('exact.jpg', 'image/jpeg', AVATAR_MAX_BYTES);
    expect(validateAvatarFile(file)).toBeNull();
  });

  it('rejects unsupported file type', () => {
    const file = makeFile('photo.gif', 'image/gif', 1024);
    expect(validateAvatarFile(file)).toBe(ko.validation.avatarType);
  });

  it('rejects pdf', () => {
    const file = makeFile('doc.pdf', 'application/pdf', 1024);
    expect(validateAvatarFile(file)).toBe(ko.validation.avatarType);
  });

  it('AVATAR_ACCEPTED_TYPES contains jpeg, png, webp', () => {
    expect(AVATAR_ACCEPTED_TYPES).toContain('image/jpeg');
    expect(AVATAR_ACCEPTED_TYPES).toContain('image/png');
    expect(AVATAR_ACCEPTED_TYPES).toContain('image/webp');
    expect(AVATAR_ACCEPTED_TYPES.length).toBe(3);
  });
});

// ---------------------------------------------------------------------------
// createValidation factory — locale-aware messages
// ---------------------------------------------------------------------------
describe('createValidation factory', () => {
  const makeFile = (name: string, type: string, size: number): File => {
    const blob = new Blob([new Uint8Array(size)], { type });
    return new File([blob], name, { type });
  };

  describe('with ko catalog', () => {
    const v = createValidation(ko);

    it('emailSchema returns ko message on invalid input', () => {
      const result = v.emailSchema.safeParse('notanemail');
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0]?.message).toBe(ko.validation.emailInvalid);
      }
    });

    it('phoneSchema returns ko message on invalid input', () => {
      const result = v.phoneSchema.safeParse('123');
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0]?.message).toBe(ko.validation.phoneInvalid);
      }
    });

    it('validateAvatarFile returns ko type message for gif', () => {
      const file = makeFile('photo.gif', 'image/gif', 1024);
      expect(v.validateAvatarFile(file)).toBe(ko.validation.avatarType);
    });

    it('validateAvatarFile returns ko size message for oversized file', () => {
      const file = makeFile('big.jpg', 'image/jpeg', AVATAR_MAX_BYTES + 1);
      expect(v.validateAvatarFile(file)).toBe(ko.validation.avatarSize);
    });
  });

  describe('with en catalog', () => {
    const v = createValidation(en);

    it('emailSchema returns en message on invalid input', () => {
      const result = v.emailSchema.safeParse('notanemail');
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0]?.message).toBe(en.validation.emailInvalid);
      }
    });

    it('phoneSchema returns en message on invalid input', () => {
      const result = v.phoneSchema.safeParse('123');
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0]?.message).toBe(en.validation.phoneInvalid);
      }
    });

    it('validateAvatarFile returns en type message for gif', () => {
      const file = makeFile('photo.gif', 'image/gif', 1024);
      expect(v.validateAvatarFile(file)).toBe(en.validation.avatarType);
    });

    it('validateAvatarFile returns en size message for oversized file', () => {
      const file = makeFile('big.jpg', 'image/jpeg', AVATAR_MAX_BYTES + 1);
      expect(v.validateAvatarFile(file)).toBe(en.validation.avatarSize);
    });

    it('en messages are distinct from ko messages', () => {
      expect(en.validation.emailInvalid).not.toBe(ko.validation.emailInvalid);
      expect(en.validation.phoneInvalid).not.toBe(ko.validation.phoneInvalid);
      expect(en.validation.avatarType).not.toBe(ko.validation.avatarType);
      expect(en.validation.avatarSize).not.toBe(ko.validation.avatarSize);
    });

    it('contactBasicSchema rejects empty name with en message', () => {
      const result = v.contactBasicSchema.safeParse({ name: '', email: '', phone: '' });
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0]?.message).toBe(en.contacts.basicInfo.validationNameRequired);
      }
    });

    it('meetingSchema rejects empty title with en message', () => {
      const result = v.meetingSchema.safeParse({
        title: '',
        starts_at: '2026-01-01T09:00',
        ends_at: '2026-01-01T10:00',
      });
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0]?.message).toBe(en.contacts.meeting.validationTitleRequired);
      }
    });

    it('experienceSchema rejects empty org with en message', () => {
      const result = v.experienceSchema.safeParse({ organizationName: '' });
      expect(result.success).toBe(false);
      if (!result.success) {
        expect(result.error.issues[0]?.message).toBe(en.contacts.experience.validationOrgRequired);
      }
    });
  });
});
