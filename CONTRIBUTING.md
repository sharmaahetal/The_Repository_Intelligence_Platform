# Contributing to Repository Intelligence Platform (RIP) 🤝

Thank you for your interest in contributing! We welcome pull requests, bug reports, feature requests, and code improvements.

---

## 🛠️ Development Guidelines

1. **Conventional Commits**:
   All commits must adhere to the [Conventional Commits](https://www.conventionalcommits.org/) specification:
   - `feat:` New features
   - `fix:` Bug fixes
   - `refactor:` Code improvements
   - `test:` Unit/integration tests
   - `docs:` Documentation updates
   - `chore:` Configuration and maintenance

2. **Code Quality & Static Analysis**:
   Before submitting a Pull Request, verify that all static analysis checks pass with **zero errors**:
   ```bash
   .venv/bin/ruff check .
   .venv/bin/ruff format --check .
   .venv/bin/mypy backend/
   .venv/bin/pytest
   ```

3. **Temporal Anti-Leakage Guard**:
   Ensure all feature engineering logic operates strictly on data available $\le t_k$ for a given point-in-time snapshot $S(t_k)$. Never introduce lookahead bias.

---

## 🚀 Submitting a Pull Request

1. Fork the repository and create a feature branch (`git checkout -b feat/your-feature`).
2. Make granular, focused commits with clear descriptions.
3. Run the complete test suite (`pytest`).
4. Push to your fork and submit a Pull Request targeting `main`.
