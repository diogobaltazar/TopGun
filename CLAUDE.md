# rose

rose is a scaffolding tool that installs and manages Claude Code configuration. This repo IS the source of truth for that configuration.

## Critical rule: edit the source code, not ~/.claude

When working inside this repo, any changes to Claude definitions — agents, commands, personas, hooks, settings — must be made to the source files here, **not** to `~/.claude` directly.

All definitions flow via `rose install`:

```
rose source (global/)  →  rose install  →  ~/.claude/
```

If you edit `~/.claude` directly, the change will be lost the next time someone runs `rose install`. Always edit the source here; the user will apply it by running `rose reinstall`.

## Project layout

```
global/        # Installed to ~/.claude/ by `rose install`
├── CLAUDE.md
├── settings.json
├── hooks/
│   ├── log-session-start.sh  # writes meta.json + session.start event (PreToolUse, once)
│   ├── log-tool-event.sh     # appends tool.call event (PostToolUse)
│   └── log-session-end.sh    # derives outcome + appends session.end (Stop)
├── agents/
│   ├── analyst.md      # Product analyst — R1-R5, W1, decision gate
│   ├── engineer.md     # Implementation agent — D3-D4
│   ├── github.md       # GitHub operations — D1, D6, D7, P2
│   └── git.md          # Git operations — D5
└── commands/
    ├── feature.md      # /feature workflow — full lifecycle orchestrator
    ├── github.md       # /github skill
    ├── git.md          # /git skill
    └── project.md      # /project skill (init, spec update)
src/rose/cli/  # Typer entrypoint (package)
├── __init__.py     # app definition, command registration
├── install.py      # rose install
└── uninstall.py    # rose uninstall
src/rose/api/  # FastAPI backend for observe dashboard
├── Dockerfile
├── requirements.txt
└── main.py
src/rose/web/  # nginx frontend for observe dashboard
├── Dockerfile
├── nginx.conf
├── index.html
├── app.js
└── style.css
pyproject.toml
Dockerfile
compose.yml    # rose + api + web services
```

## Testing changes

With `ROSE_DEV=$HOME/rose` set (already in your `~/.zshrc`), rose rebuilds from this directory on every run:

```bash
rose reinstall    # wipe ~/.claude and reinstall from this branch's source
```

Switch branches freely — `rose reinstall` always installs from the current checkout.
