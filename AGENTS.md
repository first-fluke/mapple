# Globe CRM

Globe CRM is a polyglot monorepo for customer relationship management with geospatial capabilities.

## Architecture

```
globe-crm/
├── apps/              # Deployable applications
│   ├── api/           # Backend API (Node.js)
│   ├── web/           # Web frontend (React)
│   └── mobile/        # Mobile app (Flutter)
├── packages/          # Shared libraries
│   └── types/         # Shared type definitions
├── infra/             # Infrastructure as Code (Terraform)
├── docker-compose.yml # Local development services
├── .mise.toml         # Tool version management
└── biome.json         # Lint & format configuration
```

## Tech Stack

| Layer          | Technology                    |
| -------------- | ----------------------------- |
| Backend API    | Node.js 22                    |
| Web Frontend   | React                         |
| Mobile         | Flutter 3                     |
| Database       | PostgreSQL 16 + PostGIS       |
| Cache          | Redis 7                       |
| Object Storage | MinIO (S3-compatible)         |
| IaC            | Terraform 1.x                 |
| Lint/Format    | Biome                         |
| Tooling        | mise                          |

## Getting Started

### Prerequisites

- [mise](https://mise.jdx.dev/) installed
- [Docker](https://www.docker.com/) and Docker Compose

### Setup

```bash
# Install tool versions
mise install

# Start infrastructure services
docker compose up -d

# Verify services
docker compose ps
```

### Service Endpoints

| Service    | URL                    |
| ---------- | ---------------------- |
| PostgreSQL | localhost:5432         |
| Redis      | localhost:6379         |
| MinIO API  | http://localhost:9000  |
| MinIO Console | http://localhost:9001 |

## Environment Variables

### Web (`apps/web`)

| Variable | Description | Required |
| --- | --- | --- |
| `API_URL` | Backend API URL for proxy rewrites | Yes |
| `BETTER_AUTH_SECRET` | Secret key for better-auth session signing (min 32 chars) | Yes |
| `BETTER_AUTH_URL` | Base URL of the web app for better-auth | Yes |

## Conventions

- **Commits**: Conventional Commits format — `type(scope): description`
- **Branching**: Feature branches off `main`
- **Lint/Format**: Biome (run `npx @biomejs/biome check .`)
- **Language**: TypeScript for backend/web, Dart for mobile, HCL for infra

<!-- OMA:START — managed by oh-my-agent. Do not edit this block manually. -->

# oh-my-agent

## Architecture

- **SSOT**: `.agents/` directory (do not modify directly)
- **Response language**: Follows `language` in `.agents/oma-config.yaml`
- **Skills**: `.agents/skills/` (domain specialists)
- **Workflows**: `.agents/workflows/` (multi-step orchestration)
- **Subagents**: Same-vendor native dispatch via Codex custom agents in `.codex/agents/{name}.toml`; cross-vendor fallback via `oma agent:spawn`

## Per-Agent Dispatch

1. Resolve `target_vendor_for_agent` from `.agents/oma-config.yaml`.
2. If `target_vendor_for_agent === current_runtime_vendor`, use the runtime's native subagent path.
3. If vendors differ, or native subagents are unavailable, use `oma agent:spawn` for that agent only.

## Workflows

Execute by naming the workflow in your prompt. Keywords are auto-detected via hooks.

| Workflow | File | Description |
|----------|------|-------------|
| orchestrate | `orchestrate.md` | Parallel subagents + Review Loop |
| work | `work.md` | Step-by-step with remediation loop |
| ultrawork | `ultrawork.md` | 5-Phase Gate Loop (11 reviews) |
| plan | `plan.md` | PM task breakdown |
| brainstorm | `brainstorm.md` | Design-first ideation |
| review | `review.md` | QA audit |
| debug | `debug.md` | Root cause + minimal fix |
| scm | `scm.md` | SCM + Git operations + Conventional Commits |

To execute: read and follow `.agents/workflows/{name}.md` step by step.

## Auto-Detection

Hooks: `UserPromptSubmit` (keyword detection), `PreToolUse`, `Stop` (persistent mode)
Keywords defined in `.agents/hooks/core/triggers.json` (multi-language).
Persistent workflows (orchestrate, ultrawork, work) block termination until complete.
Deactivate: say "workflow done".

## Rules

1. **Do not modify `.agents/` files** — SSOT protection
2. Workflows execute via keyword detection or explicit naming — never self-initiated
3. Response language follows `.agents/oma-config.yaml`

## Project Rules

Read the relevant file from `.agents/rules/` when working on matching code.

| Rule | File | Scope |
|------|------|-------|
| backend | `.agents/rules/backend.md` | on request |
| commit | `.agents/rules/commit.md` | on request |
| database | `.agents/rules/database.md` | **/*.{sql,prisma} |
| debug | `.agents/rules/debug.md` | on request |
| design | `.agents/rules/design.md` | on request |
| dev-workflow | `.agents/rules/dev-workflow.md` | on request |
| frontend | `.agents/rules/frontend.md` | **/*.{tsx,jsx,css,scss} |
| i18n-guide | `.agents/rules/i18n-guide.md` | always |
| infrastructure | `.agents/rules/infrastructure.md` | **/*.{tf,tfvars,hcl} |
| mobile | `.agents/rules/mobile.md` | **/*.{dart,swift,kt} |
| quality | `.agents/rules/quality.md` | on request |

<!-- OMA:END -->
