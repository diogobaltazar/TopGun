#!/usr/bin/env bash
# log-step-event.sh <agent> <step> <event> <payload_json>
# Appends a single structured step event to the active session's events.jsonl.
#
# Usage:
#   ~/.claude/hooks/log-step-event.sh rose FP step.enter '{"from":null}'
#   ~/.claude/hooks/log-step-event.sh rose AF step.exit '{"to":"CONVERGENCE","outcome":"confirmed"}'

set -euo pipefail

AGENT="${1:-unknown}"
STEP="${2:-unknown}"
EVENT="${3:-step.enter}"
if [ -n "${4:-}" ]; then PAYLOAD="$4"; else PAYLOAD="{}"; fi

SESSION_ID=$(cat "$HOME/.claude/logs/.active-session" 2>/dev/null || echo "unknown")
LOG_DIR="$HOME/.claude/logs/$SESSION_ID"
mkdir -p "$LOG_DIR"

SEQ=$(( $(wc -l < "$LOG_DIR/events.jsonl" 2>/dev/null || echo 0) + 1 ))
TS=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")

printf '%s\n' "{\"ts\":\"$TS\",\"session_id\":\"$SESSION_ID\",\"seq\":$SEQ,\"source\":\"agent\",\"agent\":\"$AGENT\",\"step\":\"$STEP\",\"event\":\"$EVENT\",\"payload\":$PAYLOAD}" \
  >> "$LOG_DIR/events.jsonl"
