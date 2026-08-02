# Repository Intelligence Platform (RIP) — 5-7 Minute Technical Demo Video Script

## Overview & Demo Goal
This script guides a 5-7 minute screen recording demonstrating the core architecture, machine learning innovations, backend performance, and browser extension user experience of the Repository Intelligence Platform.

---

## 🎬 Video Script Breakdown

### **0:00 – 1:00 | Act I: The Problem & Vision**
- **Visual**: Show a typical GitHub repository (e.g. `facebook/react` or `microsoft/vscode`).
- **Narrative**:
  > *"When evaluating open-source software, engineers look at static metrics like star counts or total open issues. But stars are cumulative—they don't tell you if a project is actively accelerating, stagnating, or on the brink of maintainer burnout.*
  > *Welcome to the Repository Intelligence Platform (RIP). RIP forecasts the future evolution of software repositories by learning from point-in-time historical snapshots, outputting calibrated probabilities for growth, maintainability, and abandonment over 90, 180, and 365-day horizons."*

---

### **1:00 – 2:30 | Act II: Historical Snapshot Engine & Temporal Leakage Guard**
- **Visual**: Show architecture diagram from [README.md](../README.md) and code in `backend/app/snapshots/snapshot_builder.py`.
- **Narrative**:
  > *"To train reliable predictive models, we must eliminate data leakage. Traditional pipelines look at current state, introducing lookahead bias. RIP uses a deterministic Snapshot Engine that constructs point-in-time snapshots $S(t_k)$ frozen in Pydantic models.*
  > *Our 24-dimensional temporal feature store calculates velocity, acceleration, contributor density, and governance metrics strictly using data generated at or before $t_k$."*

---

### **2:30 – 4:00 | Act III: Multi-Horizon Inference & SHAP Narrative Engine**
- **Visual**: Run `python -m ml.inference.predictor` or execute `curl http://localhost:8000/api/v1/forecast/facebook/react?horizon=180`. Show JSON payload in Postman / Swagger UI.
- **Narrative**:
  > *"Here is the multi-horizon prediction output for `facebook/react`. Notice the 180-day forecast: 84% probability of sustained growth, 4% probability of abandonment, and 88% maintainer retention.*
  > *Instead of giving users black-box probabilities, our Narrative Synthesizer leverages SHAP tree explainers to translate top feature attributions into natural language summaries."*

---

### **4:00 – 5:30 | Act IV: Chrome Extension Injection & SPA Observer**
- **Visual**: Navigate to GitHub in Chrome with the unpacked `extension/dist` installed. Show the RIP overlay rendered in the sidebar.
- **Narrative**:
  > *"To make these insights actionable, we built a Manifest V3 cross-browser extension using React and Zustand. Using a MutationObserver, the content script detects GitHub SPA page navigation, checks local storage caches in under 5ms, and renders the intelligence card in under 350ms."*

---

### **5:30 – 6:30 | Act V: Performance Benchmarks & Conclusion**
- **Visual**: Show [docs/performance.md](../docs/performance.md) and terminal running `python -m backend.app.monitoring.benchmark`.
- **Narrative**:
  > *"Under the hood, RIP processes **2,381 snapshots per second** with a sub-millisecond builder latency of 0.103ms and a $p_{50}$ prediction latency of 12.5ms.*
  > *The entire codebase is fully documented, tested with 100% pass rates across 70 integration tests, and ready for production deployment. Thank you for watching!"*
