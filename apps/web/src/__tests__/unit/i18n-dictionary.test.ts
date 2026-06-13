import { describe, expect, it } from 'vitest';
import { getDefaultDictionary, getDictionary } from '@/lib/i18n/loader';
import { en } from '@/lib/i18n/locales/en';
import type { Messages } from '@/lib/i18n/locales/ko';
import { ko } from '@/lib/i18n/locales/ko';

// ---------------------------------------------------------------------------
// Catalog shape — ko (source of truth)
// ---------------------------------------------------------------------------
describe('ko catalog', () => {
  it('has all top-level namespaces', () => {
    const namespaces: (keyof Messages)[] = [
      'nav',
      'settings',
      'contacts',
      'globe',
      'graph',
      'auth',
      'toasts',
      'validation',
    ];
    for (const ns of namespaces) {
      expect(ko).toHaveProperty(ns);
    }
  });

  it('nav has all required keys', () => {
    expect(ko.nav.globe).toBeTruthy();
    expect(ko.nav.contacts).toBeTruthy();
    expect(ko.nav.settings).toBeTruthy();
    expect(ko.nav.switchToDark).toBeTruthy();
    expect(ko.nav.switchToLight).toBeTruthy();
  });

  it('contacts emptyNoFilter and emptyFiltered have title and description', () => {
    expect(ko.contacts.emptyNoFilter.title).toBeTruthy();
    expect(ko.contacts.emptyNoFilter.description).toBeTruthy();
    expect(ko.contacts.emptyFiltered.title).toBeTruthy();
    expect(ko.contacts.emptyFiltered.description).toBeTruthy();
  });

  it('globe has onboarding block', () => {
    expect(ko.globe.onboarding.title).toBeTruthy();
    expect(ko.globe.onboarding.description).toBeTruthy();
    expect(ko.globe.onboarding.getStarted).toBeTruthy();
  });

  it('settings.appearance has theme mode labels', () => {
    expect(ko.settings.appearance.themeSystem).toBeTruthy();
    expect(ko.settings.appearance.themeLight).toBeTruthy();
    expect(ko.settings.appearance.themeDark).toBeTruthy();
  });

  it('validation namespace has all required keys', () => {
    expect(ko.validation.emailInvalid).toBeTruthy();
    expect(ko.validation.phoneInvalid).toBeTruthy();
    expect(ko.validation.avatarType).toBeTruthy();
    expect(ko.validation.avatarSize).toBeTruthy();
  });
});

// ---------------------------------------------------------------------------
// Catalog shape — en (translated)
// ---------------------------------------------------------------------------
describe('en catalog', () => {
  it('satisfies the Messages interface (TypeScript enforces this at compile time)', () => {
    // If en compiles, the interface is satisfied. This test guards runtime shape.
    const keys: (keyof Messages)[] = ['nav', 'settings', 'contacts', 'globe', 'graph', 'auth', 'toasts', 'validation'];
    for (const key of keys) {
      expect(en).toHaveProperty(key);
    }
  });

  it('has distinct values from ko for user-visible strings', () => {
    // English strings must be different from Korean strings
    expect(en.contacts.title).not.toBe(ko.contacts.title);
    expect(en.nav.contacts).not.toBe(ko.nav.contacts);
    expect(en.globe.emptyTitle).not.toBe(ko.globe.emptyTitle);
  });

  it('nav globe and graph labels are identical in both locales (they are proper nouns)', () => {
    expect(en.nav.globe).toBe(ko.nav.globe);
    expect(en.nav.graph).toBe(ko.nav.graph);
  });

  it('validation messages are distinct from ko', () => {
    expect(en.validation.emailInvalid).not.toBe(ko.validation.emailInvalid);
    expect(en.validation.phoneInvalid).not.toBe(ko.validation.phoneInvalid);
    expect(en.validation.avatarType).not.toBe(ko.validation.avatarType);
    expect(en.validation.avatarSize).not.toBe(ko.validation.avatarSize);
  });

  it('validation namespace has all required keys', () => {
    expect(en.validation.emailInvalid).toBeTruthy();
    expect(en.validation.phoneInvalid).toBeTruthy();
    expect(en.validation.avatarType).toBeTruthy();
    expect(en.validation.avatarSize).toBeTruthy();
  });
});

// ---------------------------------------------------------------------------
// getDictionary loader
// ---------------------------------------------------------------------------
describe('getDictionary', () => {
  it('returns ko catalog for "ko"', () => {
    expect(getDictionary('ko')).toBe(ko);
  });

  it('returns en catalog for "en"', () => {
    expect(getDictionary('en')).toBe(en);
  });

  it('falls back to ko for unknown locale', () => {
    expect(getDictionary('fr')).toBe(ko);
    expect(getDictionary('')).toBe(ko);
  });

  it('getDefaultDictionary returns ko', () => {
    expect(getDefaultDictionary()).toBe(ko);
  });
});
