'use client';

import { useAtom } from 'jotai';
import { Contact, Globe, Moon, Network, Settings, Sun } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { useTranslations } from '@/hooks/use-translations';
import type { ThemeMode } from '@/lib/atoms/theme';
import { themeModeAtom } from '@/lib/atoms/theme';
import { cn } from '@/lib/utils';

function SideNavThemeButton() {
  const [themeMode, setThemeMode] = useAtom(themeModeAtom);
  const t = useTranslations();

  function cycleTheme(current: ThemeMode): ThemeMode {
    if (current === 'system') return 'light';
    if (current === 'light') return 'dark';
    return 'system';
  }

  const isDark = themeMode === 'dark';
  const label = isDark ? t.nav.switchToLight : t.nav.switchToDark;

  return (
    <Button
      variant="ghost"
      size="icon"
      aria-label={label}
      onClick={() => setThemeMode(cycleTheme(themeMode))}
      className="mt-auto flex h-12 w-12 items-center justify-center rounded-lg text-sidebar-foreground/60 transition-colors duration-150 hover:bg-sidebar-accent hover:text-sidebar-foreground"
    >
      {isDark ? <Sun className="h-5 w-5" aria-hidden="true" /> : <Moon className="h-5 w-5" aria-hidden="true" />}
    </Button>
  );
}

export function SideNav() {
  const pathname = usePathname();
  const t = useTranslations();

  const navItems = [
    { href: '/', label: t.nav.globe, icon: Globe },
    { href: '/graph', label: t.nav.graph, icon: Network },
    { href: '/contacts', label: t.nav.contacts, icon: Contact },
    { href: '/settings', label: t.nav.settings, icon: Settings },
  ] as const;

  return (
    <nav
      aria-label={t.nav.mainNavLabel}
      className="hidden md:flex h-screen w-16 flex-col items-center border-r bg-sidebar py-4 gap-2"
    >
      {navItems.map((item) => {
        const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              'flex h-12 w-12 items-center justify-center rounded-lg transition-colors',
              isActive
                ? 'bg-sidebar-accent text-sidebar-primary'
                : 'text-sidebar-foreground/60 hover:bg-sidebar-accent hover:text-sidebar-foreground',
            )}
            aria-label={item.label}
            aria-current={isActive ? 'page' : undefined}
          >
            <item.icon className="h-5 w-5" />
          </Link>
        );
      })}
      <SideNavThemeButton />
    </nav>
  );
}
