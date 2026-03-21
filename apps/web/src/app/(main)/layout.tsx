import { AppNav } from '@/components/app-nav';
import { SkipLink } from '@/components/skip-link';

export default function MainLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="flex h-screen flex-col md:flex-row">
      <SkipLink />
      <AppNav />
      <main id="main-content" className="flex-1 overflow-y-auto p-4 pb-20 md:pb-4" tabIndex={-1}>
        {children}
      </main>
    </div>
  );
}
