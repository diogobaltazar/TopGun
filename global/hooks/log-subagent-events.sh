#!/usr/bin/env bash
# Diagnostic hook — logs raw stdin payload for SubagentStart and SubagentStop.
# Bound to both events in settings.json.
# Output: ~/.claude/logs/subagent-events.jsonl

mkdir -p "${HOME}/.claude/logs"
PAYLOAD=$(cat)
TS=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
printf '%s\n' "{\"ts\":\"${TS}\",\"hook\":\"${HOOK_EVENT:-unknown}\",\"payload\":${PAYLOAD}}" \
  >> "${HOME}/.claude/logs/subagent-events.jsonl"
