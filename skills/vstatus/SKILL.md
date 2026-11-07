---
name: vstatus
description: >-
  veri's progress since the last ask: `/vstatus`. Use when the user asks how veri's runs are going.
---

# vstatus — progress since the last ask

Alias: `/vstatus`

Obeys `operator/PRINCIPLES.md` under the veri clone root (`git -C <base dir> rev-parse --show-toplevel`); read it first.

`$S` is `skills/tdd/scripts/`, reached from this skill's base directory as `../tdd/scripts/`.
Every read runs against the target repository's main working tree; its CLAUDE.md names the
opt-in label and where PRDs are tracked.

## Since when

Invoked as `/vstatus`. The report covers what changed since the previous ask. Read that
time from `.tdd/status-last` (one UTC ISO 8601 timestamp, ending in `Z`). When the file is
missing, cover the last 24 hours and say so in the report's first line. After the report is
written, overwrite `.tdd/status-last` with the time the reads were taken, in UTC with the
trailing `Z`.

Every figure that can move carries its delta since that time: steps ticked, cost added, PRs
landed, issues added to or taken from the queue.

## The reads

Run `$S/status.sh --report` once, from the main working tree, and print its output verbatim.
It is the only read: this skill names no other, and spawns no subagent. Never read a leaf log
for this report.

Issue data comes from the snapshot `status.sh --report` reads, whose age the report's Queue
section prints. This skill itself never runs `report-cache.sh refresh`; a stale snapshot is
`status.sh --report`'s to refresh.

When `status.sh --report` exits 2, report that and stop, printing no figures of your own.

## The report

Every time the report shows (window start, merge times, launch times, tag dates, ETA clock
times) is in the machine's local zone, and the report's first line names that zone once, e.g.
"06:30 → 11:55 CST (UTC−6)". The sources arrive in different zones and are converted to that
one local zone before they are shown: UTC (`mergedAt`, `fetched_at`, `closedAt`, `updatedAt`),
the tagger's offset (tag `creatordate`) and local (`conductor.pid` lines, `.tdd` mtimes). A
report never shows two zones side by side.

Four sections, always all four and in this order. An empty one keeps its heading and says
"none".

**Landed** — one line per PR merged since the last ask: PR url, tag, and the capability in the
tag's message.

**Running** — one block per live run, as `status.sh --report`'s **Running** section defines it.
This skill restates no liveness check of its own:

- `#<n> — <title>`;
- **awake wall time**: elapsed time since launch, less any time the machine slept. No helper
  computes this yet: until one exists, subtract the sleep intervals `pmset -g log` shows over
  the run's window on a Mac, and elsewhere report the elapsed time labelled as wall time;
- **steps** k/n ticked/planned, with the delta since the last ask;
- **phase** now, and **attempts** in it;
- **PASS / REJECT** counts so far;
- **cost**: the `| total |` row, with the delta since the last ask;
- **model split**: the model each role ran on — developer, revise, verifier, conductor — from
  the `#### By model` table.

Close the section with the model split per role across all running runs.

**Queue** — counts of open opted-in issues by label; the blockers (each opted-in issue
`$S/solvable-issues.sh` leaves out, with the open issue that blocks it); the **drain ETA** at
the current N; and beside it the **PRD ETA** for each PRD the queue serves — its open children
at the same rate.

**Waiting** — PRs ready to merge (last comment ✅ Done, not merged); empty slots (N minus live
conductors, N as the dev session last stated it); bails since the last ask, each with its cause;
and pending human decisions, each restated in full (P4).

## ETAs

Every ETA comes from observed rates and is a range, never a single time. The rate is issues
landed per hour at the current N, taken from the wall time of the runs that finished (status
scope totals, tag dates); the range runs from the fastest to the slowest quartile of those
runs. With fewer than three finished runs to measure, write "no rate yet" instead of an ETA.
