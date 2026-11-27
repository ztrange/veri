---
name: voutage
description: >-
  Hold merges through a GitHub incident: read by the dev session, by path, when a merge fails for a reason `vmerge` does not name.
---

# voutage — hold merges through a GitHub outage

Obeys `operator/PRINCIPLES.md` under the clone root of the skill suite this skill belongs to (`git -C <base dir> rev-parse --show-toplevel`); read it first.

`$S` is `skills/tdd/scripts/`, reached from this skill's base directory as `../tdd/scripts/`.
Every command runs from the target repository's main working tree, and every `.tdd/` path is
under it; `$S/github-outage.sh` finds that tree itself from any worktree of the repository.

The dev session reads this skill itself, never through a subagent, since it acts on the
session's own state. It reaches it after `vmerge`'s own handling of the failed merge is over
(its settle read, its one lock release): this skill takes no merge lock and releases none.

Every line below that tells the human or is reported goes as the invoking role speaks: from
the dev session, as one notice, as vdev's *Speaking* says (P4).

## The mode is a file

*Local mode* is the file `.tdd/github-outage`: while it exists, no merge reaches GitHub (a
reviewed run is held, or joined offline where a stack is named); when it is gone, merges go
online again. Re-read it (P1), never remember it, and never edit it by hand: every read
and change is a verb of `$S/github-outage.sh` (its `SCRIPTS.md` entry is the contract), each one
call that works alone. `<driver>` below is `$PPID` in the Bash call, the long-lived process
driving this session, as `vmerge` uses it. An exit 2 of any verb that is not routed below (bad
arguments, no main working tree, a write that failed) is reported to the human once, in one
line, and that procedure stops there.

## On a failed merge

Run `$S/github-outage.sh enter <pr-url>`. It reads GitHub's status page in-process, as
`$S/github-status.sh` does with no component argument (its default components are the ones a
merge needs).

- **Exit 0, `entered`.** A counting incident; the file now holds the status lines and the failed
  PR. Local mode has begun: tell the human (P4) in one
  line, naming the incident from the line printed after `entered`, e.g.
  `Local mode: GitHub incident "<name>" (<age> min); merges held` (`merges held, stacked runs joined offline` where a stack is named). Then arm the wait.
- **Exit 0, `held`.** Local mode was already on; the PR is held again, ahead of the reviewed runs'
  PRs. Nothing is told. Arm the wait.
- **Exit 1, `unexplained`.** GitHub answered and nothing counts; nothing is written. Tell the
  human in one line that the PR's merge failed unexplained, with the `young` lines printed, if
  any.
- **Exit 2, `no answer from GitHub's status page: …`.** Nothing is written, and an existing file
  stays. Tell the human in one line that the status page gave no answer, with the cause printed.
- **Exit 2, `not a PR url: …`.** The url passed was not a PR url; nothing is read or written.
  Report that, once, in one line, naming the url.

## While the file exists

No online merge starts. A run that ends ✅ Done is reviewed as usual; on a review that is OK
(the caveats exchanged as for any merge):

- **Where `$S/stack-branch.sh` exits 0** (the target repository's `CLAUDE.md` names a stack
  branch), join it through `vmerge`'s offline join (its *Joining a stack*), never held: the join
  lands it on the local `<stack>`, gated by the full suite, and pushes nothing.
- **Where it exits 3**, start no merge: run `$S/github-outage.sh hold <pr-url>`, which appends the
  run's PR url to the file on a line of its own: exit 0, held, in the order the runs ended, and
  nothing is told; exit 3, local mode ended meanwhile, so merge it as usual; exit 2, report it
  once.

The file's PR urls, the failed PR's first, are the held merge order. A run whose review is not
OK is handled as without this skill.

## The wait

One wait, `github-status.sh wait 3600`, runs per main working tree, shared by every session on it and detached so it outlives
a reset. **Arm the wait**: run `$S/github-outage.sh wait-start` (exit 0 `started`; exit 3 `live`,
already running, or `off`, local mode ended: then arm nothing), then, unless it printed `off`,
start `$S/github-outage.sh wait` as one background command, as `dispatch.sh` is, never under a
Monitor and never a hand-written script or sleep loop (P3). Nothing is ever killed. `.tdd/stop`
does not end it.

When the background command exits, route what it printed:

- **Exit 0, `ended 0`.** No counting incident is open: leave local mode (below).
- **Exit 0, `ended 3`.** The incident is still open after an hour: arm the wait again. Nothing is
  told.
- **Exit 0, `ended 2`.** No read in that hour got an answer: tell the human in one line, then arm
  the wait again.
- **Exit 0, `ended <any other code>`** (137 is a kill). The wait ended without an answer of its
  own: tell the human in one line, naming the code, then arm the wait again.
- **Exit 2, `none`.** The wait died without an end: arm the wait again.
- **Exit 3, `live`.** Its own time ran out with the wait still running: start the background
  command again.

## Starting, recovering or resuming

A session that starts, recovers from a reset or resumes from a handoff runs
`$S/github-outage.sh status --pid <driver>`: exit 3, nothing to do. Exit 0: it runs no one-shot
check. Each `merging <url> live` line is a PR another live process claimed (after a handoff,
the old session's): tell the human once, in one line, naming the urls, since until that process
settles them or ends, every `take` exits 3 and local mode cannot end. Then it runs
`$S/github-outage.sh adopt --pid <driver>` and merges each url printed (the `mine` and `orphan`
ones: merges this session or a dead one started and never settled) as step 2 below says; then,
while the status says `mode on`, it arms the wait.

## Leaving local mode

Merge the held PRs in the file's order, one at a time, each through `vmerge` as a ✅ Done run is
merged (its review was done before it was held): where a stack is named it is joined offline,
since the file still exists until `take` prints `ended`. Each session merges one PR to completion before
it takes the next, so the order holds per session; two sessions on one tree interleave.

1. Run `$S/github-outage.sh take --pid <driver>`, the claim: no other session gets that PR.
   - A url: go to step 2.
   - `ended`: nothing is left held or merging and the file is removed; tell the human in one line
     that local mode has ended. Then run `$S/github-queue.sh replay`, which lands the issue
     writes runs queued while GitHub was down:
     - Exit 0: the queue drained; say nothing more.
     - Exit 3: there was no queue; say nothing more.
     - Exit 2: an entry got no answer and it and every later one stay queued; tell the human in
       one line, with the entry the replay names on stderr.

     Where `$S/stack-branch.sh` exits 0, land the outage's joins (*Landing the offline joins*,
     below); otherwise stop.
   - Exit 3, nothing printed: another session holds the rest, or the mode ended elsewhere; say
     nothing. Stop.
   - Exit 2: report it once. Stop.
2. Merge that PR through `vmerge`, then settle it with `$S/github-outage.sh settle <pr-url> …`:
   - landed: `merged`; go to step 1.
   - not landed for red CI, a rebase conflict, a refused push or a billing block: handled as
     `vmerge` says, and `released`; go to step 1.
   - not landed for any other cause: run `enter <pr-url>` (*On a failed merge*). Exit 0 holds it
     again and arms the wait: stop. Exit 1: `released`; go to step 1. Exit 2: `failed`, which
     holds it again; arm the wait and stop.

   `settle` exits 3 when the PR was no longer in the merging list (another session adopted it):
   go on as if it had exited 0.

A reset mid-way loses nothing: a PR not yet taken is still held, and one taken and not settled
is adopted by the recovered session.

## Landing the offline joins

The offline joins left their commits on the local `<stack>`, unpushed, and each run's draft PR
open. Once `take` has printed `ended` and the file is gone, run `$S/stack-recover.sh` in the target
repository's main working tree. It pushes each joined run's branch and then the stack, each under
a lease, confirms each run's PR reads merged, deletes the joined runs' remote branches and run
records, and runs `$S/stack-pr.sh`.

- Exit 0: it printed `<tip-sha> <tracking-pr-url>`. Wait for CI on that tip with
  `$S/wait-ci.sh <tracking-pr-url> <slice> <total> <tip-sha>`, called again on exit 3: the url and
  the sha are the two values `stack-recover.sh` printed, and `<slice> <total>` are `540 ""`, as
  `vmerge` waits. When it ends with 0
  (green) or 1 (red), CI has answered: run `$S/stack-red.sh`. Its exit 3 (not red): run
  `$S/stack-land.sh` as vdev's *Landing a slice* says. Its exit 0 (red): go to vdev's *A red
  stack*. Its exit 2, or `wait-ci.sh`'s exit 2, is told to the human in one line. Stop.
- Exit 1 or 2: tell the human in one line each, with its stderr. Stop.
- Exit 3: nothing was joined offline; report nothing. Stop.

The wait comes first because `stack-land.sh` cuts only at a commit CI has tested: run right after
the push, it would exit 3 and say nothing. And it is run here, not left to the next join, because
the queue may be empty and no join would come to run it.
