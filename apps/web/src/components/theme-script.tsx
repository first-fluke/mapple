/**
 * Inlined <script> that runs before hydration to set .dark on <html>,
 * preventing flash of wrong theme (FOWT).
 *
 * Reads globe-crm:theme from localStorage:
 *   - 'dark'   → add .dark
 *   - 'light'  → no-op
 *   - 'system' or missing → match prefers-color-scheme
 */
export function ThemeScript() {
  const script = `
(function(){
  try {
    var t = localStorage.getItem('globe-crm:theme');
    var v = t ? JSON.parse(t) : 'system';
    if (v === 'dark' || (v === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.classList.add('dark');
    }
  } catch(e) {}
})();
`.trim();

  // biome-ignore lint/security/noDangerouslySetInnerHtml: required for no-flash theme script
  return <script dangerouslySetInnerHTML={{ __html: script }} />;
}
