#!/usr/bin/env bash
# Bound to Stop in settings.json.
# Fires when Claude Code stops (session ends or is interrupted).
#
# Reads the final step.exit event from events.jsonl to determine outcome.
# Only marks the session completed (and clears .active-session) when the
# workflow reaches a true terminal step (P2 delivery or W1 investigation).
# Intermediate stops leave .active-session intact so --list shows "active".

set -euo pipefail

# Read stdin once; session_id lives in the JSON payload, not in env.
STDIN_PAYLOAD=$(cat)
SESSION_ID=$(echo "$STDIN_PAYLOAD" | python3 -c "import sys,json; print(json.load(sys.stdin).get('session_id','unknown'))" 2>/dev/null || echo "unknown")

LOG_DIR="${HOME}/.claude/logs/${SESSION_ID}"
EVENTS_FILE="${LOG_DIR}/events.jsonl"
META_FILE="${LOG_DIR}/meta.json"

mkdir -p "$LOG_DIR"

TS=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")

# Derive outcome from the last step.exit event, if any.
OUTCOME="abandoned"
if [[ -f "$EVENTS_FILE" ]]; then
  LAST_STEP=$(grep '"event":"step.exit"' "$EVENTS_FILE" | tail -1 | \
    python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('step',''))" 2>/dev/null || echo "")

  case "$LAST_STEP" in
    P2)   OUTCOME="delivery" ;;
    W1)   OUTCOME="investigation" ;;
    "")   OUTCOME="abandoned" ;;
    *)    OUTCOME="in_progress" ;;
  esac
fi

# Map outcome to meta status.
# Only "delivery" and "investigation" are truly terminal — everything else
# is an intermediate stop and the session should remain "active" in --list.
case "$OUTCOME" in
  delivery|investigation) STATUS="completed" ;;
  in_progress)            STATUS="in_progress" ;;
  *)                      STATUS="abandoned" ;;
esac

# Append session.end event.
SEQ=$(( $(wc -l < "$EVENTS_FILE" 2>/dev/null || echo 0) + 1 ))
printf '%s\n' "{\"ts\":\"${TS}\",\"session_id\":\"${SESSION_ID}\",\"seq\":${SEQ},\"source\":\"hook\",\"agent\":null,\"step\":null,\"event\":\"session.end\",\"payload\":{\"outcome\":\"${OUTCOME}\",\"final_step\":\"${LAST_STEP:-null}\"}}" \
  >> "$EVENTS_FILE"

ACTIVE_FILE="${HOME}/.claude/logs/.active-session"

if [[ "$STATUS" == "completed" ]]; then
  # Truly done — clear active-session and stamp ended_at.
  if [[ -f "$ACTIVE_FILE" ]] && [[ "$(cat "$ACTIVE_FILE")" == "$SESSION_ID" ]]; then
    rm -f "$ACTIVE_FILE"
  fi
  if [[ -f "$META_FILE" ]]; then
    python3 -c "
import sys, json
with open('${META_FILE}') as f:
    meta = json.load(f)
meta['ended_at'] = '${TS}'
meta['status'] = 'completed'
meta['outcome'] = '${OUTCOME}'
with open('${META_FILE}', 'w') as f:
    json.dump(meta, f, indent=2)
" 2>/dev/null || true
  else
    printf '%s\n' "{\"session_id\":\"${SESSION_ID}\",\"ended_at\":\"${TS}\",\"status\":\"completed\",\"outcome\":\"${OUTCOME}\"}" \
      > "$META_FILE"
  fi
elif [[ "$STATUS" == "abandoned" ]]; then
  # No tools used, start hook never ran — write minimal meta if missing.
  if [[ ! -f "$META_FILE" ]]; then
    printf '%s\n' "{\"session_id\":\"${SESSION_ID}\",\"ended_at\":\"${TS}\",\"status\":\"abandoned\",\"outcome\":\"${OUTCOME}\"}" \
      > "$META_FILE"
  fi
fi
# STATUS == "in_progress": leave meta and .active-session untouched.
