# Telemetry (planned, not yet enabled)

Nothing in v1.0 phones home. Every module runs entirely client-side. This document specifies the schema a future opt-in telemetry layer would use, so it can be reviewed before any data is collected.

## Design constraints

1. **Zero PII.** No names, emails, accounts, IP logging, or device fingerprints. No cookies. An anonymous random session ID is generated per visit and never persisted across visits.
2. **Deterministic and auditable.** Every event type is enumerated below; the client sends nothing outside this schema.
3. **Dual purpose.** The same aggregate data serves (a) program evaluation for AR INBRE / ODSS reporting (plays, completion, quiz pass rates by module) and (b) a student data-science exercise: interns analyze the arcade's own gameplay data (reaction times, error patterns, learning curves) as a real, ethically clean dataset they helped generate.

## Event schema (JSON lines)

```json
{
  "v": 1,
  "sid": "<random per-visit id, not persisted>",
  "module": "ribosome-snake",
  "event": "quiz_submit",
  "t_ms": 412345,
  "payload": { "score": 5, "pass": true, "attempt": 1 }
}
```

| event          | payload fields                                   | teaches us |
|----------------|--------------------------------------------------|------------|
| `module_open`  | `referrer_page` (hub / direct)                   | reach      |
| `flashcard_done` | `read_ms`                                      | whether the Learn step is read or skipped |
| `game_start`   | —                                                | conversion from flashcard |
| `game_error`   | `kind` (e.g. wrong_pair, misfold, out_of_window), `t_ms` | which concepts are hard; error curves over attempts |
| `game_win` / `game_loss` | `duration_ms`, `errors`, `attempt`     | difficulty calibration |
| `quiz_q`       | `q_index`, `correct`, `latency_ms`               | item-level difficulty |
| `quiz_submit`  | `score`, `pass`, `attempt`                       | learning outcome |

## What is deliberately NOT collected

Geolocation, user agent beyond coarse `mobile|desktop`, timestamps finer than the session-relative clock, free-text input (there is none), anything typed by the user.

## Storage options (undecided)

- Static: POST to a simple collector (e.g., a Cloudflare Worker / institutional endpoint) appending JSON lines.
- Interim, zero-infrastructure: aggregate page counting only (Plausible/GoatCounter class, cookieless).

Any activation of this layer should be reviewed against UAMS policy and noted in the README changelog.
