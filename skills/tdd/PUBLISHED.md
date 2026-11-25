# Published files

What a program outside veri may read, and what it may rely on when it does. Veri publishes three
files; everything else it writes is private (see the end of this page). All three stay on the machine
that ran veri: veri commits and pushes none of them.

| File | Path | Written by | When |
|---|---|---|---|
| The journal | `$VERI_HOME/runs/<owner>-<repo>/<issue>.jsonl` | `event.sh` (`veri/event.py`) | As an event is written whose line carries an issue: one line per such event (see which events never do, below) |
| The metrics file | `$VERI_HOME/runs/<owner>-<repo>/<issue>.metrics.json`, beside the issue's journal | `event.sh` (`veri/event.py`) | After an `exit`, `step-done`, `bail`, `done` or `stage-end` event of that issue reaches the journal: the whole file rewritten |
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
half of it), and only after an `exit`, `step-done`, `bail`, `done` or `stage-end` event of that issue reaches the
journal; every other event leaves it as it is. It may therefore be one phase behind the journal. A
missing file means no such event of the issue has been written yet. A failure to compute or write it
is one line on `event.sh`'s stderr and never stops a run: the event is written and the run goes on.

Every figure in it is a count or a sum, and none is a rate: rates over many issues are the reader's,
since counts add up across files and rates do not. `null` means not known, and is never zero: a reader
that sums skips it rather than adding nothing. Its keys are those below; keys are only ever added,
never removed or renamed, and the file carries no version key. A reader ignores a key it does not know.

A `REJECT` verdict's outcome is read off the journal's later lines, pairing it with the first later
`PASS` verdict of the same step and phase, across resumes and restarts; a `malformed` verdict is
neither. It has exactly one of six outcomes:

- **caught**: a later PASS of the same step and phase judged a different tree, so the work changed
  before it passed.
- **flipped**: that PASS judged the same tree, so the verifier changed its mind and nothing was fixed.
- **overturned**: a `revise-impossible` bail of that step came first, before any such PASS.
- **unresolved**: no later PASS, and a bail after it.
- **pending**: no later PASS and no bail: the run may still be going.
- **untracked**: the PASS or the REJECT carries no tree, as every line written before the tree was
  recorded does, so a catch cannot be told from a flip.

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
| `runs` | list of objects, one per run of the issue, in journal order. A run ends at a `done`, `bail` or `stop` line and the next line opens the next run, so a conductor restart with no ending line before it continues the run it is in | no |
| `runs[].index` | whole number, the run's place in the list, from 1 | no |
| `runs[].ended` | string, the event of the line that ended the run: `done`, `bail` or `stop` | yes, while the run is open (no ending line yet) |
| `runs[].cause` | string, the `bail`'s cause | yes, unless a `bail` ended the run and names a cause |
| `runs[].wall_seconds` | whole number, from the run's first line to its ending line | yes, while the run is open |
| `runs[].awake_seconds` | whole number, the awake clock's reading at the ending line less the first line's | yes, while the run is open, or when either line lacks the reading |
| `runs[].sessions` | whole number, the run's `conductor-start` lines | no |
| `runs[].leaves` | whole number, the run's `launch` lines that name a phase; summed over `runs` it equals `attempts` summed over `leaves` | no |
| `runs[].cost_usd` | number, dollars: the run's `usage` lines that name a phase, summed; summed over `runs` it equals `cost_usd` summed over `leaves`. The conductor's own spend is not split per run | no |
| `stages` | object keyed by stage name, one entry per stage (a non-leaf phase of a run, such as `preflight` or `baseline`) the journal marks with `stage-start` or `stage-end` lines; `{}` when it marks none. A stage absent from it was not recorded (veri did not mark it then), never a stage that ran zero times | no |
| `stages.<stage>` | object, one stage's figures | no |
| `stages.<stage>.runs` | whole number, the stage's `stage-start` lines | no |
| `stages.<stage>.ok` | whole number, its `stage-end` lines with `status` 0 (passed) | no |
| `stages.<stage>.failed` | whole number, its `stage-end` lines with `status` 1 (failed: a clean negative) | no |
| `stages.<stage>.no_answer` | whole number, its `stage-end` lines with `status` 2 (no answer could be obtained), or with any status outside 0 to 3 | no |
| `stages.<stage>.nothing` | whole number, its `stage-end` lines with `status` 3 (nothing to do, or still waiting) | no |
| `stages.<stage>.unended` | whole number, its starts with no `stage-end` of that stage before its next start or the journal's end: a stage killed before it could end, never counted as passed | no |
| `stages.<stage>.wall_seconds` | whole number, its `stage-end` lines' `secs` summed | no |
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
| `phases.<phase>.rejects` | object, what the phase's `REJECT` verdicts led to: one count per outcome below, each a number and never `null`, `0` when none, the six summing to the entry's `reject` | no |
| `phases.<phase>.rejects.caught` | whole number, the phase's REJECTs that were caught | no |
| `phases.<phase>.rejects.flipped` | whole number, the phase's REJECTs that were flipped | no |
| `phases.<phase>.rejects.overturned` | whole number, the phase's REJECTs that were overturned | no |
| `phases.<phase>.rejects.unresolved` | whole number, the phase's REJECTs that were unresolved | no |
| `phases.<phase>.rejects.pending` | whole number, the phase's REJECTs that were pending | no |
| `phases.<phase>.rejects.untracked` | whole number, the phase's REJECTs that were untracked | no |
| `leaves` | object keyed by leaf kind: the name a leaf was launched under less a trailing `-<digits>` (`revise-green-2` is `revise-green`), or `unnamed`; the figures of a `phases` entry less `verified_steps`, `first_try_pass` and `revise_cycles` (those three are counted per phase only), split by leaf instead of by phase, so each figure summed over `leaves` equals its sum over `phases` | no |
| `leaves.<kind>` | object, one leaf kind's figures. A line naming its leaf counts under that name's kind; a line written before leaves were named counts under the kind of the `launch` with its step, phase, attempt and actor, and under `unnamed` when no `launch` has them | no |
| `leaves.<kind>.attempts` | whole number, leaves launched | no |
| `leaves.<kind>.pass` | whole number, `PASS` verdicts | no |
| `leaves.<kind>.reject` | whole number, `REJECT` verdicts | no |
| `leaves.<kind>.kills` | whole number, leaves that exited 2 | no |
| `leaves.<kind>.wall_seconds` | whole number, the leaves' seconds summed | no |
| `leaves.<kind>.api_seconds` | whole number, the leaves' API seconds summed | no |
| `leaves.<kind>.turns` | whole number | no |
| `leaves.<kind>.input_tokens` | whole number | no |
| `leaves.<kind>.output_tokens` | whole number | no |
| `leaves.<kind>.cache_read_input_tokens` | whole number | no |
| `leaves.<kind>.cache_creation_input_tokens` | whole number | no |
| `leaves.<kind>.cost_usd` | number, dollars | no |
| `steps` | list of objects, one per ledger step a leaf ran for, in the order `metrics.sh`'s By step table lists them | no |
| `steps[].text` | string, the step's latest ledger text: a step a plan rewrite reworded (`step-reworded` lines, followed through chained rewordings) is one entry, every line naming any of its texts counted in it; two steps reworded to one text are one entry from then on, holding both steps' lines; a step reworded outside the ledger rewrite (a hand edit of the ledger) writes no such line and shows as a new step | no |
| `steps[].former` | list of strings, the step's earlier texts in the order it carried them (for two steps reworded to one text, the first's then the second's), `[]` when it was never reworded | no |
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
| `steps[].rejects` | object, the same six counts as a phase entry's `rejects`, over the step's `REJECT` verdicts, summing to the step's `reject` | no |
| `steps[].rejects.caught` | whole number, the step's REJECTs that were caught | no |
| `steps[].rejects.flipped` | whole number, the step's REJECTs that were flipped | no |
| `steps[].rejects.overturned` | whole number, the step's REJECTs that were overturned | no |
| `steps[].rejects.unresolved` | whole number, the step's REJECTs that were unresolved | no |
| `steps[].rejects.pending` | whole number, the step's REJECTs that were pending | no |
| `steps[].rejects.untracked` | whole number, the step's REJECTs that were untracked | no |
| `conductor` | object: the conductor's own spending | no |
| `conductor.cost_usd` | number, dollars over its priced sessions | yes, when no session was read or none carries a price |
| `conductor.turns` | whole number, each session's turns summed: for a session its closing record ends, the more of the turns that record counts and the turns the log shows; for one with no closing record (killed before it, or still going), the turns the log shows | yes, when no session was read |
| `conductor.sessions` | whole number, the sessions read: a session ends at its closing record, or at the next session's start when it has none | no |
| `conductor.model` | string, the conductor's model | yes, when none was recorded |
| `conductor.estimated` | boolean, `true` when a session has no closing record (killed before it, or still going), its cost then priced from its own turns' usage | no |
| `conductor.priced` | `true` when every session carries a price, `false` when none does, the string `"partial"` otherwise | no |
| `conductor.by_phase` | object keyed by window: a leaf kind (a leaf's `launch` to its `exit`), a stage (its `stage-start` to its `stage-end`), `between` (a timed turn no such window holds) or `untimed` (a turn whose record carries no time, or that the session's closing record counts and no record shows); each turn of the conductor's stream log counted once, under the innermost leaf or stage window holding its time, so its `turns` sum to `conductor.turns`. A window with no end holds no turn | yes, when no conductor log was read |
| `conductor.by_phase.<window>` | object, the conductor's turns in that window | no |
| `conductor.by_phase.<window>.turns` | whole number | no |
| `conductor.by_phase.<window>.output_tokens` | whole number, the turns' output tokens: a closed session's output split evenly over its turns | no |
| `conductor.by_phase.<window>.cost_usd` | number, dollars: an estimate from each turn's own usage and a share of its session's cost, not a billed amount | yes, when a turn of the window belongs to a session that carries no price |
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
