# rose

Coding agent scaffolding tool. Bootstraps Claude Code super-agent config into any project.

## Setup

Add this alias to your `~/.zshrc`:

```bash
alias rose='docker run --rm -it \
  -v "$(pwd):/project" \
  -v "$HOME/.claude:/claude" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  -e GITHUB_TOKEN="$(gh auth token 2>/dev/null)" \
  rose:latest'
```

Then reload:
```bash
source ~/.zshrc
```

## Commands

| Command | Does |
|---|---|
| `rose install` | Install global Claude config onto host (`~/.claude`) |
| `rose reinstall` | Wipe `~/.claude` and reinstall from scratch (alias for `rose install --reset`) |
| `rose init` | Bootstrap current project with `CLAUDE.md` + component agents |
| `rose remove` | Remove rose Claude setup from current project |
| `rose add <name>` | Add a registry config to current project |
| `rose register <path>` | Register a project agent into the rose registry via PR |

### rose install
Run once per host. Installs to `~/.claude`:
- `settings.json` — hooks (feedback loops, auto-linting, stop checks)
- `hooks/` — post-write validation script
- `agents/` — global agents (commit-organizer, doc-verifier, code-health, tdd-enforcer)
- `commands/` — slash commands (/commit, /verify, /docs, /health)

```bash
rose install                          # install into ~/.claude
rose install --force                  # overwrite existing files
rose install --reset                  # wipe ~/.claude and reinstall from scratch
rose install --link ~/source/.claude  # install into ~/source/.claude and symlink ~/.claude to it
rose reinstall                        # alias for rose install --reset
```

### rose init
Run once per project. Copies into current directory:
- `CLAUDE.md` — fill in your stack and validation commands
- `.claude/agents/` — component agents (auth, list-ui, rag)

```bash
rose init
```

### rose remove
Removes `.claude/agents/` and `CLAUDE.md` from the current project.

```bash
rose remove      # prompts for confirmation
rose remove -y   # skip confirmation
```

### rose add
Import a named config from the registry into the current project.

```bash
rose add fastapi
rose add rag-milvus
rose add fastapi --force   # overwrite existing agent
```

### rose register
Register a project agent into the rose registry by opening a PR.

```bash
rose register .claude/agents/rag.md
rose register .claude/agents/rag.md --name rag-milvus
```

## Registry

Built-in configs shipped with the image:

| Name | Description |
|---|---|
| `fastapi` | FastAPI service agent |
| `rag-milvus` | RAG pipeline with Milvus vector store |

## This repo IS the config

All files under `.claude/` are the source of truth:
- `.claude/template/` — copied by `rose init`
- `.claude/global/` — installed by `rose install`
- `.claude/registry/` — imported by `rose add`

To update config, edit files here and rebuild the image.

## Build

```bash
docker build -t rose .
```
