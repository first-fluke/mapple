<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

# Globe CRM — Web Frontend

Next.js 16 App Router application with React 19.

## Tech Stack

| Layer | Technology |
| --- | --- |
| Framework | Next.js 16 (App Router) |
| UI Components | shadcn/ui (base-nova style) |
| Styling | TailwindCSS v4 |
| Server State | TanStack Query v5 |
| Forms | TanStack Form |
| URL State | nuqs |
| Client State | Jotai |
| Lint/Format | Biome |

## Commands

```bash
npm run dev      # Start dev server
npm run build    # Production build
npm run lint     # Biome check
npm run format   # Biome format
```

## Architecture

```
src/
├── app/           # Next.js App Router pages and layouts
├── components/    # React components
│   └── ui/        # shadcn/ui components
├── hooks/         # Custom React hooks
├── lib/           # Utilities (cn, etc.)
└── providers/     # Client providers (Query, Jotai, nuqs)
```

## Conventions

- **Components**: Use shadcn/ui primitives. Add new components via `npx shadcn@latest add <component>`.
- **Styling**: Use Tailwind utility classes. Use `cn()` from `@/lib/utils` for conditional classes.
- **State**: URL state with nuqs, server state with TanStack Query, client state with Jotai atoms.
- **Forms**: Use TanStack Form for form state management.
- **Imports**: Use `@/*` path alias for absolute imports from `src/`.
- **Lint**: Run `npm run lint` before committing. Single quotes, trailing commas, semicolons.
