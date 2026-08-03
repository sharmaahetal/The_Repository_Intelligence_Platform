# Runbook: Database Connection Failure (`database_failure`) 🗄️

## Overview
This runbook covers diagnosis and recovery steps when the **PostgreSQL Database** connection is degraded or failing.

---

## 1. Symptoms & Detection
- Alert: `/health/ready` returns `"status": "degraded"`.
- Backend logs exhibit `OperationalError: cannot connect to server` or connection pool timeouts.

---

## 2. Diagnosis Steps
1. Verify PostgreSQL container process:
   ```bash
   docker compose ps postgres
   ```
2. Test raw PostgreSQL TCP connectivity:
   ```bash
   nc -zv localhost 5432
   ```
3. Inspect PostgreSQL logs:
   ```bash
   docker compose logs --tail=100 postgres
   ```

---

## 3. Recovery Steps
1. Restart PostgreSQL service:
   ```bash
   docker compose restart postgres
   ```
2. If corrupt state exists, perform restoration procedure detailed in [BACKUP_AND_RESTORE.md](../BACKUP_AND_RESTORE.md).
