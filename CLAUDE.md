# rose

rose is a scaffolding tool that installs and manages Claude Code configuration. This repo IS the source of truth for that configuration.

## Critical rule: edit the source code, not ~/.claude

When working inside this repo, any changes to Claude definitions — agents, commands, personas, hooks, settings — must be made to the source files here, **not** to `~/.claude` directly.

All definitions flow via `rose upgrade`:

```
rose source (global/)  →  rose upgrade  →  ~/.claude/
```

If you edit `~/.claude` directly, the change will be lost the next time someone runs `rose upgrade`. Always edit the source here; the user will apply it by running `rose upgrade`.

## Testing changes

To test changes, build the image from source and then run `rose upgrade`:

```bash
docker compose build rose
rose upgrade    # reinstall from this branch's source
```

Switch branches freely — build and upgrade again to pick up the new branch's changes.

## Claude configuration questions are feature requests

Rose exists to install and manage Claude Code configuration. When a user asks about Claude Code settings, permissions, hooks, agents, commands, or any other aspect of Claude's configuration, treat it as a feature request for rose — not as a one-off configuration task. The answer is always a change to rose's source files that will be delivered via `rose install` or `rose upgrade`.

## Managed permissions

Rose installs a curated set of pre-approved permissions into `~/.claude/settings.json` via `rose upgrade`. The list lives in `global/settings.json` and is merged additively — existing user-added permissions are never removed.

### What is included and why

**Git — local operations (all reversible):**
`git diff*`, `git log*`, `git status*`, `git add*`, `git commit*`, `git checkout -b*`, `git worktree*`, `git branch*`, `git remote get-url*`

These are interrupted constantly and carry no meaningful risk. `git push*` and `git reset*` are excluded — they reach the remote or are destructive.

**File & directory inspection:** `ls*`, `pwd*`, `find*`, `du*`, `df*`, `wc*`, `file*`

Pure read. No side effects.

**File reading:** `cat*`, `head*`, `tail*`

Read-only. Needed for pipelines alongside the dedicated Read tool.

**Text processing:** `grep*`, `sort*`, `uniq*`, `awk*`, `jq*`

Read-only transforms.

**System info:** `ps*`, `uptime*`, `uname*`, `which*`, `type*`

Read-only system inspection.

**Environment variables:** `env*`, `printenv*`

Included deliberately. These transit the Anthropic API — but so does everything else in Claude's context. In this setup, local env vars hold only dev-level keys; real credentials are handled by the Portkey gateway. Keeping them approval-required would provide false security while adding genuine friction.

**Docker — read-only:** `docker ps*`, `docker images*`, `docker logs*`

List and inspect only. `docker exec*` and `docker run*` remain approval-required.

### What remains approval-required

`git push*`, `git reset*`, `rm*`, `docker exec*`, `docker run*`, `curl*`, `wget*`, `sudo*`, `npm*`, `pip*` — anything that reaches outward, deletes, installs, or executes in a running container.

### Extending the list

Add new entries to `global/settings.json` and run `rose upgrade`. Never edit `~/.claude/settings.json` directly — the change will be lost on the next upgrade.

## Feedback about rose behaviour

When the user gives feedback about how rose behaves — its development flow, its tone, its planning discipline, or any other aspect of its installed configuration — the fix belongs in the rose source files (this repo), not in Claude Code's memory system. Rose installs a harness; the harness is the source of truth. Creating a memory to patch around a harness deficiency means the fix is invisible to every other session and will not survive a reinstall. Edit the source.
