'use client';

import { useAtom } from 'jotai';
import { Monitor, Moon, Sun } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useTranslations } from '@/hooks/use-translations';
import type { ThemeMode } from '@/lib/atoms/theme';
import { themeModeAtom } from '@/lib/atoms/theme';

/**
 * Three-way toggle: System / Light / Dark.
 * Accessible, keyboard-navigable, respects prefers-reduced-motion via CSS.
 */
export function ThemeToggle() {
  const [themeMode, setThemeMode] = useAtom(themeModeAtom);
  const d = useTranslations();

  const MODES: { value: ThemeMode; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
    { value: 'system', label: d.settings.appearance.themeSystem, icon: Monitor },
    { value: 'light', label: d.settings.appearance.themeLight, icon: Sun },
    { value: 'dark', label: d.settings.appearance.themeDark, icon: Moon },
  ];

  return (
    <fieldset className="flex items-center gap-1 rounded-lg border border-border p-1">
      <legend className="sr-only">{d.settings.appearance.themeGroupLabel}</legend>
      {MODES.map(({ value, label, icon: Icon }) => (
        <Button
          key={value}
          type="button"
          variant="ghost"
          size="sm"
          aria-label={label}
          aria-pressed={themeMode === value}
          onClick={() => setThemeMode(value)}
          className={
            themeMode === value
              ? 'h-7 w-7 rounded-md bg-accent px-0 text-accent-foreground transition-colors duration-150'
              : 'h-7 w-7 rounded-md px-0 text-muted-foreground transition-colors duration-150 hover:text-foreground'
          }
        >
          <Icon className="h-3.5 w-3.5" aria-hidden="true" />
        </Button>
      ))}
    </fieldset>
  );
}
