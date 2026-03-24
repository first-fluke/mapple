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
