# Claude Code — Concepts & Reference

Notes on Claude Code's behaviour, built up from docs research and most importantly, testing and verification.

---

## Session

A **session** is the continuous conversation context identified by a single `session_id` UUID. It begins when you launch (or resume) Claude Code and ends when you exit.

Key properties:

- Persists across many **[turns](#turn)** — each user message + assistant response is one turn inside the session
- Can be **resumed** — the same `session_id` continues, with the same transcript
- Can be **compacted** — the transcript is summarised, but the session carries on
- The `session_id` is stable for the entire lifetime of the conversation

---

## Turn

A **turn** is one complete request-response cycle within a session: the user submits a message, Claude thinks, uses tools, and finishes.

| Hook | Fires when |
|---|---|
| `UserPromptSubmit` | A turn begins (user submits a message); carries the prompt text |
| `Stop` | A turn ends (Claude finishes responding); carries `stop_reason` |

A [session](#session) contains many turns. `Stop` firing does not mean the session has ended.

---

## Claude Code Native Storage

Claude Code stores session data in two locations used as the source of truth for observability.

### Project

A **project** is a working directory. `~/.claude/projects/` has one subdirectory per unique `cwd`, named by encoding the path with `/` replaced by `-`. All sessions started from that directory live inside it.

```
~/.claude/projects/
└── -{absolute}-{pathto}-{project}/       ← e.g.: /Users/pereid22/rose
    ├── {session_id}.jsonl
    └── {session_id}.jsonl
```

### Transcript

A **transcript** is the full record of a session's conversation. Every entry in a **project** (see above) (e.g.: user messages, assistant responses, tool calls, tool results, system prompts) is appended as a JSON line to `{session_id}.jsonl`. Claude Code replays this file when resuming a session.

### `~/.claude/sessions/{pid}.json`

One file per running Claude Code process:

```json
{
  "pid":       71823,
  "sessionId": "dedd37bc-...",
  "cwd":       "/Users/pereid22/rose",
  "startedAt": 1775477968105
}
```

**Critical:** `sessionId` here is the **process identity**, not the transcript filename. On a fresh session they match. On a resume they diverge — the process gets a new `sessionId` (`dedd37bc`) but continues appending to the original transcript (`78b85df3.jsonl`).

```
Fresh session:
  sessions/12345.json  →  sessionId: 78b85df3
  projects/.../78b85df3.jsonl  ← created, entries have sessionId: 78b85df3  ✓ match

Resume:
  sessions/71823.json  →  sessionId: dedd37bc  (new process ID)
  projects/.../78b85df3.jsonl  ← still being written to, entries still have sessionId: 78b85df3  ✗ no match
  projects/.../dedd37bc.jsonl  ← never created
```

#### Mapping a live process to its transcript

`sessionId` in `sessions/{pid}.json` cannot be used to find the transcript on resume. Instead, use `cwd` + `startedAt`:

1. Encode `cwd` → project directory name
2. Find the `.jsonl` in that directory with `mtime >= startedAt / 1000`
3. That is the transcript being actively written to

This works because only one transcript per project can be modified after the process started.

### `~/.claude/projects/{encoded-cwd}/{session_id}.jsonl`

Full conversation transcript for each session, scoped to the working directory. The directory name is the cwd with `/` replaced by `-` (e.g. `/Users/pereid22/rose` → `-Users-pereid22-rose`). This is what `/resume` reads.

Each line is a JSON object. The two relevant entry types are `user` and `assistant`. Tool results are also `user` type (with `message.content` as an array). The fields we care about:

```json
{
  "type": "user",
  "sessionId": "8ac36fae-...",
  "timestamp": "2026-04-06T02:41:49.059Z",
  "gitBranch": "main",
  "cwd": "/Users/pereid22/rose",
  "message": {
    "role": "user",
    "content": "there are hooks in global/hooks that I no longer require"
  }
}
```

```json
{
  "type": "assistant",
  "timestamp": "2026-04-06T02:41:52.000Z",
  "message": {
    "role": "assistant",
    "stop_reason": "end_turn",
    "content": [
      { "type": "text", "text": "Which hooks would you like removed?" }
    ]
  }
}
```

Key fields for `observe.py --list`:

| Field | Where |
|---|---|
| `title` | `message.content` of first `user` entry where content is a plain string |
| `branch` | `gitBranch` of first `user` entry |
| `started_at` | `timestamp` of first entry in the file |
| `ended_at` | `timestamp` of last entry in the file (or file mtime) |

---

## Log Structure

This is a **custom rose logging system** — Claude Code has no built-in event logging. Everything here is written by hook scripts installed by `rose install`.

Session metadata (status, start time, title, branch) comes entirely from Claude Code's native storage — no session-level log file needed. Rose only logs agent activity.

```
~/.claude/logs/
└── {session_id}/
    ├── rose/
    │   └── events.jsonl
    ├── rose-backlog/
    │   └── events.jsonl
    └── rose-research/
        └── events.jsonl
```

Agent subdirectories are created when a subagent starts.

### `{session_id}/{agent}/events.jsonl`

Turns, tool calls, and workflow steps for a specific agent:

| Event | Hook | When |
|---|---|---|
| `turn.start` | `UserPromptSubmit` | User submits a message |
| `turn.end` | `Stop` | Claude finishes responding |
| `tool.call` | `PostToolUse` | After a tool succeeds |
| `tool.error` | `PostToolUseFailure` | After a tool fails |
| `step.enter` | manual | Agent enters a workflow step |
| `step.exit` | manual | Agent exits a workflow step |

### Event envelope

```json
{
  "seq":     1,
  "ts":      "2026-04-06T03:02:05.000Z",
  "event":   "turn.start | turn.end | tool.call | tool.error | step.enter | step.exit",
  "payload": {}
}
```

`seq` is monotonically increasing within each `events.jsonl` file independently.

---

## `observe.py --list`

Modelled after the `/resume` picker. Reads from Claude Code's native storage — no custom state needed.

### Data sources

| Field | Source |
|---|---|
| `session_id` | filename of `~/.claude/projects/{cwd}/{session_id}.jsonl` |
| `status` | `~/.claude/sessions/` — live if session_id present with running pid |
| `started_at` | `startedAt` from `~/.claude/sessions/{pid}.json` (if live), else first `timestamp` in transcript |
| `ended_at` | `mtime` of the transcript `.jsonl` file |
| `branch` | first `gitBranch` field found in transcript |
| `title` | first user message text in transcript |

### Display

Sessions sorted most-recent first. `started_at` is the most recent session start (i.e. last resume time, not original creation).

**Live** (pid running):
```
  78b85df3  live     06-APR-2026 04:02:01  →  …                     ⎇ main   testing logs
```

**Done** (not in sessions dir):
```
  78b85df3  done     06-APR-2026 04:02:01  →  07-APR-2026 05:15:42  ⎇ main   testing logs
```

**Unknown** (in sessions dir but pid dead — likely crashed):
```
  78b85df3  unknown  06-APR-2026 04:02:01  →  …                     ⎇ main   testing logs
```

Fields: `session_id` · `status` · `started_at` · `→` · `ended_at` · `⎇ branch` · `title`
