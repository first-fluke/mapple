# Globe CRM - Team Structure

## Teams

### Core (`@globe-crm/core`)

Responsible for the overall architecture, shared libraries, and platform infrastructure.

**Ownership:** Default owners for all files not covered by other teams.

### Frontend (`@globe-crm/frontend`)

Responsible for the web application, UI components, and client-side logic.

**Ownership:**

- `src/app/`
- `src/components/`
- `src/hooks/`
- `src/styles/`

### Backend (`@globe-crm/backend`)

Responsible for API services, business logic, and server-side infrastructure.

**Ownership:**

- `src/api/`
- `src/services/`
- `src/lib/`

### Data (`@globe-crm/data`)

Responsible for database schemas, migrations, and data access layers.

**Ownership:**

- `src/db/`
- `prisma/`
- `migrations/`

## Roles

| Role | Responsibilities |
| --- | --- |
| **Admin** | Full access, team settings, member management |
| **Member** | Code contributions, reviews, issue management |
| **Guest** | Read access, limited issue interaction |

## Workflow

1. Issues are tracked in [Linear](https://linear.app)
2. Each team manages its own backlog and sprint cycles
3. Cross-team work is coordinated through the Core team
4. All PRs require at least one review from the owning team
