# Contributing to Globe CRM

## Getting Started

1. Clone the repository
2. Create a feature branch from `main`
3. Make your changes
4. Submit a pull request

## Branch Naming

Use the Linear issue identifier as the branch name:

```
FIR-<number>
```

## Commit Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description
```

**Types:** `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`

**Scopes:** `core`, `frontend`, `backend`, `data`

## Pull Requests

- Target `main` branch
- Require at least one approving review from the owning team (see `CODEOWNERS`)
- All CI checks must pass before merging
- Use squash merge for feature branches

## Code Review

- Reviewers are auto-assigned via `CODEOWNERS`
- Reviews should focus on correctness, readability, and maintainability
- Address all review comments before merging
