# Development Rules & Guidelines

1. **Never let technical debt pile up**
   - Fix architectural flaws and code smells early. Refactor while the scope is manageable.

2. **Commit often with granular, conventional messages**
   - Use strict conventional commit prefixes: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`.
   - Ensure commits tell a clear, step-by-step story of how the project evolved.

3. **Document as you build**
   - Write subsystem documentation immediately upon completion. Do not defer documentation to the end of the project.

4. **Keep implementation plan "living"**
   - Continuously update design documents and `implementation_plan.md` as new findings, requirements, or architecture decisions emerge.

5. **Don't optimize prematurely**
   - Focus on establishing a correct implementation first.
   - Address performance, caching, concurrency, and complexity optimizations only after verifying functional correctness.
