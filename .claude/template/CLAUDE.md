# About CLAUDE.md

This file is automatically read by Claude Code at the start of every session.
It gives the agent persistent context about the project — without it, the agent
has no memory of your stack, standards, or how to validate code between sessions.

Fill in the sections below for your project. The Validation Commands section is
critical: the agent's Stop hook reads these to run checks before it is allowed
to finish any task.

---

# Project: [PROJECT NAME]

## Overview
[Brief description of the project]

## Tech Stack
- **Frontend**: [e.g. Next.js 14, TypeScript, Tailwind]
- **Backend**: [e.g. FastAPI, PostgreSQL]
- **Testing**: [e.g. Vitest, pytest]
- **Lint/Format**: [e.g. Biome, ESLint, Ruff]

## Validation Commands
<!-- CRITICAL: The agent uses these for its feedback loop -->
```
lint:      npx biome check .
typecheck: npx tsc --noEmit
test:      npm run test
test:unit: npm run test:unit
test:e2e:  npm run test:e2e
build:     npm run build
```

## Project Structure
```
src/
├── components/    # UI components
├── features/      # Feature modules (auth, rag, etc.)
├── lib/           # Shared utilities
└── types/         # TypeScript types
```

## Component Ownership (Agents)
Each component has a dedicated agent thread. Consult the relevant agent for component-specific work:

| Component | Agent | Scope |
|-----------|-------|-------|
| UI Lists  | `list-ui` | List components, pagination, filters |
| RAG       | `rag` | Retrieval, embeddings, vector store |
| Auth      | `auth` | Authentication, authorization, sessions |

## Coding Standards
- Prefer composition over inheritance
- All public functions must have tests before implementation (TDD)
- No `any` types in TypeScript
- Max function length: 40 lines — split if longer
- All async operations must have error handling

## Definition of Done
Before considering ANY task complete, verify:
- [ ] Tests written and passing
- [ ] TypeScript compiles without errors
- [ ] Linter passes with no warnings
- [ ] Relevant docs updated
- [ ] No `console.log` left in production code
- [ ] No TODO comments left unaddressed
