# Runbook: Backend Service Outage (`backend_down`) 🚨

## Overview
This runbook covers diagnosis and recovery steps when the **FastAPI Backend Service** is unresponsive or returning HTTP `5xx` errors.

---

## 1. Symptoms & Detection
- Alert: `/health/live` returns connection refused or HTTP 502/503.
- Browser extension displays: *"Backend Unreachable. Displaying cached forecast..."*

---

## 2. Diagnosis Steps
1. Check container execution status:
   ```bash
   docker compose ps
   ```
2. Inspect backend container logs:
   ```bash
   docker compose logs --tail=100 backend
   ```
3. Check CPU/Memory resource constraints:
   ```bash
   docker stats backend
   ```

---

## 3. Recovery Steps
1. Restart backend container:
   ```bash
   docker compose restart backend
   ```
2. Verify liveness probe:
   ```bash
   curl http://localhost:8000/api/v1/health/live
   ```
3. If container fails to start, verify environment variables in `.env`.
