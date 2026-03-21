export function SkipLink() {
  return (
    <a
      href="#main-content"
      className="fixed left-2 top-2 z-[100] -translate-y-full rounded-lg bg-primary px-4 py-3 text-sm font-medium text-primary-foreground transition-transform focus:translate-y-0 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
    >
      Skip to main content
    </a>
  );
}
