---
description: Audit codebase for stale code, dead code, and refactoring opportunities
allowed-tools: Read, Glob, Grep, Bash
---

Invoke the `code-health` agent to audit the codebase. If $ARGUMENTS is provided, scope the audit to that directory or file pattern.

Focus area: $ARGUMENTS

Produce the health report as described in the code-health agent, then ask the user which items they want to address.
