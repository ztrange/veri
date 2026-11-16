# Published files

What a program outside veri may read, and what it may rely on when it does. Veri publishes two
files; everything else it writes is private (see the end of this page).

| File | Path | Written by | When |
|---|---|---|---|
| The journal | `$VERI_HOME/runs/<owner>-<repo>/<issue>.jsonl` | `event.sh` (`veri/event.py`) | As a run emits each event, one line per event |
| `report-owed.json` (**optional**) | `.tdd/report-owed.json` in the working tree `/vreport` runs in | `report.sh --store-owed` (`veri/prd_report.py`) | When `/vreport` stores a PRD's owed answer |

## The journal

Its path is `$VERI_HOME/runs/<owner>-<repo>/<issue>.jsonl`, `VERI_HOME` defaulting to `~/.veri`.
`<owner>` and `<repo>` are the last two path parts of the `url` of the `origin` remote of the run's
clone, a `.git` suffix dropped (the scp form `git@host:owner/repo.git` names the same path as the
https form), and `<issue>` is the run's issue number. A run with no issue, or whose clone has no
`origin` remote, writes no journal. Every run of an issue appends to the same file, so a resumed
run continues it.

Each line is one JSON object ended by a newline:

- `ts` (epoch seconds) and `awake` (the awake clock's reading) are JSON numbers;
- every other value is a JSON string, empty when unset;
- the common keys `issue`, `actor`, `phase`, `step`, `event`, `attempt` and `skill_commit` follow
  `ts` and `awake`, in that order; then come the event's own keys, in the order its emitter gives
  them.

The events and their keys are those [`JOURNAL.md`](JOURNAL.md) lists.

## `report-owed.json` (optional)

Its path is `.tdd/report-owed.json`, relative to the working tree `/vreport` runs in. It is one JSON
object keyed by PRD number; each entry holds `updatedAt`, the PRD's `updatedAt` when its answer was
computed, and `answer`, the owed work found for that PRD. It is written only when someone runs
`/vreport` and a PRD's stored answer is missing or older than the PRD, so a reader must expect it
to be absent, or old.

## Rules

- **Append-only.** Events and keys are only ever added; none is ever removed or renamed.
- **No schema version.** No line carries one; the append-only rule stands in for it.
- **A reader tolerates.** It ignores an event or a key it does not know, and survives a line that is
  not valid JSON (a line cut short, bytes that are not UTF-8): it skips that line and reads on.

## Private

Everything else veri writes is private and may change, move or vanish without notice:

- `report-cache.json` (`.tdd/report-cache.json`), the PRD report's cache;
- `.tdd/status-last`;
- `conductor.pid`;
- the run worktree's own copy of the events, `.tdd/events.jsonl`, and its path;
- every other file under `.tdd/`.
