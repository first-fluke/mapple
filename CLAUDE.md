# Claude Code Instructions

## Project

Globe CRM — polyglot monorepo (Node.js, Flutter, Terraform).

## Commands

```bash
# Start local services
docker compose up -d

# Lint & format
npx @biomejs/biome check --write .

# Install tool versions
mise install
```

## Code Style

- Use Biome for all JS/TS linting and formatting
- Follow conventional commits: `type(scope): description`
- TypeScript for backend and web, Dart for mobile, HCL for infrastructure
- Prefer named exports over default exports
- Use absolute imports within each package

## Architecture

- `apps/` — deployable applications (api, web, mobile)
- `packages/` — shared libraries (db, config, types)
- `infra/` — Terraform infrastructure code

## Rules

- Do not modify `.agents/` or `.claude/` directories
- Run `npx @biomejs/biome check` before committing JS/TS changes
- Keep docker-compose services pinned to major versions
- All database changes go through migration files in `packages/db`
