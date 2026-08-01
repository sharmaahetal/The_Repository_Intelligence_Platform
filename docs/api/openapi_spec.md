# OpenAPI Specification & API Architecture Guide

## Overview
The **Repository Intelligence Platform (RIP)** REST API exposes endpoints for generating repository forecasts, retrieving system metrics, and executing health checks.

## Endpoints Summary

### 1. `GET /api/v1/forecast/{owner}/{repo}`
Generates a 180-day growth, maintainability, and abandonment risk forecast for a target GitHub repository.

#### Path Parameters
- `owner` (string, required): GitHub repository owner or organization (e.g. `facebook`).
- `repo` (string, required): GitHub repository name (e.g. `react`).

#### Query Parameters
- `horizon` (integer, default: 180): Prediction horizon in days (`90`, `180`, `365`).
- `model_version` (string, default: `v1.0`): Target model version string.

#### Example Request
```http
GET /api/v1/forecast/facebook/react?horizon=180&model_version=v1.0 HTTP/1.1
Host: localhost:8000
Accept: application/json
```

#### Example Response (200 OK)
```json
{
  "repository": "facebook/react",
  "owner": "facebook",
  "repo": "react",
  "prediction_horizon_days": 180,
  "prediction_time": "2026-08-01T16:42:00.000000+00:00",
  "snapshot_time": "2026-08-01T00:00:00.000000+00:00",
  "model_version": "v1.0",
  "feature_schema_version": 1,
  "label_schema_version": 1,
  "forecast": {
    "growth_probability": 0.84,
    "abandonment_probability": 0.05,
    "maintainer_retention_probability": 0.92,
    "derived_health_index": 88
  },
  "confidence": 0.88,
  "top_factors": [
    {
      "name": "contributor_retention_rate:v1",
      "impact": 0.28,
      "description": "High core maintainer activity"
    }
  ],
  "narrative_summary": "Strong upward trajectory expected for facebook/react. Derived health index 88/100.",
  "top_drivers": ["Sustained core contributor retention rate"],
  "top_risks": [],
  "lineage": {
    "prediction_id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
    "model_version": "v1.0",
    "dataset_version": "v1.0",
    "feature_schema_version": 1,
    "snapshot_timestamp": "2026-08-01T00:00:00+00:00",
    "git_commit": "fb1ac76"
  },
  "cached": false
}
```

### 2. `GET /api/v1/metrics`
Exposes Prometheus-formatted metrics (`rip_requests_total`, `rip_cache_hit_ratio`, `rip_request_latency_avg_ms`, `rip_model_version_usage_total`).

### 3. `GET /api/v1/health/live` & `GET /api/v1/health/ready`
Liveness and readiness probes for Kubernetes and container orchestrators.

## Error Catalog
- `400 Bad Request`: Invalid parameter format or missing owner/repo.
- `404 Not Found`: Repository not found on GitHub.
- `503 Service Unavailable`: Model registry unavailable or rate limit exceeded.

## Rate Limiting & Authentication
- **Authentication**: Bearer Token via `Authorization: Bearer <TOKEN>` header.
- **Rate Limit**: 120 requests/minute per client IP.
