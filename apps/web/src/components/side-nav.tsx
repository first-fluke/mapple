'use client';

import { Contact, Globe, Network, Settings } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/', label: 'Globe', icon: Globe },
  { href: '/graph', label: 'Graph', icon: Network },
  { href: '/contacts', label: 'Contacts', icon: Contact },
  { href: '/settings', label: 'Settings', icon: Settings },
] as const;

export function SideNav() {
  const pathname = usePathname();

  return (
    <nav className="hidden md:flex h-screen w-16 flex-col items-center border-r bg-sidebar py-4 gap-2">
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
    </nav>
  );
}
