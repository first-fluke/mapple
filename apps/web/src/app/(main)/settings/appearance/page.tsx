'use client';

import { ThemeToggle } from '@/components/theme-toggle';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function AppearancePage() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Appearance</CardTitle>
        <CardDescription>Customize how Mapple looks on your device.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex items-center justify-between rounded-md border p-4">
          <div>
            <h3 className="font-medium text-sm">Theme</h3>
            <p className="text-sm text-muted-foreground">Choose between light, dark, or system default.</p>
          </div>
          <ThemeToggle />
        </div>
      </CardContent>
    </Card>
  );
}
