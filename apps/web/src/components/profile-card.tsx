'use client';

import { MapPin, Network } from 'lucide-react';
import Link from 'next/link';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Drawer, DrawerContent, DrawerDescription, DrawerHeader, DrawerTitle } from '@/components/ui/drawer';
import { Separator } from '@/components/ui/separator';
import type { GlobePin } from '@/lib/api/globe';

interface ProfileCardProps {
  pin: GlobePin | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ProfileCard({ pin, open, onOpenChange }: ProfileCardProps) {
  if (!pin) return null;

  const initials = pin.name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  return (
    <Drawer open={open} onOpenChange={onOpenChange}>
      <DrawerContent>
        <div className="mx-auto w-full max-w-sm">
          <DrawerHeader className="flex flex-col items-center gap-3 pb-2">
            <Avatar className="h-16 w-16">
              {pin.avatar_url && <AvatarImage src={pin.avatar_url} alt={pin.name} />}
              <AvatarFallback className="text-lg">{initials}</AvatarFallback>
            </Avatar>
            <div className="text-center">
              <DrawerTitle>{pin.name}</DrawerTitle>
              <DrawerDescription className="mt-1 flex items-center justify-center gap-1">
                <MapPin className="h-3 w-3" />
                {pin.lat.toFixed(2)}, {pin.lng.toFixed(2)}
              </DrawerDescription>
            </div>
          </DrawerHeader>
          <Separator />
          <div className="flex gap-2 p-4">
            <Button variant="outline" className="flex-1" asChild>
              <Link href={`/contacts/${pin.id}`}>Details</Link>
            </Button>
            <Button variant="outline" className="flex-1" asChild>
              <Link href={`/graph?focus=${pin.id}`}>
                <Network className="mr-1 h-4 w-4" />
                Connections
              </Link>
            </Button>
          </div>
        </div>
      </DrawerContent>
    </Drawer>
  );
}
