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

**Recovery.** When a state file for this role and lane exists, recover: read it through
`$S/status.sh --recover dev [--lane <lane>]` and read nothing else before your first slot
decision. An `N` on the invocation wins over the file's and is written to it (see *Role state*).
Recovery re-asks each pending decision once, re-sends or checks each pending message, and ends
with `$S/role-state.sh dev [--lane <lane>] recovered`, before the slot decision. With no state
file for this role and lane, start fresh.

**Attached.** A coordinator is attached when this session has received a message from one, or
when the role state records one (recovery lists `coordinator <session-id>` under State). From
the first line after recovery a recorded coordinator counts as attached: every event P4 lets you
speak about goes to it, by that session id, and the human gets `.`.

## Role state

Write your state through `$S/role-state.sh dev [--lane <lane>]` at the moment it changes, never
at reset time: N, each timed N change (with its expiry) and order override the coordinator
sends, each pending human decision (in full), and each message sent to the coordinator and not
yet confirmed. Drop the item when it ends. When a coordinator's first message arrives, or a
message comes from a different coordinator session id, record it with
`set coordinator <session-id>`; when a send to it fails because that session is gone, remove it
with `drop coordinator`.

## Live conductors and the slot decision

A conductor is **live** when `.tdd/wt/<n>/.tdd/conductor.pid` exists and its pid answers
`kill -0`. Count them fresh at every slot decision (P1); `$S/status.sh --json` gives the same
runs with their step k/n and phase.

**The slot decision**, taken at the start and again after every merge, every park and every
conductor exit:

1. Apply any change the coordinator sent since the last decision — a new N (including a timed
   one now due or expired) or an order override — and send the coordinator no reply for it (P13).
   Write the change to the role state file (*Role state*): `dispatch.sh`, run without `--target`,
   reads N, an unexpired timed N and the order overrides from `.tdd/role-dev.state` (`.tdd/role-dev-<lane>.state` in a lane) at each slot
   decision, so an N change or an override needs no restart. An N of 0 in that file holds
   dispatch: it launches nothing and keeps watching exits; a later positive N resumes launching.
2. Count live conductors. While fewer than N are live, launch the next issue (below). When N
   went down, stop nothing: a live run finishes, and its slot is simply not refilled (P8).
3. When `$S/solvable-issues.sh` exits 3 and no run is live, the queue is empty: say so and stop.

Keep exactly N conductors running for as long as the solvable list is non-empty.

## Launching

Launches go through `$S/dispatch.sh`: it launches the next issue (the first line of
`$S/solvable-issues.sh` with no live conductor, unless the coordinator gave an override, P9)
detached, never as a conductor inside this session, and only after the previous launch's ledger
exists. The skill arms no ledger wait of its own.

`dispatch.sh` skips a solvable issue whose named paths an open run draft PR changes, on any
machine, a run on another machine included. It prints each skip line, and you report each one to
the coordinator as an override (P4).

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

Wait on the blocking watch of P3: `$S/dispatch.sh`, run as one background command,
never under a Monitor and never a hand-written script. It takes N and the launch order from
`.tdd/role-dev.state`, or `.tdd/role-dev-<lane>.state` in a lane (*The slot decision*); `--target <N>` replaces only N with a fixed value
(order overrides still apply), and `--target 0` holds dispatch: the watch keeps reporting exits
and launches nothing. It launches and re-arms without printing,
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
  a doc miss (next paragraph). **Otherwise**, a line appended to the PR's existing body (read the body, add the line, write it back), never a replacement of the body: the `Closes #<n>` line survives. A review finding is never
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
- **No closing comment.** Check for a usage limit, an API outage or sleep first (P10). Any of
  the three is not a bail: resume the run once usage is back or the API answers, from the target
  repository's main working tree:
  `$S/detach-leaf.sh $S/run-conductor.sh <n> >> .tdd/conductor-<n>.log 2>&1 < /dev/null`
  (then the restart line from *Launching*). None of the three: route it as a bail.

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

- Run `make unit` first. Start the full suite, or any suite beyond `make unit`, only while no
  conductor baseline is running: a running baseline is a `.tdd/wt/<n>/.tdd/baseline*.pid` (both
  `baseline.pid` and `baseline-<tier>.pid`) with no matching `.exit` whose pid is live, never a
  `pgrep` on the word "baseline".
- Mutations (edit a file, run the suite, restore it) run only in a scratch clone or the run's
  own worktree, never in the primary clone.
- Every `cd` in a chained command makes the whole command fail when the `cd` fails (`&&` or
  `set -e`); a `;` never follows a `cd`, or a guard whose failure would change where the next
  command runs.
- Before reporting, check that `git -C <primary clone> status --porcelain` is empty, and report
  any output as dirt.
- No concurrent background jobs that share a scratch file.
- Every command reads stdin from `/dev/null`.
- Every external command (a program, not a shell builtin such as `cd`) runs under a time limit,
  in a form that works on macOS: `perl -e 'alarm shift; exec @ARGV' <seconds> <command>`.
- `rm` removes only paths inside the project directory, never outside it; scratch lives under
  the run worktree's `.tdd/`.
- A hand fix runs `make unit` and every affected suite outside the fast tier before it pushes.
- A reviewer that pushes any fix does not merge: it reports and stops, and the fix is reviewed
  afresh before the merge.

Load `vhandoff` yourself, by reading `<resolved base dir>/../vhandoff/SKILL.md`.

Once your own context passes 15% of your context window (150k tokens of a 1M window), or the harness warns that context is nearly full,
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

With a coordinator attached (see *Starting*), each event P4 lets you speak about goes to the coordinator, not to
the human, unless you stop and ask (above).

You are the only role that watches run state; the coordinator watches none. When a coordinator is
attached, send it one message per conductor exit, bail or merge (P4).
