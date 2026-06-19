import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import { AxeDev } from '@/components/axe-dev';
import { ThemeScript } from '@/components/theme-script';
import { Providers } from '@/providers';
import './globals.css';

const geistSans = Geist({
  subsets: ['latin'],
  variable: '--font-geist-sans',
});

const geistMono = Geist_Mono({
  subsets: ['latin'],
  variable: '--font-geist-mono',
});

export const metadata: Metadata = {
  title: 'Mapple',
  description: 'Customer relationship management with geospatial capabilities',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`} suppressHydrationWarning>
      <head>
        <ThemeScript />
      </head>
      <body className="font-sans antialiased">
        <Providers>
          {process.env.NODE_ENV === 'development' && <AxeDev />}
          {children}
        </Providers>
      </body>
    </html>
  );
}
