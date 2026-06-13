import { createStore } from 'jotai';
import { describe, expect, it } from 'vitest';
import type { ThemeMode } from '@/lib/atoms/theme';
import { themeModeAtom } from '@/lib/atoms/theme';

describe('themeModeAtom', () => {
  it('defaults to "system"', () => {
    const store = createStore();
    expect(store.get(themeModeAtom)).toBe('system');
  });

  it('can be set to "light"', () => {
    const store = createStore();
    store.set(themeModeAtom, 'light');
    expect(store.get(themeModeAtom)).toBe('light');
  });

  it('can be set to "dark"', () => {
    const store = createStore();
    store.set(themeModeAtom, 'dark');
    expect(store.get(themeModeAtom)).toBe('dark');
  });

  it('can be cycled through all modes', () => {
    const store = createStore();
    const modes: ThemeMode[] = ['system', 'light', 'dark'];
    for (const mode of modes) {
      store.set(themeModeAtom, mode);
      expect(store.get(themeModeAtom)).toBe(mode);
    }
  });

  it('accepts only valid ThemeMode values', () => {
    const store = createStore();
    store.set(themeModeAtom, 'dark');
    expect(['system', 'light', 'dark']).toContain(store.get(themeModeAtom));
  });
});
