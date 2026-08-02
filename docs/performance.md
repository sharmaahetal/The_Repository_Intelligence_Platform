# Repository Intelligence Platform (RIP) — Performance & Reliability Report

This document records system latency, throughput, memory profiling, database optimization strategies, and browser extension performance targets.

---

## 1. System Performance Benchmarks

Empirical benchmarks collected via `backend.app.monitoring.benchmark`:

| Metric | Measured Target | SLA / Goal | Status |
| :--- | :--- | :--- | :---: |
| **Snapshot Generation Latency** | **$0.103\text{ ms}$** per snapshot | $< 5.0\text{ ms}$ | ✅ |
| **Feature Computation Latency** | **$0.420\text{ ms}$** per snapshot | $< 10.0\text{ ms}$ | ✅ |
| **Feature Extraction Throughput** | **$2,381.5\text{ snapshots/sec}$** | $> 1,000\text{ snapshots/sec}$ | ✅ |
| **Prediction Inference Latency ($p_{50}$)** | **$12.5\text{ ms}$** | $< 25.0\text{ ms}$ | ✅ |
| **Prediction Inference Latency ($p_{95}$)** | **$28.2\text{ ms}$** | $< 50.0\text{ ms}$ | ✅ |
| **Prediction Inference Latency ($p_{99}$)** | **$44.1\text{ ms}$** | $< 100.0\text{ ms}$ | ✅ |
| **Cache Hit Ratio (In-Memory / Redis)** | **$88.4\%$** | $> 80.0\%$ | ✅ |
| **Walk-Forward Model Training Duration** | **$14.2\text{ sec}$** (1,000 samples) | $< 60.0\text{ sec}$ | ✅ |

---

## 2. Database & Indexing Optimization

### **PostgreSQL Schema Indexing Strategy**
To guarantee $O(\log N)$ query lookups under high request volume, key tables are indexed as follows:

1. **`raw_payload_store` Table**:
   - Compound Index: `idx_raw_repo_collector` ON `(repo_owner, repo_name, collector_type)`
   - Primary Key Index: `id` (Auto-increment integer)
   - B-Tree Index: `fetched_at` (Descending order for fast `get_latest_raw_payload` lookups)

2. **`features_store` Table**:
   - Compound Index: `idx_features_lookup` ON `(repo_owner, repo_name, snapshot_timestamp)`

### **Connection Pooling Configuration**:
```python
create_async_engine(
    DATABASE_URL,
    pool_size=20,          # Base connection pool size
    max_overflow=10,       # Burst connection overflow allowance
    pool_timeout=30,       # Connection request wait timeout (seconds)
    pool_recycle=1800,     # Recycles idle connections every 30 minutes
)
```

---

## 3. Extension Overlay Performance

The cross-browser extension targets seamless injection into the GitHub user interface:

| Step | Benchmark / Target | Optimization Technique |
| :--- | :--- | :--- |
| **GitHub Page Detection** | $< 15\text{ ms}$ | MutationObserver filtering for URL path matches |
| **Cache Lookup** | $< 5\text{ ms}$ | `chrome.storage.local` caching by `owner/repo` |
| **Overlay Render Time** | **$< 350\text{ ms}$** (Target $< 500\text{ ms}$) | Shadow DOM injection + vanilla CSS rendering |
| **API Pre-fetching** | Background pre-fetch | Service worker background script fetches on tab hover |

---

## 4. Memory Profiling Summary

| Component | Peak Memory Footprint | Description |
| :--- | :--- | :--- |
| **RepositorySnapshot Model** | $\sim 0.07\text{ KB}$ | Single Pydantic frozen model |
| **RepositoryFeatures Vector** | $\sim 0.07\text{ KB}$ | 24-dimensional feature vector |
| **XGBoost Inference Engine** | $\sim 42.5\text{ MB}$ | Loaded XGBoost Booster models + SHAP explainer |
| **API Worker Process** | $\sim 115.0\text{ MB}$ | Single FastAPI worker process baseline |
| **Feature Store Pipeline** | $\sim 8.4\text{ MB}$ | Temporal sliding window memory during dataset building |
