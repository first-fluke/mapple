import { Network } from 'lucide-react';

export function GraphEmptyState() {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-3 text-muted-foreground">
      <Network className="h-12 w-12 opacity-40" />
      <p className="text-lg font-medium">No connections yet</p>
      <p className="text-sm">Add contacts and their experiences to see your network graph.</p>
    </div>
  );
}
