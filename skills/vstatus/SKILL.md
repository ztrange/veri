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

Invoked as `/vstatus`. The report covers what changed since the previous ask, whose time is
kept in `.tdd/status-last` by `status.sh --report`; this skill neither reads nor writes it.

## The reads

Run `$S/status.sh --report` once, from the main working tree, and print its output verbatim.
It is the only read: this skill names no other, and spawns no subagent. Never read a leaf log
for this report.

Issue data comes from the snapshot `status.sh --report` reads, whose age the report's Queue
section prints. This skill itself never runs `report-cache.sh refresh`; a stale snapshot is
`status.sh --report`'s to refresh.

When `status.sh --report` exits 2, report that and stop, printing no figures of your own.

## The report

Four sections, always all four and in this order. An empty one keeps its heading and says
"none".

**Landed** — one line per PR merged since the last ask: PR url, tag, and the capability in the
tag's message.

**Running** — one block per live run, as `status.sh --report`'s **Running** section defines it:
awake wall time, steps k/n, phase, cost and model split. This skill restates no liveness check
of its own.

**Queue** — counts of open opted-in issues by label, the blockers, the **drain ETA** at the
current N, and beside it the **PRD ETA** for each PRD the queue serves.

**Waiting** — PRs ready to merge, empty slots, bails since the last ask with their cause, and
pending human decisions.

## ETAs

Every ETA comes from observed rates and is a range, never a single time. The rate is issues
landed per hour at the current N, taken from the wall time of the runs that finished (status
scope totals, tag dates); the range runs from the fastest to the slowest quartile of those
runs. With fewer than three finished runs to measure, write "no rate yet" instead of an ETA.
