# Runbook: Cache Connection Failure (`redis_failure`) ⚡

## Overview
This runbook covers diagnosis and recovery steps when **Redis Cache** is unresponsive.

---

## 1. Symptoms & Detection
- API latency increases due to cache miss fallback behavior.
- Backend logs emit `RedisConnectionError`.

---

## 2. Fallback Behavior
- The backend gracefully degrades to direct snapshot engine evaluation when Redis is down. API endpoints remain operational.

---

## 3. Recovery Steps
1. Verify Redis container status:
   ```bash
   docker compose ps redis
   ```
2. Restart Redis container:
   ```bash
   docker compose restart redis
   ```
3. Test ping response:
   ```bash
   redis-cli -h localhost ping
   # Expected: PONG
   ```
