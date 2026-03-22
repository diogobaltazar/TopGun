---
description: "Project-level Claude configuration. Subcommands: config — add agents, skills, or CLAUDE.md entries to the current project's .claude/ directory."
allowed-tools: Agent, Read, Glob, Grep, Bash
---

You are orchestrating project-level Claude configuration.

Parse `$ARGUMENTS`:
- If it starts with `config`, strip `config` and run the **Config flow** below.
- Otherwise, tell the user the available subcommands: `config`.

---

## Config flow (`/project config <what you want>`)

Invoke `project-conf-agent` with the user's request.

The agent will:
1. Inspect the current project (stack, existing `.claude/` contents)
2. Converse with the user to understand what they want
3. Create the appropriate files inside `.claude/` of the current project

When the agent is done, summarise what was created for the user.

### Important context to pass to the agent

- All writes go to `.claude/` in the current working directory — the project Claude is open in.
- If Claude is running inside the rose repo, `.claude/` here means `rose/.claude/` — **not** `rose/global/`. Files written here are project-specific and are not installed globally by `rose install`.
- Never modify `~/.claude/` or `rose/global/`.
