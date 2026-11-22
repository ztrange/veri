---
name: vdev
description: >-
  The veri dev session, reached by name: `/vdev [<lane>] [N] [--auto] [--resume <file>]`, or `/vdev`.
---

# vdev — the dev session

Alias: `/vdev`

Obeys `operator/PRINCIPLES.md` under the veri clone root (`git -C <base dir> rev-parse --show-toplevel`); read it first.

`$S` is `skills/tdd/scripts/`, reached from this skill's base directory as `../tdd/scripts/`.
Every command runs from the target repository's main working tree, and every `.tdd/` path is
under it. The target repo's CLAUDE.md supplies the project specifics.

## Starting

Invoked as `/vdev [<lane>] [N] [--auto] [--resume <file>]`.

- **`<lane>`** is an optional first word naming the lane: `/vdev mu [N] …` runs every read
  (`solvable-issues.sh`, `status.sh` included) and every conductor launch with
  `VERI_LABEL=ready-for-agent:mu`; with no lane word, plain `ready-for-agent`. The session does
  not state the lane in its output: the lane is in the role state and the `taken:<lane>` label.

- **N** is how many conductors to keep running; it defaults to 1.
- **`--auto`** opts this session into autonomous mode: parked issues go to `vjudge` (*Parked
  issues*). On a `/vdev` turn the human typed, write `$S/role-state.sh dev [--lane <lane>] set
  auto on` when the invocation carries `--auto`, and `set auto off` when it does not, so autonomy
  never carries over from an earlier session; a recovery turn keeps the recorded value (*Role
  state*).
- **MCP servers:** when this session has tools from any MCP server, send once, as a notice
  (*Speaking*), the launch line that starts the session without them:
  `claude --strict-mcp-config --mcp-config '{"mcpServers":{}}'`. Change no setting yourself.
- **Writing in another repository:** when the user's instructions in this session forbid
  writing in a repository other than the session's, ask the human once whether veri may
  fast-forward its own clone before each new run, as *When to stop and ask* puts a question (a
  question session where the session has `start_session`, else in full in the transcript), and
  record the answer with `$S/update-veri.sh --consent yes|no`. Ask only when no record exists;
  never edit the user's instructions.
- **Merging is always granted** for the runs this session finishes, in the project repo only.
  A run is merged after its review is OK; never one in another repo.
- **`--resume <file>`** is read in every session. It reads a handoff for state only (live
  conductors, PRs awaiting merge, N and any timed change; overrides and permissions are in the
  role state file); the rules are this skill's. Re-read that state live before the first slot
  decision.

**Recovery.** When a state file for this role and lane exists, recover: read it through
`$S/status.sh --recover dev [--lane <lane>]` and read nothing else before your first slot
decision but `$S/github-outage.sh status` (*Local mode*, below). An `N` on the invocation wins over the file's and is written to it (see *Role state*).
Recovery re-asks each pending decision once in a session without `start_session` (in a session
with it, each is restated only in its own question session, *Speaking*), re-asks none of the question files its `Questions`
section lists, runs *When to stop and ask*'s step 3 once for each file its `Unasked questions`
section lists, acts on each file its `Answered questions` section lists as *Answers* says,
treats a restored pending decision whose text starts `landing held: <stack>` (*Routing an exit*)
as keeping every landing and every join onto that stack held until the human answers,
re-sends or checks each pending message, and ends
with `$S/role-state.sh dev [--lane <lane>] recovered`, before the slot decision. After a compaction of the dev session's own context, the dev
session re-invokes `/vdev` (with the lane word when it runs in a lane) before its next slot
decision, and that re-invocation runs this *Recovery* from the role state file. With no state
file for this role and lane, start fresh.

**Local mode.** Whether the session starts fresh, recovers or resumes (`--resume`), run
`$S/github-outage.sh status` before its first slot decision. On exit 0 `.tdd/github-outage`
exists in the target repository's main working tree (a GitHub outage: no merge goes online), or
held ones are still being merged: read `<resolved base dir>/../voutage/SKILL.md` yourself and follow it (it finishes
those merges and waits on its wait) before that decision. While that file exists a ✅ Done run
whose review is OK is handled as `voutage` says instead of being merged online: joined offline
where a stack is named, held where none is. The file is the mode, never a handoff or memory.

## Speaking

Every turn of the dev session prints `.` and nothing else, except a turn answering a question the
human typed, which answers it. A run's status is on its issue (the `taken:<lane>` claim, step
ticks, bails, merges), and a question the human must answer is in its own session (*When to stop
and ask*), so the transcript carries neither.

A **notice** — the MCP
launch line of *Starting*, a missing `delegate` skill, `github-outage.sh hold`'s exit 2, a red
stack that stays frozen after its failed jobs' re-run, `record-answer.sh`'s exit 2 (*Answers*), a
question session's failed start (*When to stop and ask*, step 3), a failed join or a landing
reported under *Routing an exit*, `dispatch.sh`'s `queueing`, `stretched` and `t-lowered` lines (each one the ended watch printed, sent as its own notice when a closing line ends the watch), its `queue-blocked` line, each line `voutage` tells the human — is
sent once: as one `PushNotification`
where the session has that tool, else as one line in its transcript.

In a session with `start_session`, restate no pending decision in your own transcript, whatever
the human's message is about: each is restated only in its own question session, which is where
P4's and P21's restatement is met. In a session
without it (a terminal), a decision is asked in full in the transcript, once, as *When to stop and
ask* says.

## Role state

Write your state through `$S/role-state.sh dev [--lane <lane>]` at the moment it changes: N, each timed N change (with its expiry, written as `<n> until <ISO-8601 datetime>`, the form `role-state.sh ... add timed-n` accepts and `dispatch.sh` parses) and order override the human
gives you, each pending human decision (in full) not held in a question file, and each message you
sent another session and have not yet confirmed. Drop the item when it ends. A pending decision `vjudge` recorded you do not write
again with `role-state.sh … add decision`: the judge records it in a question file when your brief
named one, and with `role-state.sh … add decision` otherwise. A held landing (*Routing an exit*)
is the one pending decision you record yourself, in every session, and `vjudge` never records it.

`--auto` is written with `$S/role-state.sh dev [--lane <lane>] set auto on|off` (*Starting*), and
recovery restores it: `$S/status.sh --recover dev [--lane <lane>]` prints the recorded value as
`auto on` or `auto off` under `State`, and a recovered session runs in the mode it names (with no
`auto` line, off).

## Live conductors and the slot decision

`.tdd/wt/<n>/.tdd/conductor.pid` holds two lines: the conductor's pid, then that pid's start time. A
conductor is **live** only when the file exists, its first-line pid answers `kill -0`, and that
pid's start time matches the second line: a pid alone fails on the two-line file (`illegal pid`)
and passes for a recycled pid. Do not hand-roll the check: `$S/status.sh --json` applies the
rule and gives the live runs with their step k/n and phase. Count them fresh at every slot
decision (P1).

**The slot decision**, taken at the start and again after every merge, every park and every
conductor exit:

1. A new N (a timed one with its expiry, as `<n> until <ISO-8601 datetime>`) or an order override
   the human gives you is written to the role state file with
   `$S/role-state.sh dev [--lane <lane>]` at once, an override with the human as who asked (P9),
   and applied at this slot decision. Never change N on your own: no judgment of your own and no
   `vjudge` ruling changes N.
   A numeric N also narrows the machine's test-worker budget T to the lanes' needs, never above the ceiling:
   `role-state.sh dev set n` writes this lane's need, max(N, live conductors) × `VERI_CONDUCTOR_TEST_WORKERS`
   (default 2), and prints the T it leaves, beside the other lanes' needs and the ceiling, so you weigh N's test cost
   before you apply it; `dispatch.sh` rewrites the need at each poll.
   Write the change to the role state file (*Role state*): `dispatch.sh`, run without `--target`,
   reads N, an unexpired timed N and the order overrides from `.tdd/role-dev.state` (`.tdd/role-dev-<lane>.state` in a lane) at each slot
   decision, so an N change or an override needs no restart. An N of 0 in that file holds
   dispatch: it launches nothing and keeps watching exits; a later positive N resumes launching.
2. Count live conductors. While fewer than N are live, launch the next issue (below). When N
   went down, stop nothing: a live run finishes, and its slot is simply not refilled (P8).
3. When `$S/solvable-issues.sh` exits 3 and no run is live, the queue is empty: stop with `.`
   (*Speaking*); the exit 3 is the record.

Keep exactly N conductors running for as long as the solvable list is non-empty.

## Launching

Launches go through `$S/dispatch.sh`: it launches the next issue (the first line of
`$S/solvable-issues.sh` with no live conductor, unless the human gave an override, P9)
detached, never as a conductor inside this session, and only after the previous launch's ledger
exists. The skill arms no ledger wait of its own.

`dispatch.sh` skips a solvable issue whose named paths an open run draft PR changes, on any
machine, a run on another machine included, but never the issue's own run draft PR. Its output holds each skip; you report
no skip line.

Every launch, a resume included, appends with `>>` to `.tdd/conductor-<n>.log`, the file
`stop-reason.sh` and `metrics.sh` read; none truncates it. A launch by hand follows the same
form:

```bash
$S/detach-leaf.sh $S/run-conductor.sh <n> >> .tdd/conductor-<n>.log 2>&1 < /dev/null
```

Several launches by hand are written out one literal line each, or looped under `bash -c`; never
through an unquoted variable expanded into arguments (`set -- $spec`): zsh does not word-split
it, so the issue number and its knobs reach `run-conductor.sh` as one argument.

Every conductor launch, a resume included, is followed by:

```bash
$S/detach-leaf.sh $S/restart-conductor.sh <n> >> .tdd/restart-<n>.log 2>&1 < /dev/null
```

It restarts that run's conductor at its next ledger commit once its growth reaches
0.85 × `VERI_RESET_GROWTH_CONDUCTOR`. `dispatch.sh` starts this restart watcher
(`restart-conductor.sh`) itself for every launch it makes, so you run the line above by hand only
for a launch you make by hand. A restart is not an exit to route.

`dispatch.sh` launches without printing. Announce no launch: `dispatch.sh` records each in
`.tdd/dispatch.log`, and the run's `taken:<lane>` claim carries its start.

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
- `queue-blocked <pr-url>…`: every solvable issue is skipped for overlap and no run is live, each
  blocking draft PR named; dispatch prints it once per set of blocking PRs. Send it as a notice
  (*Speaking*) and re-arm the watch: a re-armed dispatch prints it again only for a different set

Those are the closing lines: each ends the watch. Three more lines are advice, printed while
`dispatch.sh` keeps watching, never the end of the watch; they change nothing:

- `queueing <k> waiting for T=<t>, <w> workers in use: a lower N would shorten the wait`: test
  runs keep queueing
- `stretched <n> <tier> <seconds>s, idle <idle>s`: a run's `fast` or `all` test run took more than
  twice its idle duration, once per run and tier
- `t-lowered <old> <new> <cases>`: a load timeout lowered T from `<old>` to `<new>`, the timed-out
  `<cases>` named; dispatch reports it once

When a closing line ends the watch, send each `queueing`, `stretched` and `t-lowered` line that
watch printed as a notice (*Speaking*), then route the closing line.

You arm no other wait for conductors, ledgers or merges: no `watch-runs.sh`, no
`until [ -f … ]`, no `while kill -0 <pid>`. `voutage`'s wait on GitHub's status page is its own.

## Routing an exit

On each conductor exit, read the facts — the issue's last comment only
(`gh issue view <n> --json comments --jq '.comments[-1].body'`, never the whole comment
thread), the committed ledger, the PR — never the exit code alone, and route:

- **Last comment ✅ Done.** Where `$S/stack-branch.sh` exits 0 (the target repository's
  `CLAUDE.md` names a stack branch), review it, and on OK hand it to `vmerge`, which joins the run
  to the stack rather than merging it, as its *Joining a stack* says, offline while
  `.tdd/github-outage` exists; no outage hold runs in front of it. Where it exits 3, review it, and
  on OK run `$S/github-outage.sh hold <pr-url>` first: exit 3 (`.tdd/github-outage` does not
  exist) merges it through `vmerge`; exit 0 holds it instead, since a GitHub outage holds merges,
  and it is then handled as `voutage` says; exit 2 is sent once as a notice (*Speaking*) and
  nothing is merged. A run that ended with an open
  question for the human is never merged, and never joined; nor is any reviewed run joined onto a
  stack whose landing is held (*Landing a slice*, below).

  **Briefing a review, hand-fix or merge subagent here:** the brief also carries the rules in
  the block under "Running the sibling skills" that opens "Every brief for a review, hand-fix or
  merge subagent also says".

  **Caveats before any merge.** A caveat is one of three kinds only: a test never watched
  failing; a change to a guard or other product code outside the issue's stated scope; a
  departure from the issue's wording. Each caveat your review found passes `vjudge`, run as
  *Running the sibling skills* says, and a caveat `vjudge` settles is ruled by it. Before the
  merge, append each ruling to the PR's body as one line naming the caveat and the ruling (read
  the body, add the line, write it back). A caveat `vjudge` does not settle becomes a question as
  *When to stop and ask* puts one, tied to the run's issue: that PR is not merged until you read
  the answer from the question file, and every other run goes on. A review reporting no caveat
  is merged on its OK.

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
- **Last comment is a bail.** A bail whose last `bail` event in `.tdd/wt/<n>/.tdd/events.jsonl` has
  cause `step-too-big` is first passed to `vjudge`, run as *Running the sibling skills* says, with
  the ledger's `## Owed steps` and the issue's acceptance criteria, before `vbail`: the run stopped
  at the growth limit, and the judge rules on what the issue needs. Hand the bail to `vbail <n>` only
  when the judge did not resume the run, so one bail is never acted on twice. An issue is parked only through
  `$S/park-issue.sh <n> <cause> <unblock> [<pr>] [--blocked-by <n>[,<n>…]]`: it labels the issue
  `parked` and posts the cause and what would unblock it. Pass the number of every issue or PR
  that must land first as `--blocked-by`, so the parked issue waits on each. Budget raises come only from the human.
- **No closing comment.** Check for a usage limit, an API outage or sleep first (P10). Any of
  the three is not a bail: resume the run once usage is back or the API answers, from the target
  repository's main working tree:
  `$S/detach-leaf.sh $S/run-conductor.sh <n> >> .tdd/conductor-<n>.log 2>&1 < /dev/null`
  (then the restart line from *Launching*). The resume takes a slot like any launch: it runs only
  when the live conductors, counted fresh as *Live conductors and the slot decision* defines,
  number fewer than N (an unexpired timed N included); otherwise it is held, and the next freed slot goes to it ahead of the solvable
  queue: `dispatch.sh` fills a freed slot only from that queue and never sees a held resume, so
  launch the held resume before restarting `dispatch.sh`. It also runs only when no process is
  inside the run's worktree: run `lsof +D <absolute path of .tdd/wt/<n>>` from the main working
  tree, never from inside the worktree, and read its output, not its exit code (`lsof` can exit 1
  while printing lines); any process line it prints is a foreign process, and the resume is then
  held to the next slot decision. None of the three: route it as
  a bail.
- **A failed merge.** It reaches you two ways, each with its report: a `merge-failed <pr-url>`
  line from `dispatch.sh`, for a `queued-merge.sh` merge, which leaves no report the session can
  read (its output goes wherever its launcher sent it, and no skill records where), so its cause
  is not named; or the report of a `vmerge`
  subagent you started, saying the merge did not land. When the failed merge's report names red
  CI, a rebase conflict, a refused push or a billing block, handle it as `vmerge` says. Any other
  cause, by either way: read `<resolved base dir>/../voutage/SKILL.md` yourself, not through a
  subagent, and follow it for that PR's url.
- **A failed join.** The `vmerge` subagent's report names the join's exit. An exit 1 because the
  stack is red (its stderr names the red commit) leaves the run as it is: the stack goes to *A red
  stack* meanwhile, and the join is retried once `$S/stack-red.sh` exits 3, never sooner. An exit
  1 for a conflict you cannot resolve goes to *When to stop and ask*. Any other exit 1 (a red fast
  tier, a unit owing a grade, an offline join's red full suite) is reported to the human as a
  notice (*Speaking*), with its stderr. Each leaves the run as it is. An exit 2 is reported as a
  notice with its stderr, and then read `<resolved base dir>/../voutage/SKILL.md` yourself, not
  through a subagent, and follow its *On a failed merge* for that PR's url, never retrying the
  join blind. An exit 3, the pull request already merged into the stack, is nothing to do.
- **Landing a slice.** After each join, and after each `$S/stack-red.sh` exit 3, run
  `$S/stack-land.sh` without `--now`, in the target repository's main working tree, unless a
  landing is held: whether a slice lands now (100 commits or an idle stack) is the script's to
  decide, not yours. Exit 0 is reported as a notice (*Speaking*) with the slice's pull request url
  and the issues it landed. Exit 3, nothing to land, is the common case and is not reported. Exit
  1 is reported as a notice with its stderr. Exit 2 can mean the carry-over is still owed
  (`$S/stack-carry.sh <cut>`, named on its stderr), which leaves the stack for the human: it holds
  every later landing and every join onto that stack, a reviewed run's join included, and goes to
  *When to stop and ask*, never through `vjudge`. At once, record it yourself with
  `$S/role-state.sh dev [--lane <lane>] add decision "landing held: <stack> — <the exit 2 line>"`
  (*Role state*), then ask the human as *When to stop and ask* does. The landing stays held while
  that decision is recorded; once you have acted on the human's answer, drop it with
  `$S/role-state.sh dev [--lane <lane>] drop decision <id>`. Nothing else lifts the hold: no later
  join, rerun or judgment.
  Where a stack is named, the standing merge permission in the project repo (*Starting*) covers
  `$S/stack-land.sh` for the stack's slices, and a pull request based on the default branch
  is still merged through `vmerge` as before; nothing else reaches the default branch: no other
  push, merge or rebase onto it. `--now` is run only when the human asks for it.
  You never rebase a live run's branch across a landing: the run carries itself at its own join,
  whose rebase onto the stack is the run's, so its branch keeps one writer.

After routing a `dispatch.sh` line, and launching any held resume the freed slot now takes, start
`dispatch.sh` again as one background command. Then take the slot decision.

## A red stack

Where the target repository's `CLAUDE.md` names a stack branch, a red CI answer on its tip
freezes every join, so every lane waits on it. The stack is fixed by hand, never by a new veri run,
in one bounded attempt; this is veri's own procedure, and an operator may run it with any
test-first hand method.

- **The culprit.** Run `$S/stack-culprit.sh <red-sha>` and keep what it prints as the *culprit
  file*. On its exit 0, brief one hand-fix subagent, as *Running the sibling skills* says, with
  the culprit file: in a *fix worktree* (a detached worktree under the target repository's
  `.tdd/`, cut from `origin/<stack>`'s tip) it fixes exactly the cases the culprit file names,
  each watched red before the fix and green after, and commits without pushing.
- **The bounds.** The fix edits no test file. Each of its commits has a subject ending `(#<n>)`,
  naming the culprit's issue `<n>`, and a `Stack-fix: <red-sha>` trailer. It is pushed only by
  `$S/stack-fix.sh <n> <red-sha> <culprit-file>`, which you run, never the fix agent.
- **The review.** Before `stack-fix.sh` runs, one independent read-only review subagent, which
  did not write the fix, reads `git diff origin/<stack>..HEAD` in the fix worktree and answers OK
  or not OK. Only an OK runs `stack-fix.sh`.
- **CI is the gate.** After `stack-fix.sh` pushes, wait on `$S/stack-red.sh` until the newest
  completed run is on the fix's commit or a later one: exit 3 is the stack back to normal (the
  freeze lifts and joins resume); exit 0 is the fix failing.
- **One attempt.** A review that is not OK, a `stack-fix.sh` exit 1, or a red CI answer on the
  fix's tip is answered by `$S/stack-revert.sh <n>`, which reverts the fix, when it was pushed,
  with the culprit. No second fix is briefed.
- **No culprit.** On a `stack-culprit.sh` exit 3, re-run the red workflow run's failed jobs once
  (`gh run rerun <run-id> --failed`). Green, the freeze lifts; red again, the freeze stays and a
  notice is sent (*Speaking*). Nothing is reverted without a culprit.
- **No answer.** A `stack-fix.sh` exit 2, or a `stack-revert.sh` exit 2 or exit 3, is never taken
  as fixed or reverted: the stack stays frozen, and it goes to *When to stop and ask*.
- **Offline.** While `.tdd/github-outage` exists, a stack frozen by `.tdd/stack-local-red`
  (`$S/stack-red.sh` prints `local`) gets no culprit search, revert or hand fix through GitHub,
  all of which read it: send it once as a notice (*Speaking*) and take it to *When to stop and
  ask*. Once the human has acted, run `$S/queued-merge.sh --local-green`: exit 0 lifts the freeze
  and joins resume, exit 3 says it was already lifted, exit 1 keeps it, and exit 2 is reported.

## Running the sibling skills

The harness may report this skill's base dir as a symlink. Resolve it first, with
`cd -P <base dir> && pwd` (or `realpath <base dir>`), and read every sibling skill at
`<resolved base dir>/../<skill>/SKILL.md`, never at the path the harness reports.

Run `vmerge`, `vbail`, `vjudge` and `vfile` each through a subagent on the cheapest model that can do
the job, briefed to return at most 10 lines and to read the skill at
`<resolved base dir>/../<skill>/SKILL.md`.

Load the installed `delegate` skill with the Skill tool and work through it: every log, diff,
review and issue sweep is read by a subagent briefed as that skill says, and only its report
enters your context. Where `delegate` and P6 differ (the return's length, the cheapest adequate
model, work done inline rather than in a subagent), P6 holds. The subagents and the brief block
below stay as this section states them, a merge or hand-fix subagent pushing as its skill or
brief says. When `delegate` is not installed, send that once as a notice (*Speaking*) and follow P6.

**Every brief for a review, hand-fix or merge subagent also says:**

- Its first line, in bold, is the default: never write `rm` in any command, not even on
  `/dev/null`, save the one exception its second line states.
- Its second line states that exception: `rm` on a path inside the project directory, never on
  one outside it; scratch lives under the run worktree's `.tdd/`.
- Run `make unit` first. Start the full suite, or any suite beyond `make unit`, only while no
  conductor baseline is running: a running baseline is a `.tdd/wt/<n>/.tdd/baseline*.pid` (both
  `baseline.pid` and `baseline-<tier>.pid`) with no matching `.exit` whose pid is live, never a
  `pgrep` on the word "baseline".
- Mutations (edit a file, run the suite, restore it) run only in a scratch clone or the run's
  own worktree, never in the primary clone. A mutation probe backs the file up with `cp` into the
  run worktree's `.tdd/`, mutates it with `perl -pi -e` or a script (never `sed -i.<ext>`, which
  leaves a backup file), and restores it from the `cp` backup when the file has uncommitted edits
  (`git checkout -- <file>` would discard them), with `git checkout -- <file>` otherwise.
- Every `cd` in a chained command makes the whole command fail when the `cd` fails (`&&` or
  `set -e`); a `;` never follows a `cd`, or a guard whose failure would change where the next
  command runs.
- Before reporting, check that `git -C <primary clone> status --porcelain` is empty, and report
  any output as dirt.
- No concurrent background jobs that share a scratch file.
- Every command reads stdin from `/dev/null`.
- Every external command (a program, not a shell builtin such as `cd`) runs under a time limit,
  in a form that works on macOS: `perl -e 'alarm shift; exec @ARGV' <seconds> <command>`.
- Every command runs with `$VERI_VENV/bin` (default `~/.veri-tools/venv/bin`) first on PATH, set
  in that same call, since calls share no shell state; the prefix goes on the form the two items
  above require:
  `PATH="${VERI_VENV:-$HOME/.veri-tools/venv}/bin:$PATH" perl -e 'alarm shift; exec @ARGV' 900 make unit < /dev/null`.
- A hand fix runs `make unit` and every affected suite outside the fast tier before it pushes.
- Every fix or tick note the subagent writes cites a commit's subject next to its sha: a rebase
  merge rewrites shas, and the subject still finds the commit.
- A reviewer that pushes any fix does not merge: it reports and stops, and the fix is reviewed
  afresh before the merge.

Load `vhandoff` yourself, in every session, by reading `<resolved base dir>/../vhandoff/SKILL.md`.
Load `voutage` yourself, at `<resolved base dir>/../voutage/SKILL.md`: it holds the session's own
merge state.

The dev session never compacts or clears its own context on its own judgment.

## Parked issues

On resume, read the parked set with `$S/parked-issues.sh` (exit 3: none parked), never from a
handoff or memory: GitHub holds it and each park's cause. Un-parking an issue, or returning a bailed or preflight-refused one, removes its
`taken:<lane>` claim (and the `parked` or `bailed` marker, if it has one) and puts it back on the queue in one call: `$S/release-issue.sh <n>`, never a bare
label removal, which leaves the issue claimed (`taken:<lane>`) with nothing that takes it back.

After every merge, and on recovery, read `$S/parked-issues.sh` and release each issue whose fifth
field is `ready` (every blocker it waits on landed) with `$S/release-issue.sh <n>`.

**Under `--auto`** (the role state's `auto on`), at that same reading pass each other issue
`$S/parked-issues.sh` lists to `vjudge`, run as *Running the sibling skills* says, with its park
comment, except one whose sixth field is `question`: its park holds a question the human has not
answered on the issue, in a terminal as in a session with `start_session`, so it is never passed
again and waits for that answer (in a session with `start_session`, its question file is handled
as *When to stop and ask*, step 1, says). A decision the judge reaches is posted on the issue as a comment naming
the rule applied and the option not taken (its *Recording*), and the issue is then returned with
`$S/release-issue.sh <n>`, so its resumed run applies the decision. A judge outcome on its *Always
surface* list leaves the issue parked, unreleased, and goes to the human as a question the way
*When to stop and ask* puts one: a `.tdd/questions/<id>.md` file and a session for it. Without
`--auto`, no parked issue is passed to `vjudge` by this rule, and a parked issue is released only
on the human's answer, or when every blocker it waits on landed (above).

## Priority

Apply the priority label the target repo's CLAUDE.md names yourself, once `vjudge` is clear (run
as *Running the sibling skills* says), to an issue whose landing makes future runs cheaper (a
slower suite made faster, a leaf cost cut, a recurring bail cause removed) or gives the human
something usable, or feedback on a plan, sooner (P16). `$S/solvable-issues.sh` ranks `priority`
issues ahead, so the label is the order. A priority call `vjudge` surfaces instead of clearing
becomes a question as *When to stop and ask* puts one, and the label waits on its answer.

## When to stop and ask

Stop and ask the human only for: red CI you cannot fix, a ⟦human-owed⟧ step, a conflict you
cannot resolve, a decision a ledger step asks for, a review caveat `vjudge` does not settle
(*Routing an exit*), a veri fault found while veri's repository is not the project repo, a split
or criteria rewrite `vfile` proposes that `vjudge` surfaces (*Out of scope*), a priority call
`vjudge` surfaces (*Priority*), a held landing (*Routing an exit*), or whether veri may fast-forward its own clone (*Starting*). Each
such case but a held landing first goes through `vjudge`,
run as *Running the sibling skills* says: what the judge settles is acted on and never asked, and
only what it surfaces reaches the human, as P21 says, stated in full (P4). A held landing is asked
without `vjudge`: you record it (*Routing an exit*) and ask the human yourself, in full in your
transcript in a session without `start_session`, and in a session with it by writing its question
file yourself under step 2's four headings and running step 3, so no judge settles it and it
always reaches the human. Every other question put to the human quotes the `vjudge` ruling that
surfaced it; a question with no such ruling is not asked but passed to `vjudge` first. Everything else you decide and keep going; a turn never ends while a
slot can be filled (P5).

**In a session without the app's `start_session` tool** (a terminal), your brief to `vjudge` names
no question-file path and nothing is written under `.tdd/questions/`: a case the judge does not
settle is asked in full in your own transcript, once (P4).

**In a session with `start_session`**, each case has a question file, `.tdd/questions/<id>.md`:
`<id>` is `<lane>-<n>` for a question tied to issue `<n>` and `<lane>-<slug>` otherwise, `<lane>`
being `main` with no lane word. A lane word holds no `-` and is not `main`, so no two lanes share a
question-file prefix.

1. Before briefing `vjudge` on a case, look for its question file. When it exists, run no `vjudge`
   on the case again. With an `## Asked` line the question was asked: open no second session for
   it and send no notification. With neither an `## Asked` nor an `## Answer` line it was written
   but never asked: run step 3 for it now. An `## Answer` in it is acted on as *Answers* says.
2. Otherwise your brief to `vjudge` names that path. The judge writes there a case it does not
   settle, under `#### Question`, `#### Options`, `#### Found` and `#### Recommendation`, and
   returns the path.
3. When `vjudge` returns the path, call `start_session` once, with a brief naming the file's path,
   your own session id and the *Question session* section of this skill as the procedure to
   follow, and nothing else of the question. When `start_session` returns the new session's id,
   append one line, `## Asked <session-id>`, to the question file, and only then send one
   `PushNotification` naming the question by its `<id>`. When the start fails, append nothing,
   send no `PushNotification`, and send the failure once as a notice (*Speaking*): the file stays
   unasked, and recovery lists it under `Unasked questions`.
4. Do not wait for that session to start or to answer: on the same turn, carry on with every run
   the question does not block.

The `## Asked <session-id>` line is the only line you write to a question file, save a held
landing's, which you write whole. It is not part of the question, which otherwise only `vjudge`
writes (as the answer is the question session's), but the record
that you opened its session; it is appended after `vjudge` parked the issue with the file, so the
park comment never holds it.

The issue of an issue-bound question is parked by `vjudge` (its *The procedure* step 5) with
`$S/park-issue.sh --question-file` naming the question file, so the park comment is that file
verbatim. You park no question's issue yourself, and never read the question or an answer back
from the comment. In a session with `start_session`, your own transcript never holds a question's
text or a request for an answer.

**Answers.** On a message naming a question file, read the answer from the file, never from the
message, and act on it. For a question tied to issue `<n>`, first run
`$S/record-answer.sh <n> <question-file>`, before you act: it posts the question and the answer
on the issue as one comment, which `vjudge` reads as the owner's decision and a resumed run as the
answer to its park. Act only on its exit 0 (posted) or 3 (already there); on exit 2 neither act
nor delete the file, and send its stderr line once as a notice (*Speaking*). You post an answer on
an issue by no other route. Delete the question file only after you observe your own action on
the answer in state (the label gone, the run resumed, the merge landed) and, for a question tied
to an issue, after `record-answer.sh` exited 0 or 3 for it, and say so nowhere. After a reset,
recovery sorts each of your lane's question files into one of three sections: re-ask none of the
files its `Questions` section lists (asked, not yet answered); run step 3 once for each file its
`Unasked questions` section lists (written, never asked); and act on each file its `Answered
questions` section lists as this paragraph says (record, act, observe, delete).

## Question session

A question session is started by vdev with `start_session` and briefed with a question file's
path, vdev's session id and this section. It asks nothing the file does not ask:

1. Read the question file.
2. Put its question to the human, as plain text (P21).
3. Write the human's answer under an `## Answer` heading in the same file.
4. Send vdev, by the session id in the brief, one line naming the file.
5. Archive itself.

## Out of scope

You do not groom issues: grooming (`vgroom`) is the human's to run, not yours. You do not edit
veri's scripts or skills. You file and reprioritise issues only where this skill says you do
(*Priority*, and below):

- **A veri fault** (a script, a prompt or a skill misbehaving) a run turns up is filed through
  `vfile` when veri's repository is the project repo. Otherwise it becomes a question (*When to
  stop and ask*) naming the repository, file and change, and nothing is written there (P11).
- **A bug a run in your lane turns up** is filed through `vfile` with the lane as its scope, so
  it carries `ready-for-agent:<lane>` (plain `ready-for-agent` with no lane word). A veri defect
  from a run on another repository is never opted in.
- **A split or criteria rewrite `vfile` proposes** passes `vjudge` and is not shown to the human
  first; one `vjudge` surfaces becomes a question.
