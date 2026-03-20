#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-/project}"

echo "Initializing rose in $TARGET..."

# .claude/agents/
if [ -d "$TARGET/.claude/agents" ]; then
  echo "  .claude/agents/ already exists — skipping (no overwrite)"
else
  mkdir -p "$TARGET/.claude/agents"
  cp -r /rose/template/.claude/agents/. "$TARGET/.claude/agents/"
  echo "  created .claude/agents/ (auth, list-ui, rag)"
fi

# CLAUDE.md
if [ -f "$TARGET/CLAUDE.md" ]; then
  echo "  CLAUDE.md already exists — skipping (no overwrite)"
else
  cp /rose/template/CLAUDE.md "$TARGET/CLAUDE.md"
  echo "  created CLAUDE.md"
fi

echo ""
echo "Done. Next steps:"
echo "  1. Edit CLAUDE.md — fill in your stack and validation commands"
echo "  2. Edit .claude/agents/*.md — tailor each agent to this project"
echo "  3. Delete agents you don't need, add new ones for your components"
