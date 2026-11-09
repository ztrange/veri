---
name: vdev
description: >-
  The veri dev session, reached by name: `/vdev [<lane>] [N] [--resume <file>]`, or `/vdev`.
---

# vdev — the dev session

Alias: `/vdev`

Obeys `operator/PRINCIPLES.md` under the veri clone root (`git -C <base dir> rev-parse --show-toplevel`); read it first.

`$S` is `skills/tdd/scripts/`, reached from this skill's base directory as `../tdd/scripts/`.
Every command runs from the target repository's main working tree, and every `.tdd/` path is
under it. The target repo's CLAUDE.md supplies the project specifics.

## Starting

Invoked as `/vdev [<lane>] [N] [--resume <file>]`.

- **`<lane>`** is an optional first word naming the lane: `/vdev mu [N] …` runs every read
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
   one now due or expired) or an order override — and send the coordinator no reply for it (P13).
   An N change restarts `dispatch.sh` with the new `--target`.
2. Count live conductors. While fewer than N are live, launch the next issue (below). When N
   went down, stop nothing: a live run finishes, and its slot is simply not refilled (P8).
3. When `$S/solvable-issues.sh` exits 3 and no run is live, the queue is empty: say so and stop.

Keep exactly N conductors running for as long as the solvable list is non-empty.

## Launching

Launches go through `$S/dispatch.sh`: it launches the next issue (the first line of
`$S/solvable-issues.sh` with no live conductor, unless the coordinator gave an override, P9)
detached, never as a conductor inside this session, and only after the previous launch's ledger
exists. The skill arms no ledger wait of its own.

Every launch, a resume included, appends with `>>` to `.tdd/conductor-<n>.log`, the file
`stop-reason.sh` and `metrics.sh` read; none truncates it. A launch by hand follows the same
form:

```bash
$S/detach-leaf.sh $S/run-conductor.sh <n> >> .tdd/conductor-<n>.log 2>&1 < /dev/null
```

Every conductor launch, a resume included, is followed by:

```bash
$S/detach-leaf.sh $S/restart-conductor.sh <n> >> .tdd/restart-<n>.log 2>&1 < /dev/null
```

It restarts that run's conductor at its next ledger commit once its growth reaches
0.85 × `VERI_RESET_GROWTH_CONDUCTOR`. `dispatch.sh` starts this restart watcher
(`restart-conductor.sh`) itself for every launch it makes, so you run the line above by hand only
for a launch you make by hand. A restart is not an exit to route.

`dispatch.sh` launches without printing. Announce each launch recorded in `.tdd/dispatch.log`
since your last turn as `Started #<n> — <title>`, the title read from
`gh issue view <n> --json title` (to the coordinator when one is attached, P4).

## Watching

Wait on the blocking watch of P3: `$S/dispatch.sh --target <N>`, run as one background command,
never under a Monitor and never a hand-written script. It launches and re-arms without printing,
and prints one line per event:

- `done <n> <pr-url>`
- `bail <n>`
- `silent-exit <n>`
- `merge-failed <pr-url>`
- `stalled <n>`
- `queue-empty`

You arm no other wait for conductors, ledgers or merges: no `watch-runs.sh`, no
`until [ -f … ]`, no `while kill -0 <pid>`.

## Routing an exit

On each conductor exit, read the facts — the issue's last comment only
(`gh issue view <n> --json comments --jq '.comments[-1].body'`, never the whole comment
thread), the committed ledger, the PR — never the exit code alone, and route:

- **Last comment ✅ Done.** Review it, and on OK merge it through `vmerge`.
  A run that ended with an open question for the human is never merged.

  **Briefing a review, hand-fix or merge subagent here:** the brief also carries the rules in
  the block under "Running the sibling skills" that opens "Every brief for a review, hand-fix or
  merge subagent also says".

  **Caveats before any merge**, whether on your own OK or on a coordinator's merge
  instruction: send the coordinator every caveat your review found, of three kinds only:
  a test never watched failing; a change to a guard or other product code outside the
  issue's stated scope; a departure from the issue's wording. Merge only after a reply that
  names each caveat. A review with none says so in the same report, and that report is
  still sent.

  **No coverage claim from the diff alone.** A review never reports "no coverage" or
  "coverage lost" from the diff alone: before the claim it searches the whole test tree,
  including directories the diff never touches, for the behaviour's name. The claim carries
  the `file:line` where coverage was found (then it is not a finding) or the search term it
  used and found nothing for.

  **Every finding is blocking or a PR-body line.** Each finding your review of a ✅ Done run
  makes is one of two things. **Blocking**, fixed on the PR's branch before merge: a criterion
  with no test that goes red when its behaviour is removed; a behaviour failure or regression;
  a surviving mutant in a guard, an exit-code path, or data-deleting or data-overwriting code;
  a doc miss (next paragraph). **Otherwise**, a line in the PR body. A review finding is never
  filed as an issue.

  **Doc miss.** When the run's PR adds or renames a phase, subcommand, flag or event, the
  review searches for the name in the script's usage string, `SCRIPTS.md`, `REVISE.md`, the
  `REQUIREMENTS.md` rows and the prompt templates. Any site that omits it, or still states the
  old behaviour, blocks the merge.

  **Rate limits.** A GitHub call refused with `rate limit exceeded` while `gh api rate_limit`
  still reports quota has hit GitHub's secondary limit: use REST rather than wait for the
  reset.
- **Last comment is a bail.** Hand it to `vbail <n>`. An issue is parked only through
  `$S/park-issue.sh <n> <cause> <unblock> [<pr>]`: it labels the issue `parked` and posts the
  cause and what would unblock it. Budget raises come only from the coordinator or the human.
- **No closing comment.** Check for a usage limit or sleep first (P10). Either one is not a
  bail: resume the run once usage is back, from the target repository's main working tree:
  `$S/detach-leaf.sh $S/run-conductor.sh <n> >> .tdd/conductor-<n>.log 2>&1 < /dev/null`
  (then the restart line from *Launching*). Neither one: route it as a bail.

After routing a `dispatch.sh` line, start `dispatch.sh` again as one background command. Then
take the slot decision.

## Running the sibling skills

The harness may report this skill's base dir as a symlink. Resolve it first, with
`cd -P <base dir> && pwd` (or `realpath <base dir>`), and read every sibling skill at
`<resolved base dir>/../<skill>/SKILL.md`, never at the path the harness reports.

Run `vmerge`, `vbail` and `vjudge` each through a subagent on the cheapest model that can do
the job, briefed to return at most 10 lines and to read the skill at
`<resolved base dir>/../<skill>/SKILL.md`.

**Every brief for a review, hand-fix or merge subagent also says:**

- Mutations (edit a file, run the suite, restore it) run only in a scratch clone or the run's
  own worktree, never in the primary clone.
- Every `cd` in a chained command makes the whole command fail when the `cd` fails (`&&` or
  `set -e`); a `;` never follows a `cd`, or a guard whose failure would change where the next
  command runs.
- Before reporting, check that `git -C <primary clone> status --porcelain` is empty, and report
  any output as dirt.
- No concurrent background jobs that share a scratch file.

Load `vhandoff` yourself, by reading `<resolved base dir>/../vhandoff/SKILL.md`.

Once your own context passes 200k tokens, or the harness warns that context is nearly full,
reset yourself with `/vhandoff dev` at the next point where no human decision is pending and no
run awaits your ruling or merge instruction (between batches), never in the middle of an
instruction.

## Parked issues

On resume, read the parked set with `$S/parked-issues.sh` (exit 3: none parked), never from a
handoff or memory: GitHub holds it and each park's cause. Un-parking an issue removes its
`parked` label and puts it back on the queue in one call: `$S/release-issue.sh <n>`, never a bare
label removal, which leaves the issue claimed (`taken:<lane>`) with nothing that takes it back.

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

You are the only role that watches run state; the coordinator watches none. When a coordinator is
attached, send it one message per conductor exit, bail or merge (P4).
