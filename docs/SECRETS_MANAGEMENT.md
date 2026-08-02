# Production Secrets Management Guidelines

## Overview
The **Repository Intelligence Platform (RIP)** enforces a zero-secrets-in-code policy. `.env` files are used exclusively for local development and unit testing and are strictly disallowed in production environments.

In production deployments, configuration parameters and credentials must be injected directly as process environment variables by the host platform's secret store.

---

## Required Secrets & Environment Variables

| Variable Name | Required | Description | Example / Format |
|---|---|---|---|
| `APP_ENVIRONMENT` | Yes | Deployment environment (`development`, `staging`, `production`) | `production` |
| `GITHUB_TOKEN` | Yes | Personal Access Token (PAT) for GitHub API authentication | `ghp_...` |
| `DATABASE_URL` | Yes | PostgreSQL connection string | `postgresql://user:pass@host:5432/dbname` |
| `REDIS_URL` | Optional | Redis connection string for caching | `redis://:pass@host:6379/0` |
| `VAULT_TOKEN` | Optional | HashiCorp Vault token (if Vault provider enabled) | `hvs....` |

---

## Production Deployment Providers

### 1. Render Deployment
1. Navigate to **Environment Secrets** in the Render Dashboard.
2. Add `APP_ENVIRONMENT=production`, `GITHUB_TOKEN`, and `DATABASE_URL`.
3. Render injects these variables securely into the container runtime without writing secrets to disk.

### 2. Railway Deployment
1. Navigate to **Variables** in the Railway Project Settings.
2. Add variables using Railway's encrypted Variable Editor.

### 3. Kubernetes / Helm Deployment
1. Create an encrypted Kubernetes Secret manifest:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: rip-backend-secrets
type: Opaque
stringData:
  GITHUB_TOKEN: "ghp_..."
  DATABASE_URL: "postgresql://..."
```
2. Reference secrets in Deployment pod specs via `envFrom.secretRef`.

### 4. CI/CD GitHub Actions Workflow
1. Store secrets in **Repository Settings -> Secrets and Variables -> Actions**.
2. Pass secrets into CI test jobs:
```yaml
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }}
```

---

## Security Invariants
- **No Mock Credentials**: Code must raise `MissingSecretError` if a required credential is missing in production.
- **Redaction**: Structured logging formatters automatically redact authorization tokens, database passwords, and Bearer tokens.
