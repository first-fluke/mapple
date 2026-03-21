export function GlobeSkeleton() {
  return (
    <div className="flex h-full w-full items-center justify-center bg-background">
      <div className="relative h-[80%] max-h-[600px] w-[80%] max-w-[600px]">
        <div className="h-full w-full animate-pulse rounded-full bg-muted" />
      </div>
    </div>
  );
}
