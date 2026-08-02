# Disaster Recovery, Backup & Restore Strategy

## Overview
This document outlines the backup, retention, and disaster recovery procedures for the **Repository Intelligence Platform (RIP)**.

The platform manages four persistent data artifacts:
1. **Raw Payloads & Snapshots** (`PostgreSQL / SQLite database`)
2. **Parquet Datasets** (`datasets/export/`)
3. **Trained Model Artifacts** (`artifacts/registry/`)
4. **Experiment & Schema Metadata** (`artifacts/experiments/`)

---

## Backup Schedules & Retention Policy

| Target | Frequency | Backup Method | Retention Window |
|---|---|---|---|
| PostgreSQL Database | Daily (02:00 UTC) | `pg_dump` compressed dump to S3/GCS | 30 daily, 12 monthly |
| Model Registry (`artifacts/registry`) | Daily (03:00 UTC) | Tarball gzip archive to S3/GCS | 90 days |
| Datasets (`datasets/`) | Weekly (Sunday) | Parquet directory sync to Cloud Storage | 180 days |

---

## Step-by-Step Restoration Procedures

### 1. Database Restoration Procedure
To restore a database dump:
```bash
# 1. Stop backend services
docker-compose stop backend

# 2. Restore PostgreSQL database dump
pg_restore -h localhost -U rip_user -d predictive_analytics_db --clean daily_backup_2026-08-01.dump

# 3. Restart backend services
docker-compose start backend
```

### 2. Model Registry Restoration Procedure
To restore model artifacts to the registry directory:
```bash
# Extract model registry tarball archive into registry base directory
tar -xzf model_registry_backup_2026-08-01.tar.gz -C /var/lib/rip/artifacts/registry/

# Verify restored model artifacts via readiness probe
curl http://localhost:8000/api/v1/health/ready
```

---

## Emergency Contact & Escalation
- **Platform DevOps Lead**: `devops@repository-intelligence.internal`
- **Database Administrator**: `dba@repository-intelligence.internal`
