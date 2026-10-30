---
name: veri-dev
description: >-
  The veri dev session, reached by name: `/veri-dev [<lane>] [N] [--resume <file>]`, or `/vdev`.
---

# veri-dev — the dev session

Alias: `/vdev`

Obeys `operator/PRINCIPLES.md` under the veri clone root (`git -C <base dir> rev-parse --show-toplevel`); read it first.

`$S` is `skills/tdd/scripts/`, reached from this skill's base directory as `../tdd/scripts/`.
Every command runs from the target repository's main working tree, and every `.tdd/` path is
under it. The target repo's CLAUDE.md supplies the project specifics.

## Starting

Invoked as `/veri-dev [<lane>] [N] [--resume <file>]`.

- **`<lane>`** is an optional first word naming the lane: `/veri-dev mu [N] …` runs every read
  (`solvable-issues.sh`, `status.sh` included) and every conductor launch with
  `VERI_LABEL=ready-for-agent:mu`; with no lane word, plain `ready-for-agent`. State the lane
  in your first line of output.

- **N** is how many conductors to keep running; it defaults to 1.
- **MCP servers:** when this session has tools from any MCP server, tell the human once, in one
  line, the launch line that starts the session without them:
  `claude --strict-mcp-config --mcp-config '{"mcpServers":{}}'`. Change no setting yourself.
- **Writing in another repository:** when the user's instructions in this session forbid
  writing in a repository other than the session's, ask the human once whether veri may
  fast-forward its own clone before each new run, and record the answer with
  `$S/update-veri.sh --consent yes|no`. Ask only when no record exists; never edit the user's
  instructions.
- **Merging is always granted** for the runs this session finishes, in the project repo only.
  A run is merged after its review is OK; never one in another repo.
- **`--resume <file>`** reads a handoff for state only (live conductors, PRs
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
$S/detach-leaf.sh $S/run-conductor.sh <n> >> .tdd/conductor-<n>.log 2>&1 < /dev/null
```

Every launch, a resume included, appends with `>>` to that `.log`, the file `stop-reason.sh`
and `metrics.sh` read; none truncates it.

Announce it as `Started #<n> — <title>`, the title read from `gh issue view <n> --json title`.

Launch the next issue only once the previous launch's ledger exists: wait for
`.tdd/wt/<prev>/.tdd/issue-<prev>.md` with a Monitor on
`until [ -f .tdd/wt/<prev>/.tdd/issue-<prev>.md ]; do sleep 15; done; echo ledger <prev>`
(a script that blocks, P3). Until that file exists the issue is not yet claimed, and
`solvable-issues.sh` would hand it out again.

## Watching

Wait on the blocking watch of P3: `$S/watch-runs.sh`, run by a Monitor (or a background
command) itself, never a hand-written script. It prints one line per conductor exit; re-arm
silently.

## Routing an exit

On each conductor exit, read the facts — the issue's last comment
(`gh issue view <n> --json comments`), the committed ledger, the PR — never the exit code
alone, and route:

- **Last comment ✅ Done.** Review it, and on OK merge it through `veri-merge`.
  `veri-merge` does not exist yet: until it does, merge with the installed
  `merge` skill, and only when the ledger has no unchecked step (`$S/next-unchecked.sh <
  .tdd/wt/<n>/.tdd/issue-<n>.md` exits 3) and no `⟂ refactor pending` mark
  (`$S/next-pending-refactor.sh` on the same file exits 3); otherwise report it as not ready.
  A run that ended with an open question for the human is never merged.

  **Caveats before any merge**, whether on your own OK or on a coordinator's merge
  instruction: send the coordinator every caveat your review found, of three kinds only:
  a test never watched failing; a change to a guard or other product code outside the
  issue's stated scope; a departure from the issue's wording. Merge only after a reply that
  names each caveat. A review with none says so in the same report, and that report is
  still sent. A review may not report "no coverage" or "coverage lost" from the diff alone: before
  the claim it searches the whole test tree, including directories the diff never touches, for the
  behaviour's name, and the claim carries the `file:line` where coverage was found (then it is not a
  finding) or the search term it used and found nothing for. A mutation refused with `rate limit
  exceeded` while `gh api rate_limit` still reports quota hit GitHub's secondary limit: use REST, never wait for the reset.
- **Last comment is a bail.** Hand it to `veri-bail <n>`. `veri-bail` does not exist yet: until
  it does, classify the cause with `$S/classify-bail.sh <cause>`, resume a first bail once with
  `$S/run-conductor.sh <n>` launched as above (with `VERI_NEW_SKILL=1` when the fix it needs
  landed after its launch), and park a second one with `$S/park-issue.sh <n> <cause> <unblock>
  [<pr>]`, the only way to park: it labels the issue `parked` and posts the cause and what
  would unblock it. Budget raises come only from the coordinator or the human.
- **No closing comment.** Check for a usage limit or sleep first (P10). Either one is not a
  bail: resume the run once usage is back. Neither one: route it as a bail.

Then take the slot decision.

## Parked issues

On resume, read the parked set with `$S/parked-issues.sh` (exit 3: none parked), never from a
handoff or memory: GitHub holds it and each park's cause. Un-parking an issue removes its
`parked` label.

## When to stop and ask

Stop and ask the human only for: red CI you cannot fix, a ⟦human-owed⟧ step, a conflict you
cannot resolve, or a decision a ledger step asks for. Each is stated in full (P4). Everything
else you decide and keep going; a turn never ends while a slot can be filled (P5).

## Out of scope

You do not file, groom or reprioritise issues — that is the coordinator's job. You do not edit
veri's scripts or skills: a veri fault is reported to the coordinator as facts, and becomes an
issue there.

With a coordinator attached, each event P4 lets you speak about goes to the coordinator, not to
the human, unless you stop and ask (above).
