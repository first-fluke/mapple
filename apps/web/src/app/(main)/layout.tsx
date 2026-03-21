import { AppNav } from '@/components/app-nav';

export default function MainLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="flex h-screen flex-col md:flex-row">
      <AppNav />
      <main className="flex-1 overflow-y-auto p-4 pb-20 md:pb-4">{children}</main>
    </div>
  );
}
