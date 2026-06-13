'use client';

import { Contact, Globe, Network, Settings } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTranslations } from '@/hooks/use-translations';
import { cn } from '@/lib/utils';

export function BottomNav() {
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
      className="fixed bottom-0 left-0 right-0 z-50 flex md:hidden h-16 items-center justify-around border-t bg-background"
    >
      {navItems.map((item) => {
        const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              'flex min-h-12 min-w-12 flex-col items-center justify-center gap-1 px-3 py-2 transition-colors',
              isActive ? 'text-primary' : 'text-muted-foreground hover:text-foreground',
            )}
            aria-label={item.label}
            aria-current={isActive ? 'page' : undefined}
          >
            <item.icon className="h-5 w-5" />
            <span className="text-xs">{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
