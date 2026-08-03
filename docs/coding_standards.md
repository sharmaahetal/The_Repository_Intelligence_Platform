# Coding Standards & Code Hygiene Guidelines 📜

## 1. Code Style & Formatting
- **Python**: PEP 8 compliance, explicit type annotations on all function signatures (`def fn(x: int) -> str:`), Google-style docstrings.
- **TypeScript**: Strict TypeScript (`strict: true` in `tsconfig.json`), no `any` types unless explicitly mapped, React functional components with `React.FC`.

## 2. Architectural Hygiene
- **Never Let Technical Debt Accumulate**: Fix architectural smells and code duplication immediately. Refactor while scope is manageable.
- **Never Guess Code Logic or Paths**: Always inspect authoritative source code using search and view tools.
- **No Superficial Symptom Patches**: Resolve underlying root causes. Never swallow exceptions silently or return dummy 0-byte fallbacks without logging.
- **Preserve API Contracts**: Modifications to function signatures require updating all callers system-wide.

## 3. Immutability & Value Objects
- Domain models (`RepositorySnapshot`, `SnapshotMetadata`, `PredictionContext`, `ForecastUIModel`) are immutable Value Objects.
- Domain state changes produce new object instances via pure functions.
