---
name: veri-dev
description: >-
  Run the veri dev session: keep N detached conductors running over the solvable issues, one
  issue each, refill a slot on every exit, and route each exit by fact — merge or report a
  finished run, triage a bail, check a silent exit. Invoke as
  `/veri-dev [N] [--afk] [--resume <file>]`. Use when the user wants veri to work through its
  queue, keep N runs going, or resumes a dev-session handoff.
---

# veri-dev — the dev session

Alias: `/vdev`

Obeys `../veri-ops/PRINCIPLES.md`; read it first.

`$S` is `skills/tdd/scripts/`, reached from this skill's base directory as `../tdd/scripts/`.
Every command runs from the target repository's main working tree, and every `.tdd/` path is
under it. The target repo's CLAUDE.md supplies the project specifics.

## Starting

Invoked as `/veri-dev [N] [--afk] [--resume <file>]`.

- **N** is how many conductors to keep running; it defaults to 1.
- **`--afk`** grants merge permission for the runs this session finishes, and for nothing else.
  Without it, a finished run is reported, never merged.
- **`--resume <file>`** reads a handoff for state only (live conductors, parked runs, PRs
  awaiting merge, N and any timed change, overrides and permissions with their expiry); the
  rules are this skill's. Re-read that state live before the first slot decision.

## Live conductors and the slot decision

A conductor is **live** when `.tdd/wt/<n>/.tdd/conductor.pid` exists and its pid answers
`kill -0`. Count them fresh at every slot decision (P1); `$S/status.sh --json` gives the same
runs with their step k/n and phase.

**The slot decision**, taken at the start and again after every merge, every park and every
conductor exit:

1. Apply any change the coordinator sent since the last decision — a new N (including a timed
   one now due or expired) or an order override — and reply `ack` to it.
2. Count live conductors. While fewer than N are live, launch the next issue (below). When N
   went down, stop nothing: a live run finishes, and its slot is simply not refilled (P8).
3. When `$S/solvable-issues.sh` exits 3 and no run is live, the queue is empty: say so and stop.

Keep exactly N conductors running for as long as the solvable list is non-empty.

## Launching

The next issue is the first line of `$S/solvable-issues.sh` with no live conductor, unless the
coordinator gave an override (P9). Launch it detached, never as a conductor inside this
session:

```bash
$S/detach-leaf.sh $S/run-conductor.sh <n> > .tdd/conductor-<n>.out 2>&1 < /dev/null
```

Announce it as `Started #<n> — <title>`, the title read from `gh issue view <n> --json title`.

Launch the next issue only once the previous launch's ledger exists: wait for
`.tdd/wt/<prev>/.tdd/issue-<prev>.md` with a Monitor on
`until [ -f .tdd/wt/<prev>/.tdd/issue-<prev>.md ]; do sleep 15; done; echo ledger <prev>`
(a script that blocks, P3). Until that file exists the issue is not yet claimed, and
`solvable-issues.sh` would hand it out again.

## Watching

Wait on the blocking watch of P3. `watch-runs.sh` does not exist yet: until it does, use a
Monitor on a script that blocks and prints one line per conductor exit, conductor start or
merge to the default branch. A start you launched yourself and already announced gets no text;
re-arm silently.

## Routing an exit

On each conductor exit, read the facts — the issue's last comment
(`gh issue view <n> --json comments`), the committed ledger, the PR — never the exit code
alone, and route:

- **Last comment ✅ Done.** Under `--afk`, merge it through `veri-merge`. Without `--afk`,
  report one line, `ready to merge #<n> — <title>`, with the PR url, and do not merge.
  `veri-merge` does not exist yet: until it does, merge under `--afk` with the installed
  `merge` skill, and only when the ledger has no unchecked step (`$S/next-unchecked.sh <
  .tdd/wt/<n>/.tdd/issue-<n>.md` exits 3) and no `⟂ refactor pending` mark
  (`$S/next-pending-refactor.sh` on the same file exits 3); otherwise report it as not ready.
  A run that ended with an open question for the human is never merged.
- **Last comment is a bail.** Hand it to `veri-bail <n>`. `veri-bail` does not exist yet: until
  it does, classify the cause with `$S/classify-bail.sh <cause>`, resume a first bail once with
  `$S/run-conductor.sh <n>` launched as above (with `VERI_NEW_SKILL=1` when the fix it needs
  landed after its launch), and park a second one: one issue comment with the cause and what
  would unblock it. Budget raises come only from the coordinator or the human.
- **No closing comment.** Check for a usage limit or sleep first (P10). Either one is not a
  bail: resume the run once usage is back. Neither one: route it as a bail.

Then take the slot decision.

## When to stop and ask

Stop and ask the human only for: red CI you cannot fix, a ⟦human-owed⟧ step, a conflict you
cannot resolve, or a decision a ledger step asks for. Each is stated in full (P4). Everything
else you decide and keep going; a turn never ends while a slot can be filled (P5).

## Out of scope

You do not file, groom or reprioritise issues — that is the coordinator's job. You do not edit
veri's scripts or skills: a veri fault is reported to the coordinator as facts, and becomes an
issue there.

## Requirements

| ID | Requirement | Why |
|---|---|---|
| D1 | Invoked as `/veri-dev [N] [--afk] [--resume <file>]`. N defaults to 1, and `--afk` grants merge permission for what this session finishes. | |
| D2 | It keeps exactly N conductors running while the solvable list is non-empty. | Idle slots were the recurring waste. |
| D3 | Each conductor is a detached `run-conductor.sh <n>`, never a conductor run inline. | An inline conductor costs ~60k tokens per issue in the session. |
| D4 | It launches the next issue only after the previous launch's ledger exists. | A claim appears only ~10 minutes into a run. |
| D5 | On each exit it routes by fact: ✅ Done → `veri-merge` under `--afk`, else "ready to merge #N"; a bail → `veri-bail`; no closing comment → P10. | |
| D6 | After every merge, park or exit it recounts and refills to N. | |
| D7 | It applies the coordinator's changes to N or to the order at the next slot decision. | |
| D8 | It stops and asks only for: red CI it cannot fix, a ⟦human-owed⟧ step, an unresolvable conflict, a decision a ledger step asks for. | |
| D9 | It does not file, groom or reprioritise issues, and does not edit veri's scripts. | Those are the coordinator's job, and a veri fix is an issue for veri. |

This unit is **ungraded**: nothing has signed it yet. #1725 grades this prose against the
table above, and #1726 records the signature.
