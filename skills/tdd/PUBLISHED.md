# Published files

What a program outside veri may read, and what it may rely on when it does. Veri publishes three
files; everything else it writes is private (see the end of this page). All three stay on the machine
that ran veri: veri commits and pushes none of them.

| File | Path | Written by | When |
|---|---|---|---|
| The journal | `$VERI_HOME/runs/<owner>-<repo>/<issue>.jsonl` | `event.sh` (`veri/event.py`) | As an event is written whose line carries an issue: one line per such event (see which events never do, below) |
| The metrics file | `$VERI_HOME/runs/<owner>-<repo>/<issue>.metrics.json`, beside the issue's journal | `event.sh` (`veri/event.py`) | After an `exit`, `step-done`, `bail` or `done` event of that issue reaches the journal: the whole file rewritten |
| `report-owed.json` (**optional**) | `.tdd/report-owed.json` in the main working tree, whichever directory `/vreport` runs in | `report.sh --store-owed` (`veri/prd_report.py`) | When `/vreport` stores a PRD's owed answer |

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

Each key has a format, stated in [`JOURNAL.md`](JOURNAL.md) after the key's name, that says how to
read its value (a whole number, a URL, a sha, one of a list of values, …) and whether it may be
empty.

The events and their keys are those `JOURNAL.md` lists, but the journal holds only the
lines whose writer gave them an issue: a line is appended to the journal of the issue in its own
`issue` key, and a line with an empty `issue` goes only to the worktree's private event log,
`.tdd/events.jsonl`. A writer that runs inside a run takes the issue from `VERI_ISSUE`, so its lines
reach the journal when that is set.

### Events that never reach the journal

These writers give their lines no issue (or write the line themselves), so today these events are
only ever in the worktree's event log, never in the journal:

- `comment` (`comment.sh`)
- `diff-leaf-deviation` (`diff-leaf-deviation.sh`)
- `grading` (`grade-prose.sh`)
- `pin-retired` (`pin-recheck.sh`)
- `prose-owed-waived` (`prose-owed.sh`)
- `rebase-refresh-retry` (`queued-merge.sh`)
- `suite-flake` (`rerun-alone.sh` and `suite-red-resume.sh flake`)
- `step-added` as `add-ledger-step.sh` writes it, one line per inserted step; the conductor's own
  `step-added` mark, written through `event.sh` with `VERI_ISSUE` set, does reach the journal.

## The metrics file

Its path is `<issue>.metrics.json` beside the issue's journal,
`$VERI_HOME/runs/<owner>-<repo>/<issue>.metrics.json`, resolved as the journal's path is: a run that
writes no journal (no issue, or no `origin` remote) writes no metrics file either.

It holds the object `metrics.sh <issue> --json` builds, folded from the whole journal, so it covers
every run of the issue, a resumed one and one made in another worktree included. `event.sh` rewrites
the whole file at once (a temporary file in the same directory renamed over it, so a reader never sees
half of it), and only after an `exit`, `step-done`, `bail` or `done` event of that issue reaches the
journal; every other event leaves it as it is. It may therefore be one phase behind the journal. A
missing file means no such event of the issue has been written yet. A failure to compute or write it
is one line on `event.sh`'s stderr and never stops a run: the event is written and the run goes on.

Every figure in it is a count or a sum, and none is a rate: rates over many issues are the reader's,
since counts add up across files and rates do not. `null` means not known, and is never zero: a reader
that sums skips it rather than adding nothing. Its keys are those below; keys are only ever added,
never removed or renamed, and the file carries no version key. A reader ignores a key it does not know.

| Key | Type | May be `null` |
|---|---|---|
| `run` | object: the run as a whole | no |
| `run.issue` | string, the issue number | no |
| `run.outcome` | string: `running`, `landed`, `stopped`, `bailed`, `usage-limit`, `killed` or `unknown` | yes, when how the run ended cannot be told |
| `run.wall_seconds` | whole number, the issue's wall time as the `done` mark states it | yes, until the run writes `done` |
| `run.awake_seconds` | whole number, the part of that time the machine was awake | yes, until the run writes `done` |
| `run.bails` | list of objects, one per `bail` event, in journal order | no |
| `run.bails[].cause` | string, the bail's cause | yes, when the event lacks it |
| `run.bails[].classification` | string, `process` or `system` | yes, when the event lacks it |
| `run.bails[].phase` | string, empty when the bail named no phase | yes, when the event lacks it |
| `run.bails[].step` | string, the ledger step's text, empty when none | yes, when the event lacks it |
| `phases` | object keyed by phase name, one entry per phase a leaf was launched for | no |
| `phases.<phase>` | object, one phase's figures | no |
| `phases.<phase>.attempts` | whole number, leaves launched | no |
| `phases.<phase>.pass` | whole number, `PASS` verdicts | no |
| `phases.<phase>.reject` | whole number, `REJECT` verdicts | no |
| `phases.<phase>.kills` | whole number, leaves that exited 2 | no |
| `phases.<phase>.wall_seconds` | whole number, the leaves' seconds summed | no |
| `phases.<phase>.api_seconds` | whole number, the leaves' API seconds summed | no |
| `phases.<phase>.turns` | whole number | no |
| `phases.<phase>.input_tokens` | whole number | no |
| `phases.<phase>.output_tokens` | whole number | no |
| `phases.<phase>.cache_read_input_tokens` | whole number | no |
| `phases.<phase>.cache_creation_input_tokens` | whole number | no |
| `phases.<phase>.cost_usd` | number, dollars | no |
| `phases.<phase>.verified_steps` | whole number, the steps with a `PASS` or `REJECT` verdict of the phase, `0` when none | no |
| `phases.<phase>.first_try_pass` | whole number, those steps whose first such verdict was `PASS`, `0` when none | no |
| `phases.<phase>.revise_cycles` | whole number, the phase's `revise` events, `0` when none; on a journal written before `revise` was recorded, `0` is the event's absence, not a run that needed no revise | no |
| `steps` | list of objects, one per ledger step a leaf ran for, in the order `metrics.sh`'s By step table lists them | no |
| `steps[].text` | string, the step's ledger text | no |
| `steps[].attempts` | whole number | no |
| `steps[].pass` | whole number | no |
| `steps[].reject` | whole number | no |
| `steps[].kills` | whole number | no |
| `steps[].retries` | whole number, leaves the supervisor relaunched | no |
| `steps[].no_verdict` | whole number, verifiers relaunched for giving no verdict | no |
| `steps[].wall_seconds` | whole number, from the step's `step-start` to its `step-done` | yes, until the step has both |
| `steps[].api_seconds` | whole number | no |
| `steps[].turns` | whole number | no |
| `steps[].input_tokens` | whole number | no |
| `steps[].output_tokens` | whole number | no |
| `steps[].cache_read_input_tokens` | whole number | no |
| `steps[].cache_creation_input_tokens` | whole number | no |
| `steps[].cost_usd` | number, dollars | no |
| `conductor` | object: the conductor's own spending | no |
| `conductor.cost_usd` | number, dollars over its priced sessions | yes, when no session was read or none carries a price |
| `conductor.turns` | whole number | yes, when no session was read |
| `conductor.sessions` | whole number, the sessions read | no |
| `conductor.model` | string, the conductor's model | yes, when none was recorded |
| `conductor.estimated` | boolean, `true` when a session has no closing record yet | no |
| `conductor.priced` | `true` when every session carries a price, `false` when none does, the string `"partial"` otherwise | no |
| `total` | object: the run's whole spend | no |
| `total.turns` | whole number | no |
| `total.input_tokens` | whole number | no |
| `total.output_tokens` | whole number | no |
| `total.cache_read_input_tokens` | whole number | no |
| `total.cache_creation_input_tokens` | whole number | no |
| `total.cost_usd` | number, dollars | no |
| `total.includes_conductor` | boolean, `true` when the conductor's spend is in the total's figures | no |

## `report-owed.json` (optional)

Its path is `.tdd/report-owed.json` in the main working tree, whichever directory or linked worktree
`/vreport` runs in. Only `report.sh --store-owed`, run by `/vreport`, writes it, and it replaces the
whole file at once (a temporary file renamed over it), so a reader never sees half of it.

It is one JSON object keyed by PRD number; each entry holds `updatedAt`, the PRD issue's `updatedAt`
when its answer was computed, `answer`, the owed work found for that PRD (`count`, a whole number of
0 or more, and `sections`, a list of strings), and `computedAt`, the UTC time the answer was computed
and stored. An entry written before `computedAt` existed lacks it.

```json
{
  "014": {
    "updatedAt": "2026-11-02T10:00:00Z",
    "answer": {"count": 2, "sections": ["Alpha section", "Beta section"]},
    "computedAt": "2026-11-07T10:00:00Z"
  }
}
```

It is written only when someone runs `/vreport`, so a reader must expect it to be absent or old. A
missing file means no answer is stored yet. An entry is current only while its `updatedAt` equals the
PRD issue's `updatedAt` on GitHub; otherwise it is stale: the PRD changed after its answer was
computed.

## Rules

- **Append-only.** Events and keys are only ever added; none is ever removed or renamed. A key whose
  format is a list of values may gain values the same way.
- **No schema version.** No line carries one; the append-only rule stands in for it.
- **A reader tolerates.** It ignores an event or a key it does not know, and treats a value it does
  not know (one its key's list does not hold yet) as it treats a key it does not know. It survives
  a line that is not valid JSON (a line cut short, bytes that are not UTF-8): it skips that line and
  reads on.

## Private

Everything else veri writes is private and may change, move or vanish without notice:

- `report-cache.json` (`.tdd/report-cache.json`), the PRD report's cache;
- `.tdd/status-last`;
- `conductor.pid`;
- the run worktree's own copy of the events, `.tdd/events.jsonl`, and its path;
- every other file under `.tdd/`.
