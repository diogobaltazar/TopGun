---
description: Full verification cycle — lint, typecheck, tests, docs check
allowed-tools: Bash, Read, Glob, Grep
---

Run a full verification pass on the current project. Do the following in order, stopping and reporting any failures:

1. **Detect project type** — check for package.json, pyproject.toml, Cargo.toml, go.mod
2. **Lint** — run the project's linter (eslint, ruff, clippy, golangci-lint)
3. **Type check** — run the project's type checker (tsc --noEmit, mypy, cargo check)
4. **Tests** — run the full test suite
5. **Docs** — invoke the `doc-verifier` agent to check documentation is current

Report results in a summary table:
```
| Check      | Status | Details        |
|------------|--------|----------------|
| Lint       | ✓/✗   | ...            |
| Type check | ✓/✗   | ...            |
| Tests      | ✓/✗   | X passed, Y failed |
| Docs       | ✓/✗   | ...            |
```

If any check fails, fix the issues before reporting complete.
