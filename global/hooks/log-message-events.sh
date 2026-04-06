#!/usr/bin/env bash
# Logs PreToolUse/PostToolUse events for the SendMessage tool.
# Invoked by the PostToolUse:SendMessage hook in settings.json.
mkdir -p "${HOME}/.claude/logs"
PAYLOAD=$(cat)
TS=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
printf '%s\n' "{\"ts\":\"${TS}\",\"hook\":\"${HOOK_EVENT:-unknown}\",\"payload\":${PAYLOAD}}" \
  >> "${HOME}/.claude/logs/message-events.jsonl"
