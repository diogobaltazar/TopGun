#!/usr/bin/env bash
# Bound to SubagentStart.
# Maps the launching agent type to a step code and emits step.enter to events.jsonl.
# Agents not in the map are silently ignored.

set -euo pipefail

STDIN_PAYLOAD=$(cat)

SESSION_ID=$(echo "$STDIN_PAYLOAD" | python3 -c "import sys,json; print(json.load(sys.stdin).get('session_id','unknown'))" 2>/dev/null || echo "unknown")
AGENT_TYPE=$(echo "$STDIN_PAYLOAD" | python3 -c "import sys,json; print(json.load(sys.stdin).get('agent_type',''))" 2>/dev/null || echo "")

# Map agent type → step code. Anything else is not our concern.
case "$AGENT_TYPE" in
  deep-research)   STEP="DR" ;;
  code-inspect)    STEP="CI" ;;
  backlog-inspect) STEP="BI" ;;
  *)               exit 0 ;;
esac

LOG_DIR="${HOME}/.claude/logs/${SESSION_ID}"
EVENTS_FILE="${LOG_DIR}/events.jsonl"

[[ ! -d "$LOG_DIR" ]] && exit 0   # no session yet — nothing to write to

TS=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
SEQ=$(( $(wc -l < "$EVENTS_FILE" 2>/dev/null || echo 0) + 1 ))

printf '%s\n' "{\"ts\":\"${TS}\",\"session_id\":\"${SESSION_ID}\",\"seq\":${SEQ},\"source\":\"hook\",\"agent\":\"${AGENT_TYPE}\",\"step\":\"${STEP}\",\"event\":\"step.enter\",\"payload\":{\"from\":\"AF\"}}" \
  >> "$EVENTS_FILE"
