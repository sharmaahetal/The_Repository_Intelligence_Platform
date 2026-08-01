# Security Threat Model & Risk Mitigation Strategy

## Overview
This document details the security posture, threat model, and defense-in-depth controls for the Repository Intelligence Platform (RIP) backend services and Manifest V3 browser extension.

## Threat Analysis & Countermeasures

### 1. Cross-Site Scripting (XSS)
- **Threat**: Untrusted repository names, descriptions, or commit messages injected from GitHub DOM could execute arbitrary script in the content script or overlay card context.
- **Mitigation**:
  - All text content rendered inside React components is escaped using HTML entity encoding (`escapeHTML()`, `sanitizeText()`).
  - Strict React virtual DOM rendering without `dangerouslySetInnerHTML`.

### 2. Content Security Policy (CSP)
- **Threat**: Extension content script loading unauthorized external scripts or sending data to unapproved remote servers.
- **Mitigation**:
  - Manifest V3 strictly enforces `script-src 'self'`.
  - Host permissions restricted strictly to `*://github.com/*` and backend API endpoints (`http://localhost:8000/*`).

### 3. Service Worker & Messaging Isolation
- **Threat**: Web page scripts faking extension messages to tamper with forecast data.
- **Mitigation**:
  - `MessagingService` validates message sender identity via `sender.id === chrome.runtime.id`.
  - The content script never performs direct backend `fetch()` requests; all network activity is proxied through the background service worker.

### 4. API Abuse & Denial of Service (DoS)
- **Threat**: Malicious clients flooding the `/api/v1/forecast` endpoint to exhaust memory or GitHub API rate limits.
- **Mitigation**:
  - In-memory `PredictionCache` (15-minute TTL) absorbs repetitive repository queries.
  - Per-IP rate limiting (120 req/min) enforced at backend middleware layer.
  - Circuit breaker trips to fallback responses when GitHub API returns HTTP 429.

### 5. Secrets & Token Storage
- **Threat**: GitHub PAT or database connection strings leaked in client extension bundles or source repositories.
- **Mitigation**:
  - Extension bundle contains zero API keys or authentication tokens.
  - Backend secrets managed exclusively via `SecretsManager` environment variables or secret vaults.
