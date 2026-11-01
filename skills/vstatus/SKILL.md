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

Run `$S/report-cache.sh refresh` once, first, from the main working tree. Exit 2 means no
fresh cache: report that and stop; never build the report from a stale `.tdd/report-cache.json`.
Issue states, labels, blockers (from each issue's `blockedBy`) and wall times are read
from that file (`{fetched_at, issues}`; each issue carries `number`, `title`, `state`, `labels`,
`closedAt`, `updatedAt`, `links`, `blockedBy`, `wallSeconds`, `lane`, and `body` for a PRD only; no issue
carries comments), the same file `/vreport`
reads, never a full `gh issue list`. The other reads stay direct:

- `$S/status.sh --json` — every run: issue, title, step k/n, phase, attempts, elapsed seconds,
  cost, state, PR; and the scope totals (attempted, done, bailed, wall seconds).
- `$S/metrics.sh <n>`, run in `.tdd/wt/<n>` for each running issue — PASS and REJECT counts, the
  `#### By model` table (role, model) and the `#### Total` row. A cost is read from its
  `| total |` row only, never summed from phase rows (P7).
- `git tag --sort=-v:refname --format='%(refname:short) %(creatordate:iso-strict) %(contents:subject)'`
  — the tags cut since the last ask; each tag's message is its capability.
- `gh`, for PRs only — merged PRs since the last ask (`gh pr list --state merged --search
  "merged:>=<time>"`, where `<time>` is the UTC value from `.tdd/status-last`) and open PRs.

Count the reads before making them. **More than three go to one subagent**, on the cheapest
model that can run them, briefed with this list and returning only the figures — one line per
landed PR, per run, per label and per waiting item. Never read a leaf log for this report.

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

**Running** — one block per live run. A run is live when `.tdd/wt/<n>/.tdd/conductor.pid` names a
pid that answers `kill -0` and whose start time matches the one recorded on the lock's second
line, the definition `skills/tdd/SKILL.md` preflight step 1.2 uses. A lock whose pid is dead or
reused is not a running run:

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
