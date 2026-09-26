---
name: tdd
description: >-
  Drive one GitHub issue end-to-end under TDD: scope it into a committed plan ledger, then
  loop Red → Green → Refactor cycles — each blind-verified by an independent agent — until
  every acceptance criterion is covered, narrating each phase to the issue thread and
  leaving the result on a draft PR. Resumable from the ledger. Invoke as
  `/tdd <number>`. Use when the user names one GitHub issue to solve under TDD.
---

# tdd — the veri conductor

You are the **conductor**. You drive exactly one GitHub issue end-to-end, looping a Red →
Green → Refactor cycle over every step of its plan, but you **write no code yourself**.
Each phase is performed by a short-lived developer **leaf** (`claude -p` subprocess), and
after each phase a separate **blind independent verifier** leaf confirms the work. Every
leaf — developer or verifier — is launched **through the supervisor** (`supervise.sh`),
never directly, so a hung or runaway leaf is killed instead of stalling the whole run. You
orchestrate the leaves, branch on their verdicts, narrate every phase and verdict to the
issue thread, and leave the result on a **draft PR** for a human to review and merge.

This slice lifts veri from a single criterion to a **full multi-criterion issue**, solved
by a **resumable loop** over a committed **ledger**, on top of everything earlier (blind
verification, the supervisor, and the two retry axes — the **revise loop** on a `REJECT`
and the supervisor's **stuck-retry**, all still in force):

- **Scope & plan → ledger.** The conductor decomposes the issue into a checklist of small
  steps — each one cycle's worth, aligned to an acceptance criterion — written to a
  committed per-issue **ledger** (`.tdd/issue-<n>.md`) that is the **source of truth** for
  which steps are done, and mirrored to the issue thread.
- **The cycle loop.** The conductor loops Red → Green → Refactor over the ledger's steps
  until every criterion is covered, checking each step off in the ledger **atomically with
  its green commit** so git and ledger never diverge.
- **Resume.** Re-running `/tdd <n>` reads the ledger and continues from the first
  unchecked step.

Hardened edges (#7) have since landed too, and are described below: the preflight
baseline bail, reverting only the half-done step, and deterministic cause classification.
Still **out of scope**: the loop and parallel rungs of the scope ladder. A step that
exhausts its revise budget, or a leaf that stays killed-stuck past the supervisor's
budget, **bails** — preserving completed steps' commits and classifying the cause
(process vs system).

## The two roles, and why the verifier is blind

- A **developer leaf** writes the failing test, the implementation, or the refactor. It
  is allowed to see everything: the issue, the repo, the prior phases.
- A **verifier leaf** confirms one developer claim. It is **blind**: it receives only the
  test, the issue's behavior spec, and the repo — never the developer's rationale — and
  it establishes ground truth by **running the test itself**. Blindness is enforced
  structurally: the verifier prompt is built by `build-verify-prompt.sh`, whose only
  inputs are the spec and the test path, so the developer's reasoning physically cannot
  reach it (see ADR-0003).

You — the conductor — must keep these roles distinct. Do **not** write the test or the
implementation yourself, and do **not** pass a developer leaf's explanation into a
verification.

## The scripts (this skill's `scripts/` directory)

Let `S=<base directory>/scripts`, where *base directory* is the path the harness printed
when this skill loaded (`Base directory for this skill: …/tdd`). It is the same
skill whether it lives in the target repo's `.claude/skills/` or is symlinked into
`~/.claude/skills/` for use from any repo — never assume a repo-relative path. All leaf
machinery lives there and is unit-tested (`$S/tests/*.test.sh`):

`$S` is pinned: a run launched through `$S/run-conductor.sh` executes the skill snapshot —
the commit recorded in `.tdd/issue-<n>-skill-commit` and exported to every leaf as
`VERI_SKILL_COMMIT` — not the clone's current tip, so a PR landing on `main` while you work
does not change the scripts and templates under a running conductor (see *The skill
snapshot* below). Every launch `supervise.sh` makes also writes the commit it ran under to
the event log (`.tdd/events.jsonl`, key `skill_commit`), so a run that took a newer skill
with `VERI_NEW_SKILL=1` is the sha changing partway down that file.

- `$S/supervise.sh <name> <cmd> [args...]` — **the leaf launcher.** Spawns `<cmd>` under a
  heartbeat + hard-timeout watchdog, owns the `.tdd/<name>.log` progress log, and returns
  the captured output on stdout. **Exit 0 = success, 1 = leaf-failure, 2 = killed-stuck**
  (hung past the heartbeat window or over the hard timeout, **after** its stuck-retry
  budget). A one-line status goes to stderr. Tunables: `VERI_HEARTBEAT` (silence window s,
  default 180), `VERI_TIMEOUT` (hard cap s, default 900), `VERI_STUCK_RETRIES` (extra
  attempts after a killed-stuck, default 1 — the **liveness** axis, independent of both the
  conductor's verdict-axis `REVISE_BUDGET` and its cost-axis `VERI_REFACTOR_BUDGET`).
  Three more choose the **model** each leaf runs on, resolved here through
  `$S/leaf-model.sh` and passed to `claude --model`: `VERI_MODEL` (every leaf),
  `VERI_MODEL_DEVELOPER` (developer leaves only — `develop-*`, `revise-*`) and
  `VERI_MODEL_VERIFIER` (verifier leaves only — `verify-*`, `verify-pin` included). A role
  variable beats `VERI_MODEL`; all three unset means no `--model` flag at all, which is the
  default. The value goes through verbatim, so an alias (`sonnet`, `opus[1m]`) or a full id
  (`claude-sonnet-5`) both work.
  Because leaves **stream** (below), the default
  `VERI_HEARTBEAT` is a real silence window — a working leaf keeps it fresh, a genuinely
  hung one trips it — so just use the defaults; no need to pin heartbeat to the timeout.
  **Every leaf is launched through this — never call `run-leaf.sh` or `claude` directly.**
  It records its own final code in the completion file `.tdd/<name>.exit` on **every** path,
  killed-stuck included — that is what makes a detached launch waitable. And because a
  killed-stuck leaf is relaunched (`VERI_STUCK_RETRIES`), one call can take **more than one**
  `VERI_TIMEOUT` of wall time, which is why the wait below loops rather than naming one long
  timeout.
- `$S/detach-leaf.sh <cmd> [args...]` — **the detaching half of a detached launch.** Runs
  `<cmd>` as the leader of a **new session**, and so of a new process group, then returns at
  once. Every leaf launch below goes through it, and none uses `nohup` — *Launching a leaf*
  says why. Redirections go on the call as usual — the launched process inherits them.
- `$S/wait-leaf.sh <name> [max-seconds]` — **the foreground half of a detached launch.**
  Blocks polling for that completion file and exits with the code recorded in it as soon as
  it lands (0 / 1 / 2, the launcher's own contract), or **exit 3** — nothing to report yet —
  once `max-seconds` pass with no completion file. The default is 540 s, comfortably inside
  Claude Code's 10-minute cap on a single foreground Bash call. On a **3, call it again**:
  the leaf is still running. A 3 with no leaf running means no result was ever recorded —
  never success. A **2** also means the supervisor died without recording a status: no
  completion file, and the pid in `.tdd/<name>.pid` no longer runs a supervisor for that
  name. It takes the killed-stuck branch like any other 2.
- `$S/run-leaf.sh <prompt-file|-> [claude args...]` — the inner leaf invocation. Runs
  `claude -p --output-format stream-json` so the leaf **streams events as it works** (that
  is the supervisor's heartbeat), then appends the clean final result. You always run it
  *via* `supervise.sh`, not on its own.
- `$S/extract-result.sh` — pulls the final result text out of a leaf's stream-json (used
  by `run-leaf.sh`; passes plain text through unchanged).
- `$S/build-develop-prompt.sh <phase> …` — assemble a **developer** leaf's prompt from a
  versioned template: `red <spec-file> <step-text> <test-cmd>`, `green <spec-file>
  <step-text> <test-cmd> <test-path> <target>`, `refactor <spec-file> <step-text>
  <test-cmd> <touched-files>`, `revise <phase> <spec-file> <step-text> <test-cmd>
  <reason-file>`. Prints the prompt on stdout; **exit 2** with a diagnostic and **no
  stdout** on an unknown phase or a missing template, spec or reason file — never a partial
  prompt. The mirror of `build-verify-prompt.sh` and its opposite in emphasis: the verifier
  builder is defined by what it **cannot** carry (no rationale parameter, so blindness is
  structural), this one by what it **must** carry — the same instructions on every run of a
  phase, with only the variables changing. **Build every developer prompt with it**; a
  phase's instructions live in its template, not in prose you improvise per cycle.
- `$S/build-verify-prompt.sh <red|green|refactor|pin|plan> <spec-file> <test-path> [target]` —
  assemble the blind verifier prompt. Used by `verify.sh`; you rarely call it directly.
- `$S/verify.sh <red|green|refactor|pin|plan> <spec-file> <test-path> [target]` — the **verify
  verb**: build the blind prompt → launch the verifier leaf **through the supervisor** →
  parse the verdict. Prints the verifier's **reason** on stdout; **exit 0 = PASS, 1 =
  REJECT, 2 = malformed or killed-stuck**. The `pin` phase is the *already satisfied*
  check: the verifier confirms the test passes now, **fails** under a behaviour-removing
  mutation it applies and then reverts itself, and is behaviour-level — the same trivial
  / over-coupled / too-complex bar as `red`.
- `$S/run-verdict.sh [--step "<STEP>"] [--fast-cmd '<cmd>'] <red|green|refactor|pin|plan> <spec-file> <test-path> [target]`
  — the **verdict launcher**: `verify.sh`'s own call, argument for argument, reached as a
  command rather than as a shell string. This is what `supervise.sh verdict-<phase>` runs;
  it passes every argument through untouched and `exec`s the verify verb, so the step title
  travels in argv and its exit code is `verify.sh`'s.
- `$S/parse-verdict.sh` — extracts `PASS|REJECT` + reason from a leaf's output (used by
  `verify.sh`).
- `$S/tick-criterion.sh "<substring>"` — the pure text transform both tick wrappers
  delegate to: reads a checkbox body on stdin, flips the first unchecked `- [ ]` matching
  the substring, writes it back on stdout. **Exit 3** if nothing matched.
- `$S/tick-issue-criterion.sh <n> "<substring>"` — tick a criterion checkbox in the
  issue body (the human-facing mirror).
- `$S/next-unchecked.sh < .tdd/issue-<n>.md` — print the **first unchecked ledger step**'s
  description; **exit 3** when none remain (the loop-done / nothing-to-resume signal).
- `$S/tick-ledger.sh [--refactor-pending] .tdd/issue-<n>.md "<substring>"` — check a step off
  in the **committed ledger**, in place (staged + committed together with that step's green
  code). **Exit 3** if no unchecked step matched the substring — the file is left untouched,
  so a green commit that ticked nothing says so instead of reading as done.
  `--refactor-pending` appends ` ⟂ refactor pending` to that same line in the same write, so
  the green commit records the step as **green but not yet tidied**; that is the flag the
  green PASS ticks with, and the one the pin path must tick without — a pinned step runs no
  refactor loop, so a mark left there would never be cleared.
- `$S/next-pending-refactor.sh < .tdd/issue-<n>.md` — print the **first ticked step whose
  refactor is unverified**: the description of the first `- [x]` step carrying the
  ` ⟂ refactor pending` mark, with the mark stripped, so what comes back is the same text
  `next-unchecked.sh` hands the loop and the tick wrappers match on. **Exit 0** when it
  printed one; **exit 3** with empty stdout when no step carries the mark — every green step
  has been tidied, so a resume has no refactor loop to re-enter.
- `$S/clear-refactor-pending.sh .tdd/issue-<n>.md "<substring>"` — the counterpart of
  `tick-ledger.sh --refactor-pending`: **strip the ` ⟂ refactor pending` mark** from the first
  ticked step matching the substring, in place, once that step's refactor has been verified.
  Nothing on stdout. **Exit 0** when it cleared the mark; **exit 3** when no ticked step both
  matched and carried it — the file is left byte-identical, because nothing is written unless
  the transform found its line.
- `$S/add-ledger-step.sh <ledger> after|before "<anchor substring>" '<text>' […]` — **grow
  the plan mid-run**: insert each text as `- [ ] <text> ⟦added⟧ ⟦criterion k⟧` directly after
  the anchor step, or directly before it, inheriting the anchor's criterion. `VERI_STEP_GROWTH`
  (default 3) bounds how many `⟦added⟧` steps one ledger may hold, on a **fifth axis** of its
  own — plan growth, never merged with the other four. **Exit 0** = inserted; **exit 1** = the
  budget cannot hold them, so nothing is inserted and every text is appended as a plain bullet
  under a trailing `## Owed steps` heading instead; **exit 2** = the anchor matches no step or
  more than one, or the budget is unreadable, with the ledger left byte-identical. Every text
  one growth is made of goes in **one call**: the script takes them all at once and reads the
  budget once per call, so a call per text would refuse a third text that one call either fits
  whole or files whole. Every insertion is marked in the log beside the call it made —
  `VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/next-pending-refactor.sh < .tdd/issue-<n>.md || $S/next-unchecked.sh < .tdd/issue-<n>.md)" $S/event.sh step-added
  anchor='<anchor>' added=<count>` — because a plan that changes with no record leaves the
  log unable to say which steps the run chose for itself; an exit 1 owes the same mark with
  `added=0`, since a step the budget refused is still a decision the run made.
- `$S/classify-bail.sh <cause>` — deterministically classify a bail cause
  (`killed-stuck`/`no-verdict` → `system`, `revise-exhausted` → `process`; unknown → exit
  non-zero). Used in the *Bailing* step so the classification is consistent, not ad-hoc.
- `$S/stop-requested.sh [--clear]` — **has an operator asked this run to stop, and how?**
  Run from the worktree, it reads `.tdd/stop`. **Exit 0** = a stop was requested: the mode —
  `at-ledger`, `at-leaf` or `now` — is printed on stdout and nothing else, so capture it and
  enter *Stopping* with it. **Exit 3** = no request, nothing on stdout; carry on. **Exit 2** =
  the file's first line is not one of the three modes, or an argument the script does not
  take: nothing on stdout, the complaint on stderr, `.tdd/stop` left as it was. `--clear`
  removes `.tdd/stop` and exits 0 whether or not it was there — the last act of *Stopping*.
- `$S/refactor-budget.sh <count>` — **bound the refactor loop**, so a step costs the same on
  every run. Given the number of transforms applied so far this step, it decides whether
  another one may run: **exit 0** = still under budget (launch the next transform leaf),
  **exit 3** = budget spent (stop the loop, go to verify-refactor), **exit 2** =
  `VERI_REFACTOR_BUDGET` is not a whole number ≥ 0 — a misconfigured run, with a diagnostic
  on stderr and **nothing on stdout**, fail-closed the way `classify-bail.sh` is on an
  unrecognised cause. A one-line status goes to stdout on 0 and 3 alike (`refactor 5/5 —
  budget spent`), so your narration can mirror it. `VERI_REFACTOR_BUDGET` (default 5) is a
  **third** tunable on a **third axis**: `VERI_STUCK_RETRIES` is liveness (the leaf never
  answered), `REVISE_BUDGET` is verdict (it answered and was rejected), this one is **cost
  per step** — how much tidying one step is worth, decided once for the run instead of by
  your judgement mid-loop.
- `$S/event.sh <event> [key=value …]` — append one JSON line to the run's event log
  `.tdd/events.jsonl`, relative to the worktree you are in. `supervise.sh` and `verify.sh`
  call it from inside themselves, so their events are complete by construction; **your**
  marks — `step-start`, `step-done`, `pin`, `revise`, `bail`, `done`, `resume` — are prose,
  so each is prescribed below at the point the matching narration is, and the run's context
  (`VERI_ISSUE`, `VERI_ACTOR=conductor`, `VERI_STEP`, `VERI_PHASE`, `VERI_ATTEMPT`) rides on
  the call in the environment. The log is run state: it is ignored, never committed, and
  goes with the worktree.
- `$S/metrics.sh <n>` — the event log's **reader**: prints on stdout one markdown
  `### 📊 Metrics` report of what solving issue `<n>` cost — attempts, verdicts, kills,
  retries and budgets spent, per phase and per step. Everything it knows comes from
  `.tdd/events.jsonl` in the worktree you are in, so it is called there and at the end, once
  the marks it reads have all been written. The conductor both commits its output beside the
  ledger and pastes it into the issue thread (the *Draft PR* step, and *Bailing*): a run that
  never calls it leaves the figures computable and uncomputed, which from the issue thread is
  indistinguishable from not having them.
- `$S/over-budget.sh <tier> <seconds> <usual>` — say whether one recorded test-command run
  was slow enough to be worth a word: **exit 0** = over budget, **exit 1** = not, **exit 2** =
  `VERI_UNIT_BUDGET` or `VERI_TIME_WARN_RATIO` cannot be read (the same misconfiguration
  step 5's `time-budget.sh` preflight refuses). On exit 0 it prints **exactly one line**,
  carrying a ⏱; on exit 1 it prints nothing at all. **Paste that ⏱ line verbatim into that
  phase's narration** in the issue thread, and do nothing else with it: **nothing branches on
  this check** — not the phase's verdict, not a retry, not a bail. A slow run is a remark, and
  a run that is not slow leaves you an empty capture and therefore nothing to paste.
- `$S/capture-spec.sh <n>` — the **blind spec**, on stdout: the issue's body, plus a `## Bug`
  section carrying its what-happened, expected, steps to reproduce and environment when the
  issue carries the `bug` label (and nothing extra when it does not). Redirect it into
  `.tdd/issue-<n>-spec.md` (step 3). Exit 2 on a missing issue number.
- `$S/ensure-run-state-ignored.sh [repo-root]` — make the **target repo** ignore veri's run
  scratch (`.tdd/*.log`, `.rc`, `.prompt`, `.reason`, the blind spec) while keeping the ledger
  tracked. Writes the rule to **both** the worktree's `.gitignore` (committed, so the first
  `git add -A` never sweeps leaf logs into history) and the shared
  `$(git rev-parse --git-common-dir)/info/exclude` (never committed, read by every worktree,
  so the caller's checkout — still on the default branch — stops reporting `.tdd/` as
  untracked). Idempotent in both files; the word on stdout reports the `.gitignore` only,
  `added` when it wrote the rule there, `already present` when it was there — the exclude
  file is ensured either way. Run once per issue right after entering the worktree (step 1).
- `$S/issue-worktree.sh <n> <slug>` — the **linked worktree the issue branch lives in**.
  Creates (or hands back) `<repo-root>/.tdd/wt/<n>` on branch `tdd/<n>-<slug>`, cut from
  **`origin/<default>` as just fetched** — never from the caller's `HEAD`, and never from the
  **local** branch of that name: that one **lags the remote by design**, since a run executes the skill pinned from
  `origin/<default>` and nothing obliges anyone to pull the primary clone, so a branch cut
  from it starts **stale** and its PR then owes a rebase over everything that landed meanwhile.
  The fetch moves no local branch and touches no working tree. A local `main`/`master` is the
  fallback on two separate axes: it supplies `<default>`'s **name** when the clone records no
  `origin/HEAD` (an origin does not guarantee one), and it is the **base** itself when there is
  **no remote** at all, as before. Prints the worktree's **absolute path on stdout** — the only
  thing on stdout; git's chatter goes to stderr, so the path is safe to capture.
  **Idempotent**: a second call for the same issue prints the same path and creates nothing,
  which is what makes a resume land in the worktree the first run made — an existing issue
  branch is checked out as it is, with no fetch. **Exit 0** = the path. **Exit 2** = no answer
  could be obtained — either the branch is **already checked out in another worktree** (it names
  that path and touches nothing: **never steal a checkout**, another conductor owns that run),
  or the default branch cannot be named, or fetching it failed — never a silent fallback to the
  stale local ref. And exit 2 when the worktree it would have handed back **holds a live
  conductor**: `.tdd/conductor.pid` there names a process that still answers `kill -0`, so it
  names that pid instead of printing the path (#170) — a second conductor `cd`'ing into a live
  run's worktree reads that run's ledger as its own and *Resume* throws the live leaf's
  uncommitted work away. A **dead** pid is a bailed or killed run, still a resume, still the path.
  `$S/issue-worktree.sh --remove <n>` removes the worktree once the PR has landed, and
  **refuses** (exit 2) one holding uncommitted changes.
- `$S/detect-test-command.sh [--issue <body-file>] [repo-root]` — print the one command that
  runs the **target repo's** full suite on stdout; **exit 3** — the repo-wide *nothing to do*
  code — when no marker it trusts matched, which is your cue to ask the user. First match
  wins: the issue body's own `Test command:` line, then the repo's `.veri/test-command`,
  then every inference (see *Detecting the test command*).
- `$S/solvable-issues.sh [--repo <owner/name>]` — the **selection layer**: prints the
  numbers of the issues veri may take right now — open, labelled `ready-for-agent`, every
  issue under their `## Blocked by` heading closed, and not already claimed by an open PR
  saying `Closes #<n>` — one per line, in three bands: the issues labelled `priority` first,
  then the `bug`s, then the rest, each band ascending by number. The band only reorders that
  set, it never enlarges it — the four conditions run first, so a `priority` issue that is
  blocked, claimed or not opted in is still not printed. `VERI_PRIORITY_LABEL` names the
  first band's label (default `priority`; set-but-empty is **exit 2**, like `VERI_LABEL`),
  and the second band's is GitHub's own `bug`. **Exit 0** when it printed at least one,
  **exit 3** with empty stdout when none is takeable (nothing to do, not an error).
  `VERI_GH_JSON=<dir>` reads `issues.json` / `prs.json` fixtures instead of shelling out to
  `gh`, which is what makes it testable with no network. The conductor does not call this —
  it is rung 2's, driven by the loop branch of this skill.

## Launching a leaf — detach, then wait in the foreground

Every leaf launch below has the same three-part shape — clear the completion file, launch
detached, wait in the foreground — and each phase spells it out in full. A **developer
leaf** (red, green, refactor, revise) is launched straight through the supervisor:

```
rm -f .tdd/<name>.exit .tdd/<name>.pid
VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/next-pending-refactor.sh || cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" $S/detach-leaf.sh $S/supervise.sh <name> <cmd> [args...] > .tdd/<name>.out 2> .tdd/<name>.err
$S/wait-leaf.sh <name>
```

The `rm -f` first, because the completion file is named for the **phase**, not the cycle: a
`.tdd/develop-red.exit` left by the previous step's red leaf would end the next wait
instantly, with the previous cycle's code — and a `.tdd/<name>.pid` left the same way, naming a
supervisor long gone, would end it with a 2 before the new supervisor wrote its own. Then the launch, **detached** — through
`detach-leaf.sh`, so the call returns at once and the leaf runs in a **session of its own**.
Then `wait-leaf.sh` in the **foreground**, which blocks until the leaf finishes and exits
with its code. On **exit 3** the leaf is still running and you have only spent the wait's
budget: **call `wait-leaf.sh` again**, as many times as it takes. Only a 0, 1 or 2 is an
answer. Read the leaf's report from `.tdd/<name>.out` — the captured stdout — instead of
from the launcher's stdout, which the detached call no longer hands you.

Never `nohup … &` in place of that detach: `nohup` makes the leaf ignore a hang-up (SIGHUP),
but it leaves it in the **process group** of the Bash call that launched it, so a harness
that signals that group when the call ends takes the leaf with it. A leaf killed that way
writes no completion file, so the wait above returns exit 3 forever and you read that as
"still running" — the run stalls with nothing to say why.

**Before every leaf launch, ask whether a stop was requested: run `$S/stop-requested.sh`**
ahead of the `rm -f`, for a developer leaf and a verifier alike. On exit 3 no stop is
pending: launch as normal. On exit 0 branch on the mode it printed — `at-ledger` launches the
leaf anyway, because every leaf between two ledger commits is on the way to the next one, and
`at-leaf` or `now` launch nothing and go to *Stopping*. On exit 2 treat it as a stop in mode
`at-ledger`, narrating that the request was unreadable: a `.tdd/stop` exists, so somebody
meant to stop this run, and only how urgently is in doubt — the mode that cannot be wrong is
the one that loses nothing.

**Before reading any leaf's exit 2 as killed-stuck, run `$S/stop-requested.sh`.** A `now`
stop kills the live leaf, so its wait comes back 2 exactly as a hung leaf's does: a pending
`now` explains the 2, and the run goes to *Stopping* instead of *Bailing*. Any other answer
leaves the 2 to be read as the phase below reads it.

The launch carries `VERI_TEST_CMD`: the run's test command, reaching the leaf through its
**environment** rather than its prompt, so the verifier stays blind. It is a prefix on the
launch line and not a one-off `export` because every Bash call you make is a fresh shell, so
nothing set in preflight survives to a launch three steps later.

It carries `VERI_ISSUE` and `VERI_STEP` for the same reason, and they are the same two
values your own marks below spell: the supervisor's `launch` and `exit` events and the
verifier's `verdict` event are written by `event.sh`, which reads the run context out of
the environment it is called in. Nothing downstream can supply it — `leaf-role.sh` derives
the actor, the phase and the attempt from the leaf's **name**, and no name says which issue
is being solved or which step of its plan the leaf is on — so a launch that omits them
leaves every one of that leaf's events with an empty `issue` and an empty `step`, and a
reader can attribute the leaf to a step only by interleaving timestamps with `step-start`.

**The step's title reaches a command line as data, never hand-typed into it where a
script can read it instead.** Double quotes stop an apostrophe but not an expansion: a
`$`, a backtick or a `"` in the title is substituted, run or cut short inside `"<STEP>"`,
silently, and the run carries on with a title nobody wrote (#437). So every leaf's
launch reads `VERI_STEP` out of the committed ledger inside its own command substitution —
`next-unchecked.sh` before the step's green commit ticks it, `next-pending-refactor.sh`
after, and `next-pending-refactor.sh || next-unchecked.sh` where the phase could be either —
and a verifier's launch reads `--step` the same way, so the title never passes through the
line as text. The conductor's own lines read it the same way: every `event.sh` mark's
`VERI_STEP` and `anchor=`, every `preserve-attempt.sh` call, and the matcher `tick-ledger.sh`,
`clear-refactor-pending.sh` and `tick-issue-criterion.sh` are handed to find the checkbox
they tick — once the step is ticked and cleared, as the last `- [x]` line of the ledger.
`tick-issue-criterion.sh` is the exception: it ticks the **issue body**, whose criteria are
the issue's own words and not the ledger's reworded steps, so its matcher is criterion k's
first line read out of that body's `## Acceptance criteria` — still data, never retyped. Where a
command still spells the title, it is in double quotes — `"<STEP>"`.
One rule, because the title is the planning leaf's own English and an apostrophe is
ordinary in it: a single-quoted `'<STEP>'` closes on that apostrophe — *that shell's
stderr* becomes `'that shell'` followed by junk — and the line dies in the shell you type
it into, before anything is launched (#431). A fragment fails the same way one argument
over: `'that shell'` again, and again before anything runs. Inside double quotes an
apostrophe is an ordinary character. The other placeholders on those lines stay
single-quoted; they are paths, commands and ids, and none of them carries the planning
leaf's prose.

A **verifier** (`verify.sh`, which goes through the supervisor too) takes the same shape
with one wrinkle: the verify verb is reached through `run-verdict.sh`, the **verdict
launcher**, rather than typed into a `bash -c "…"` command string. The string is what broke
on a step title carrying an apostrophe (#426) — `--step '<STEP>'` inside a `"…"` closes on
the title's own `'`, and the launch dies before any verifier runs. The launcher takes the
title as one element of its argv and hands it on as one element of `verify.sh`'s, so no
second shell ever parses it —

```
rm -f .tdd/verdict-<phase>.exit .tdd/verdict-<phase>.pid
VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/next-pending-refactor.sh || cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" $S/detach-leaf.sh $S/supervise.sh verdict-<phase> $S/run-verdict.sh --step "$(cat .tdd/issue-<n>.md | $S/next-pending-refactor.sh || cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" <phase> … > .tdd/verify-<phase>.reason 2> .tdd/verify-<phase>.err
$S/wait-leaf.sh verdict-<phase>
```

— named `verdict-<phase>`, never `verify-<phase>`, which the verifier leaf's own supervisor
already owns. `run-verdict.sh` **execs** the verify verb, so the code the supervisor sees is
`verify.sh`'s own and the completion file it records is the verdict. `wait-leaf.sh` then returns **the verdict**: 0 PASS, 1 REJECT, 2 malformed or
killed-stuck. The reason is read back from `.tdd/verify-<phase>.reason`, the file the revise
step takes as a path.

Supervising that wrapper gives the wait a second way to end, and it is the one a developer
leaf's **2** already means: `wait-leaf.sh verdict-<phase>` also exits **2** when that
supervisor died without recording a status — nothing wrote the completion file, so there is
no verdict behind the code and `.tdd/verify-<phase>.reason` is empty or left over from an
earlier attempt. Read it as a **killed-stuck** verifier, exactly as *Develop (red)* reads a
killed developer leaf: **bail** cleanly (see *Bailing*), do not retry, and do not quote the
reason file for a verdict nothing wrote.

**Never launch a leaf in a background Bash call and then wait for its notification.** The
conductor often runs as a print-mode session (`claude -p "/tdd <n>"` — one of the two
unattended modes below), and in print mode that notification never arrives: the turn ends, the
`claude -p` process exits, and the leaf is orphaned. The supervisor keeps running it under
`.tdd/`, but nothing will ever read its result, tick the ledger or narrate the outcome (this
is how #70 was lost). The detach-then-wait shape behaves identically interactively and
unattended, so it is the only one this procedure uses.

## Launching the conductor

`/tdd <n>` is a skill, so it can be typed inside an interactive Claude Code session. Every
leaf is a `claude -p` subprocess, and a session the operator is already in is the situation a
guard on nested launches refuses; when one fires, every leaf of the run dies at launch. If it
does, run the conductor from a plain shell **outside** any Claude Code session instead —
`claude -p "/tdd <n>"`.

**veri never unsets `CLAUDECODE`, or any other such guard, itself.** The binary's refusal
names the risk it is declining — nested sessions share runtime resources and will crash all
active sessions — and those are the operator's sessions, not veri's. Unsetting the variable
in a launcher would spend that risk on their behalf without their knowledge, so preflight
refuses and says what to run instead, and leaves the decision where it belongs.

**Three launch modes, and which one to pick.** `/tdd <n>` typed into an **interactive**
Claude Code session is the one to use when you intend to watch the run and steer it — and
only from a session that is not itself inside another one, per the guard above. The two
unattended modes both run the conductor in **print mode**: `claude -p "/tdd <n>"` typed by
hand, and `$S/run-conductor.sh <n>`, which builds that same command line — the procedure as
the prompt, the streaming flags, `--permission-mode bypassPermissions`, and the parent
session's handles severed — and is what an unattended or scheduled launch should call.

**Interactive or print mode is a trade you pick per run.** An interactive conductor can be
steered — asked a question, redirected, interrupted mid-run — and costs ~25,000 tokens a
request more, the harness surface an interactive session re-sends on every request (#207,
recorded at `run-conductor.sh:7`). A print-mode conductor is that much cheaper per request,
and cannot be steered: there is no human on the other end of its turn, so every decision the
procedure would put to an operator becomes a bail instead — it stops and says why, and you
read that afterwards rather than answering it at the time.

**The skill snapshot: a run executes one skill from its first launch to its last.**
`$S/run-conductor.sh <n>` does not run the skill as it sits in the clone. It fetches `origin`,
records the default branch's tip in `.tdd/issue-<n>-skill-commit` on a run's first launch,
and runs every launch — the first and each resume — from a snapshot of that commit
(`git archive` into a temporary directory), so a pull between two launches never changes the
skill mid-run. The record is run state and is git-ignored. Two cases refuse rather than guess:

- **A recorded commit the launching clone cannot resolve** (a second clone, a shallow one, a
  pruned branch) is exit 2, never a silent re-pin to whatever the clone holds.
- **Taking the new skill is an explicit act:** `VERI_NEW_SKILL=1` on a resume replaces the
  recorded commit with the fresh tip and writes a `skill-repin` event to the run worktree's
  `.tdd/events.jsonl`, where `metrics.sh` reads it.

When no commit can be resolved at all the launch runs unpinned, says so on stderr, and hands
the conductor `VERI_SKILL_UNPINNED=1` for the plan comment (step 2.4).

## Inputs

There is one command, so what the user typed after it is what decides which of the two
procedures below runs. No shape of argument is ever a question to put back to the user: a
word that is not a number is never a malformed issue number, and an empty argument is never
a missing one. Read the first word of `$ARGUMENTS` and resolve it three ways — there is no
fourth case:

- **An integer** — it is an issue **number** `<n>`, and this invocation is the
  single-issue procedure: run *Procedure* below on that issue, end to end.
- **Any other word** — it is a **scope** to drain: `Read` this skill's `SCOPE-LOOP.md`
  (beside this file, at `<base directory>/SCOPE-LOOP.md`) and run *Draining a scope — the
  loop* from it. That loop selects the issues in that scope and runs the single-issue
  procedure over them one at a time. It lives in its own file because only this branch ever
  executes it, and an integer argument takes *Procedure* and never comes back — so keeping
  it here would bill every single-issue conductor for procedure it will not read (#202).
- **No argument at all** — a bare invocation is the scope `plain`, so it takes the scope
  branch above with `plain` as its scope.

A session born as a **worker** `<name>` takes none of those three: `Read` this skill's `WORKER.md`
(beside this file, at `<base directory>/WORKER.md`) and run *The worker loop* from it, which
works the issues the work queue assigns to `<name>` through the single-issue procedure. It
lives in its own file for the same reason `SCOPE-LOOP.md` does: only a worker ever reads it.

## Procedure

Work through these steps in order. If a **preflight** step fails, stop and tell the user
what is wrong — do not start a cycle on a poisoned baseline. Once the cycle is underway,
drive it to a draft PR or to a clean stop on a `REJECT`.

### 0. Preflight — baseline checks (bail before any cycle)

These run **first**, before any branch or cycle. If any fails, the baseline is poisoned —
**bail immediately**: report which check failed and stop. This is a degenerate bail (no
branch, no commits, nothing to revert or push) — just refuse to start. A red, dirty, or
unauthenticated baseline never gets a cycle.

1. **Git repo & clean tree.** `git rev-parse --is-inside-work-tree` succeeds and
   `git status --porcelain` is empty. If dirty, stop and ask the user to commit or stash.
   The run no longer commits in this checkout — step 1.2 moves into a worktree that is clean
   by construction — but the check **stays**: the conductor still reads the issue and the
   default branch from here, and a dirty caller's checkout means something else is mid-work
   in it.
2. **`gh` and `claude` authenticated.** `gh auth status` succeeds, and `claude auth status`
   reports `"loggedIn": true`. Every leaf is a `claude -p` subprocess: with an expired
   session each one fails at launch (`supervise.sh` exit 1 before any work), which is
   neither a verdict nor a hang and so has no bail classification — catch it here.
   Then run `$S/leaf-launchable.sh`, which asks the other half of the same question: not
   whether the binary would be *allowed* to work, but whether it starts at all. **Exit 2**
   means it does not — a guard refused the launch, the case *Launching the conductor*
   above describes (#187) — and is a preflight-class stop: report its stderr diagnostic
   verbatim and do not start. It runs **here**, before step 3, because the baseline is the
   expensive half of preflight and is wasted either way when no leaf can launch; a run that
   discovers this later has already paid for the suite, the worktree, the spec and a public
   `### ▶️ Resuming` comment on the issue thread.
3. **Suite is green at baseline — and time it.** The issue may name its own test command,
   so read its body first — into a temp file, since the caller's checkout must stay clean:
   ```
   body="$(mktemp)" && gh issue view <n> --json body -q .body > "$body"
   ```
   Then get the fast tier's command from `$S/detect-test-command.sh --tier fast --issue "$body"`
   (see *Detecting the test command*) and run it. If already red, stop and report — a cycle must
   not start on a red baseline. Reading the body **here**, before the baseline runs, is what
   keeps the baseline and every later leaf on one command: detected after the baseline, the
   issue's line would arrive too late to be the command the baseline proved green. Note how
   long the run took and keep it as `baseline`, the elapsed wall time in whole seconds
   (round up). This measurement is free — the run happens anyway — and it is taken once, so
   a suite that gets slower mid-run does not move the timeout under a leaf.

   **Then time the full tier too.** Get its command from
   `$S/detect-test-command.sh --tier all --issue "$body"`, run it once, and keep its elapsed
   wall time in whole seconds (round up) as `full`; step 7 sizes the run's hard timeout from
   that number, not from `baseline`. The full-tier run is the work a leaf actually does — a
   verifier runs this very command and a developer leaf runs the suites covering the files it
   touched — while no leaf runs the fast tier at all, so a timeout timed off the fast one
   bounds work nobody does: that is how #300's green leaf was killed at the 900 s floor
   twice over while it was working. It is timed here, with the same single-measurement rule,
   and costs one full-tier run the Draft PR gate pays for anyway. If it is red, stop and
   report, for the same reason a red fast tier stops the run.
4. **Default branch.** Capture it for the PR base:
   `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`.
5. **Tunables parse.** Run `$S/refactor-budget.sh 0` once. **Exit 2** means
   `VERI_REFACTOR_BUDGET` is not a whole number ≥ 0 — stop and report its stderr diagnostic
   verbatim. A budget that cannot be read is a poisoned baseline like a red suite, not a
   decision, and catching it here is what lets the refactor loop treat exit 2 as impossible.
   Exit 0 and exit 3 both mean it parses (3 only says the budget is 0 — a run with the
   refactor loop switched off), so continue.

   Then the plan-growth budget, which `add-ledger-step.sh` reads the same way: it must be
   unset, or a whole number ≥ 0. There is nothing to run, since that script refuses an
   anchor it cannot find before it ever looks at the budget, so read the value here:
   ```
   [[ -z "${VERI_STEP_GROWTH+x}" || "$VERI_STEP_GROWTH" =~ ^[0-9]+$ ]]
   ```
   False — anything else, **including set-but-empty** — is the same **exit 2** as a bad
   `VERI_REFACTOR_BUDGET`: stop and do not start, reporting the value verbatim. Caught here
   it costs nothing; left to the first leaf that tries to grow the plan, it surfaces as a
   refused insertion mid-cycle, with the branch, the worktree and the plan already built.

   Then the two money budgets: run `$S/step-budget.sh` once, with no arguments. **Exit 2**
   means `VERI_STEP_BUDGET` or `VERI_RUN_BUDGET` is not a non-negative decimal number — the
   same preflight-class stop as a bad `VERI_REFACTOR_BUDGET`: report its stderr diagnostic
   verbatim and do not start, before any leaf is launched. Exit 0 prints the step budget,
   then the run budget, one per line.
6. **Leaf models parse.** Run `$S/leaf-model.sh develop-red` and
   `$S/leaf-model.sh verify-green` once each. Both roles, because the three variables do not
   all reach both: `VERI_MODEL_DEVELOPER` is only ever read for a developer name and
   `VERI_MODEL_VERIFIER` only for a verifier one, so a preflight that asked a single name
   would let the other role's bad value through and kill every leaf of that half at launch.
   **Exit 2** means the value cannot be a model name — whitespace in it, so `sonnet 5` is two
   words where the CLI takes one — and is a preflight-class stop like step 5: report its
   stderr diagnostic verbatim and do not start. The resolver is otherwise first called at
   launch, by which time the branch, the worktree and the plan already exist and a typo costs
   a bail to undo. An empty print is the normal answer for a run that chose no model, so exit
   0 with nothing on stdout means continue.
7. **Size the run's hard timeout from the full-tier measurement.** Hand step 3's `baseline`
   and its `full` measurement to `$S/leaf-timeout.sh` and **export** the result, so every
   leaf of the run is launched under it rather than under the supervisor's fixed 900 s
   default:
   ```
   timeout="$($S/leaf-timeout.sh "$baseline" --full "$full")" && export VERI_TIMEOUT="$timeout"
   ```
   `--full` says which of the two measurements the timeout is sized from: the full-tier one
   displaces the fast one rather than mixing with it, because a leaf runs the full tier and
   never the fast one.
   The script keeps a quick suite on today's 900 s and gives a slow one 6 × its baseline —
   which is what stops a leaf whose own test command takes minutes being killed as stuck
   while it is working (#71: a 900 s cap against a 140-250 s suite, two bails, both steps
   reverted). Because the export is done here, in the conductor's own shell, it is in force
   for every `supervise.sh` in every phase of every cycle below; nothing else has to pass
   it. An explicit `VERI_TIMEOUT` is printed back as given, so setting one by hand still
   wins and the liveness axis stays yours. **Exit 2** means the number could not be read —
   a malformed measurement, or an explicit `VERI_TIMEOUT` that is not a whole number ≥ 1 —
   and is a preflight-class stop like step 5: report its stderr diagnostic verbatim and do
   not start, because a run whose timeout is garbage kills every leaf it launches.

### 1. Read the issue, enter the issue's worktree, capture the spec (or resume)

1. Read the issue: `gh issue view <n> --json number,title,body,url`.
2. **Derive the slug and enter the issue's worktree.** Slug from the title — lowercase,
   non-alphanumerics to `-`, collapse and trim `-`, cap to ~6 words. Then let the script
   make (or hand back) the worktree the issue branch lives in, and move into it:
   ```
   wt="$($S/issue-worktree.sh <n> <slug>)" && cd "$wt"
   ```
   Then **take the worktree**, before anything else you do in there:
   ```
   mkdir -p .tdd && printf '%s\n' "$PPID" > .tdd/conductor.pid && $S/stop-requested.sh --clear
   ```
   The `--clear` beside it drops a stale stop request a killed run never got to clear, so a
   `.tdd/stop` left behind cannot stop the run that resumes it at its first checkpoint.
   That lock is the **worktree guard**, and it guards this machine's worktree only: for
   exactly as long as the pid in there answers `kill -0`, `issue-worktree.sh` refuses this
   worktree to a second conductor on this computer, so none can land in a live run's tree and
   follow *Resume*, whose `git reset --hard HEAD` on a `⟂ refactor pending` step throws your
   leaf's uncommitted work away (#170). It is **not** the claim on the issue. A pid is a
   machine-local name, veri is developed from more than one computer, and `origin` is all they
   share: what keeps the issue out of `solvable-issues.sh`'s pool is the draft PR step 2.3
   opens as the first act after the plan commit — minutes from here, and open for the rest of
   the run, a bail included (ADR-0024). Until that PR exists this lock is the only mark of the
   run there is, which is why the window between this worktree and the plan commit is the one
   place two machines can still collide.
   Write **`$PPID`**, not `$$`: inside a tool call `$PPID` is your own process, which lives as
   long as this run, while `$$` is the shell of that one command — already gone when anyone
   reads the lock, so the guard would be dead on arrival, and the number may since have been
   handed to a stranger. **Nothing deletes it**: liveness is the whole rule, so a bail, a crash
   or a `kill` frees the worktree — never the issue, which its PR goes on holding — with no
   cleanup step to forget, and a resume overwrites the dead pid with its own here.
   **Every later step of the run happens inside that worktree**: the blind spec
   (`.tdd/issue-<n>-spec.md`), the ledger (`.tdd/issue-<n>.md`), every leaf log and prompt,
   every commit, the push and the PR. All the `.tdd/…` paths below are **relative to the
   worktree**, so once you have `cd`'d there they read exactly as written — do not prefix
   them with the caller's path.
   The **caller's checkout is left exactly as it was**, still on whatever branch it was on:
   it is never switched and never committed in. That is the point — a skill symlinked out of
   it or a dev server serving it must not silently start seeing the issue branch (ADR-0013).
   **Exit 2 is a preflight-class stop**, for any of the reasons the script's entry under *The
   scripts* enumerates — that entry is the one place they are listed, so this step cannot fall
   behind it. Report the script's diagnostic verbatim and **do not start** — no branch of your
   own, no cycle, nothing to revert.
3. **Write the behavior spec to a file** the verifier leaves will read — inside the worktree,
   which you are now in:
   `mkdir -p .tdd && $S/capture-spec.sh <n> > .tdd/issue-<n>-spec.md`.
   (The verifier is blind; this on-disk spec — never your narration — is what it sees.)
   What it writes is enumerated in its entry under *The scripts*, the one place that list
   lives, so this step cannot fall behind it. The extra `## Bug` section it adds for an issue
   labelled `bug` is there because a bug's Red is a reproduction (ADR-0015), and this file is
   the only channel the developer and the blind verifier have to learn what it must reproduce.
4. **Ignore run state.** `$S/ensure-run-state-ignored.sh` writes the same rule — ignore
   `.tdd/*` except the ledger — into **two** files, and needs both. Into the worktree's
   `.gitignore`, which is committed: if the script prints `added`, commit it as the branch's
   first commit, `git add .gitignore && git commit -m "chore: ignore veri run state (#<n>)"`;
   `already present` means that file already carried the rule, so there is nothing to commit.
   Without it, the atomic `git add -A` in Green would commit every leaf log and prompt, and
   the merged repo would be unsafe for the next `git add -A` too. And into
   `$(git rev-parse --git-common-dir)/info/exclude`, which the script ensures on every run
   whichever word it printed — a file git never commits and every worktree of the repo reads.
   That second write is what keeps `.tdd/wt/<n>` out of the **caller's** `git status`: the
   caller's checkout stays on the default branch for the whole run, so it never sees the
   `.gitignore` commit above, which lives only on the issue branch. Because `info/exclude`
   needs no branch and no commit, it is in force in the caller's checkout immediately — and
   preflight step 1, which refuses to start on a dirty caller's checkout, passes for the next
   `/tdd` without waiting for this one's PR to merge.
5. **Resume check.** If `.tdd/issue-<n>.md` (the ledger) already exists in the worktree, this
   is a **resume**: skip step 2 (the plan is already written), post a `### ▶️ Resuming`
   comment naming the next unchecked step, and go straight to the cycle loop (step 3).
   Otherwise continue to step 2 to scope and plan. This check needs no special casing for a
   re-run: `issue-worktree.sh` is **idempotent**, so a second invocation puts you back in the
   same worktree the first run built, with its committed ledger already on disk.

### 2. Scope & plan → the ledger

Decompose the issue into a **plan**: a checklist of small steps, each one cycle's worth and
aligned to an acceptance criterion. Surface sizing (note if a step looks too big to be one
cycle) but do **not** gate on it.

**Plan from the whole issue, not only its criteria.** `## Acceptance criteria` is the
primary alignment, but read `## What to build` (and any notes) as a second source and look
for gaps: a behaviour the prose asks for that no criterion covers still gets a step. Phrase
that step as a testable criterion of your own and add it to the ledger (it goes into the
plan comment with the rest) rather than dropping it silently. A behaviour left unplanned
surfaces mid-run as a plan amendment — a late extra step, or a verifier's remark — as it
did in #43's step 5 and #41's step 6, instead of at scoping time.

1. Write the plan as a checkbox list to the **ledger** `.tdd/issue-<n>.md`, e.g.:
   ```
   # Plan for #<n> — <issue title>

   - [ ] <step 1: a behaviour-level criterion, one cycle's worth> ⟦criterion 1⟧
   - [ ] <step 2: a gap step no criterion covers>
   ```
   Each step's text should be a distinctive, behaviour-level description — it doubles as the
   substring you will pass to `tick-ledger.sh`. Prefer the issue's own acceptance-criteria
   wording where it maps cleanly to one cycle. End each step's line with ` ⟦criterion k⟧`,
   where k is the 1-based position of the acceptance criterion it serves, and leave a gap
   step without one: `criterion-finished.sh` reads that notation to decide when the issue's
   criterion may be ticked.
2. **Commit the ledger** as the run's starting point:
   `git add .tdd/issue-<n>.md && git commit -m "plan: scope #<n> into <k> steps (#<n>)"`.
   (The ledger is committed — step 1.4 guaranteed `.gitignore` tracks `.tdd/issue-*.md`
   while ignoring leaf logs.)
3. **Push the branch and open the draft PR** — the run's claim, made as the first act after
   the plan commit, from inside the worktree:
   ```
   $S/push-branch.sh
   gh pr create --draft --base <default-branch> \
     --title "WIP: <type>: <criterion summary> (#<n>)" \
     --body "Closes #<n> — work in progress: <k> steps planned. The ledger .tdd/issue-<n>.md is the source of truth."
   ```
   An open PR saying `Closes #<n>` is the claim every other machine can see, and the plan
   commit is the run's first — a PR needs a commit ahead of the base, so this is the
   earliest the claim can be made. Until it exists a second machine running `/tdd <scope>`
   reads the issue as free and takes it again, as four unseen runs did on 2026-09-14. The
   title says **WIP** because a draft branch that reads as finished work is a second way to
   be misread; step 4 is where the PR is retitled and readied.
4. **Mirror the plan** to the issue thread: post a `### 🗺️ Plan` comment listing the steps,
   naming the test command preflight detected and every leaf will run, and noting that the
   ledger is the source of truth and each step will be blind-verified. The test command is
   in that comment so a wrong one is visible on the thread before the first leaf starts,
   rather than after a cycle has paid for it. The comment also states the hard timeout
   preflight step 7 settled on and where it came from, **naming the tier the measurement was
   of** — `timeout 1200 s (6 × a 200 s full-tier baseline)`, or `timeout 900 s (floor; 40 s
   full-tier baseline)`, or `timeout 900 s (VERI_TIMEOUT set by hand)` — so a reader of the
   thread can see which number every leaf of this run is under, why, and that it was timed
   against the work a leaf does rather than against the fast tier no leaf runs. On #71 that had to be reconstructed from the timestamps of two bails.
   Beside those two, the comment names the **skill commit** this run started on —
   `git -C "$S" rev-parse HEAD`, the version of the procedure and scripts you are executing.
   The thread is where a human reads a run back, so it is where the version has to be: a
   `### 🛠️ Refactor` comment describing work the run never did is indistinguishable from a
   true one without it, as #150's narration landing under #170's run was.
   When `VERI_SKILL_UNPINNED=1` is in your environment the launch found no skill commit to
   pin, and the comment says `unpinned` in place of a commit rather than naming none.

### 2b. Start comment

Post a short comment announcing veri has started, naming the branch (and the worktree it is
running in) and the number of plan steps, and noting each phase will be blind-verified:
`gh issue comment <n> --body "..."`.

### 2c. Verify the plan (blind)

The plan is the run's definition of done — `criterion-finished.sh` ticks the issue's
criterion from the ledger's own paraphrase of it — so it is verified once, here: after the
ledger is committed (before that there is no plan on disk to read) and before the first step
(a plan caught wrong after step 3 has already been paid for). The `plan` phase is blind like
the other four: its inputs are the issue spec and the proposed ledger, and nothing else. It
runs no tests, so it is the cheapest verification in the run.

```
rm -f .tdd/verdict-plan.exit .tdd/verdict-plan.pid
VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> $S/detach-leaf.sh $S/supervise.sh verdict-plan $S/run-verdict.sh plan .tdd/issue-<n>-spec.md .tdd/issue-<n>.md > .tdd/verify-plan.reason 2> .tdd/verify-plan.err
$S/wait-leaf.sh verdict-plan     # foreground; on exit 3 call it again
```

The third positional is the **ledger**, where the other phases pass a test path, and there
is no `--step`: the plan has no step under judgement yet. Note the wait's exit code — the
verdict — and read the reason back out of `.tdd/verify-plan.reason` to narrate it. Post a
`### 🗺️ verify-plan — PASS|REJECT` comment carrying that reason; it names any step the
verifier judged too big for one cycle whichever way the verdict went, so that observation
reaches the thread even on a PASS.

- **PASS (exit 0):** continue to the cycle loop.
- **REJECT (exit 1):** the plan is wrong, not the run — **rewrite the ledger** from the
  reason alone (it names the criterion and the part of it no step covers), commit the
  rewrite with `git add .tdd/issue-<n>.md && git commit -m "plan: rewrite #<n> after
  verify-plan REJECT (#<n>)"`, post the revised plan to the thread, and **re-verify** by
  running the launch above again. Rewrite and re-verify up to `REVISE_BUDGET` times; if the
  last re-verification is still `REJECT`, **bail** as a process failure (see *Bailing*) —
  the plan, not a leaf, is what the methodology rejected.
- **Malformed / killed-stuck (exit 2):** no verdict could be obtained — **bail** as a system
  failure (see *Bailing*), after the stop check in *Launching a leaf*. A plan nobody looked
  at is never a PASS.

### 3. The cycle loop

Loop until the ledger has no unchecked step. Each iteration runs **one full cycle** (Red →
Green → Refactor) for the next step; let **STEP** be that step's description:

```
$S/next-unchecked.sh < .tdd/issue-<n>.md        # exit 3 ⇒ all steps done → go to step 4 (PR)
VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/next-unchecked.sh < .tdd/issue-<n>.md)" $S/event.sh step-start
```

The `event.sh` line is this step's **mark** in the run's event log — the step has no issue
comment of its own, so the moment `next-unchecked.sh` hands one over is where its clock
starts. Every mark below is spelled the same way, with the run's context riding on the call
in the environment as *The scripts* sets out above, so one instruction carries the whole
call.

Run the Red, Green, and Refactor phases below **against STEP's criterion** (use STEP's
wording as the criterion the leaves pin, and as the `<substring>` for ticking). When a
step's cycle completes (refactor verified), loop back to `next-unchecked.sh` for the
following step. The phase sub-steps are:

#### The step's cost check

Every leaf of a step that runs **before its green commit** — develop-red, each verify-red,
each revise attempt of red or green, develop-green, each verify-green — is followed by
`$S/step-cost.sh '<STEP>'`: what the step's leaves have spent so far,
read off their `usage` events, against the step budget `step-budget.sh` printed in preflight.
The check runs only once that leaf has exited and `supervise.sh` has harvested its `usage`
event, because a check made while the leaf is still going reads a figure short of what the
step has spent. None follows a leaf after the green commit: by then the step is ticked, and its refactor
loop is one leaf already handed its own budget as a number (ADR-0017), so a check there
could change nothing.

`step-cost.sh` exit 3 means no leaf of this step has reported its usage yet, and that is not a
crossing: nothing has been spent to weigh, so the step goes on and the next leaf is checked as usual.

The check fires at most once per step. Once its crossing branch has run, the step's later
leaves are not checked again and nothing re-arms it for this step,
so a step that goes on to cost three times its budget is not asked about at every remaining leaf.

On a crossing — the figure `step-cost.sh` printed is over the step budget — send one leaf the
`over-budget` prompt, carrying the two figures, and launch it through the supervisor the way
the `exhausted` leaf is launched:

```
$S/build-develop-prompt.sh over-budget .tdd/issue-<n>-spec.md "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" '<test-cmd>' <spent> <step-budget> > .tdd/develop-over-budget.prompt
rm -f .tdd/develop-over-budget.exit .tdd/develop-over-budget.pid
VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" $S/detach-leaf.sh $S/supervise.sh develop-over-budget $S/run-leaf.sh .tdd/develop-over-budget.prompt --permission-mode bypassPermissions > .tdd/develop-over-budget.out 2> .tdd/develop-over-budget.err
$S/wait-leaf.sh develop-over-budget   # foreground; on exit 3 call it again
```

That leaf answers in prose around its report lines, so read its answer with the script, never
by eye — which outcome it holds is an exit code, not a judgement made per run:

```
$S/exhausted-outcome.sh < .tdd/develop-over-budget.out > .tdd/over-budget-answer.txt; echo $?
```

- **exit 0 — split.** Exactly the revise-exhausted path's split (see *Revise*):
  `.tdd/over-budget-answer.txt` holds the criteria, one per line, and they replace the step.
  Restore the tree first, so the step's uncommitted work cannot become the first replacement
  step's inherited start, then grow the plan in **one** call, then commit it before the run
  goes on, because the committed ledger is what a resumed run reads:
  ```
  git reset --hard HEAD
  git clean -f -- <test-path>   # a test file Red created is untracked, so the reset leaves it
  VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/next-unchecked.sh < .tdd/issue-<n>.md)" $S/event.sh step-added anchor="$($S/next-unchecked.sh < .tdd/issue-<n>.md)" added=<count>
  $S/add-ledger-step.sh .tdd/issue-<n>.md instead-of "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" '<criterion>' …   # every line of the answer in ONE call
  git add -A && git commit -m "plan: replace <STEP summary> with <count> smaller steps (#<n>)"
  ```
  Then loop back to `next-unchecked.sh`, which now hands over the first of them.
  **`add-ledger-step.sh` exit 1 → bail with cause `step-too-big`**, as it already is on the
  other two paths that grow a plan — see *Bailing*. The split shares `VERI_STEP_GROWTH` with
  them, because all three are plan growth.
- **exit 1 — a decision for the user.** `.tdd/over-budget-answer.txt` holds the leaf's answer.
  **Park the step** — the same park the revise-exhausted path takes (see *Revise*): stop the
  run there, carrying that answer and the two figures, what the step has spent and the
  step budget, and leave the plan as it is so the user's decision picks the run back up.
- **exit 3 — neither answer: record the crossing and carry on with the step.** This is
  **not a bail**, and it is where this path parts from the revise-exhausted one, whose exit 3
  bails with cause `revise-exhausted` because a verifier that will not pass the work leaves
  nothing to go on with. Here nothing has failed: every verdict may be a PASS and the step is
  merely dear, and bailing a converging step because it is expensive is exactly what this
  check exists not to do. Record the crossing, leave the check disarmed, and let the step
  finish normally:
  ```
  VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/next-unchecked.sh < .tdd/issue-<n>.md)" $S/event.sh step-over-budget spent=<spent> budget=<step-budget>
  ```

#### Red — one failing test (developer leaf), then verify-red (blind)

1. **Develop.** Build the prompt from the `red` template — it already instructs the leaf to
   write **exactly one** failing test pinning the criterion to **observable external
   behavior**, with **no production code**, and to run **the suite holding that case**, not
   the full suite, against the unmodified code, since the only question Red asks is whether
   that one case fails — and launch the leaf **through the supervisor**:
   ```
   $S/build-develop-prompt.sh red .tdd/issue-<n>-spec.md "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" '<test-cmd>' > .tdd/develop-red.prompt
   rm -f .tdd/develop-red.exit .tdd/develop-red.pid
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" $S/detach-leaf.sh $S/supervise.sh develop-red $S/run-leaf.sh .tdd/develop-red.prompt --permission-mode bypassPermissions > .tdd/develop-red.out 2> .tdd/develop-red.err
   $S/wait-leaf.sh develop-red     # foreground; on exit 3 call it again
   $S/step-cost.sh "$($S/next-unchecked.sh < .tdd/issue-<n>.md)"   # the step's cost check — see *The step's cost check*
   ```
   The template also states what a valid test is: behavior, not mechanism (no process, fork
   or call count and no timing across a suite run — those are `make profile`'s job — except
   a call count the criterion itself names, pinned with an in-process spy on the one wrapper
   called, never a `PATH` shim counting real processes); lightweight (~100ms, costly
   dependencies replaced unless the behavior under test IS the dependency); and
   self-contained (never runs another suite, whole or sliced, and never re-runs its own). A
   criterion that cannot be pinned within those rules is not weakened into one that can —
   the leaf reports it untestable instead (below).
   You supply only those variables; the instructions are the template's, identical every
   run. The leaf's report is in `.tdd/develop-red.out`, and ends with the lines you branch on — `TEST_PATH:`, `TARGET_TEST:`,
   `AGAINST_UNMODIFIED: FAILS | PASSES | UNTESTABLE`, `WHY:`, `FAIL_OUTPUT:` — so take the
   **test path** and **target test id** from the first two and read the third for the next
   sub-step.
   `AGAINST_UNMODIFIED` exists because a criterion earlier work already satisfies cannot
   yield a failing test, and that fact has to reach you as data: in #30's step 3 it did not,
   and a faithful test spent two verify-red `REJECT`s and two revise leaves reporting
   IMPOSSIBLE before the run bailed and the revert discarded it. `UNTESTABLE` is the same
   kind of fact for a criterion that cannot be pinned as a lightweight, behavior-level test
   at all (#331's "at most N python3" cost +41s of `make test`, satisfied only by a shim
   that re-ran whole suites under a counter) — the leaf says so rather than writing that test
   to force a pass.
   If the wait exits **2 (killed-stuck)**, the leaf hung or ran away — **bail**
   cleanly (see *Bailing*), after the stop check in *Launching a leaf*; do not retry.
2. **Verify (blind).** Branch on the leaf's `AGAINST_UNMODIFIED` line.
   On **`UNTESTABLE`** there is no test on disk for a blind verifier to judge — sending
   nothing to verify-red would only get a malformed-verdict `REJECT` for the wrong reason —
   so skip verify-red and verify-pin entirely and **bail** immediately with cause
   `untestable-criterion` (see *Bailing*), carrying the leaf's `WHY:` as the reason. This is
   a **process** failure: the criterion as phrased cannot be tested as behavior, not that
   the plumbing broke.
   On **`FAILS`**, check the prediction before any verifier: run `red-divergence.sh` on the
   leaf's report and branch on **its** exit code:
   ```
   $S/red-divergence.sh < .tdd/develop-red.out > .tdd/verify-red.reason; echo $?
   ```
   - **Exit 3 — `PREDICTION: MATCHED`:** nothing was surprising. The script printed
     nothing; carry on with the verifier below.
   - **Exit 0 or 2 — diverged, or a prediction nobody can read:** the test failed for a
     reason other than the one it was written to catch (exit 0), or the report carries no
     readable `PREDICTION:` line at all (exit 2), which is handled the same way — an
     unreadable prediction is not a matched one. Beck stops on that surprise, because the
     test is then the suspect, and this gate is **yours**: verify-red is blind by
     construction and the prediction is the developer's reasoning, so no verifier can be
     told about it. So **skip verify-red and verify-pin**, keep the reason the script wrote
     to `.tdd/verify-red.reason` (on exit 2 write your own one-line reason there instead —
     the report had no prediction to read), mark it with
     `$S/event.sh prediction-diverged` so the divergence is in the run log, preserve the
     attempt beside that mark with
     `$S/preserve-attempt.sh <n> "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" develop-red 1 prediction-diverged` so the tree the
     surprising test came from survives the next leaf that overwrites it (best-effort: note
     it if it fails and carry on), and enter the
     **revise loop** for red exactly as a verify-red `REJECT` does (see *Revising on a
     REJECT*) — the revise leaf answers `.tdd/verify-red.reason`, and the attempt spends
     `REVISE_BUDGET` like any other.

   On a matched prediction, run
   the red verifier against the on-disk test and spec, **redirecting its stdout (the
   reason) to a file** — the revise step takes the reason as a *path*, not as text you
   retype:
   ```
   rm -f .tdd/verdict-red.exit .tdd/verdict-red.pid
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" $S/detach-leaf.sh $S/supervise.sh verdict-red $S/run-verdict.sh --step "$(cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" red .tdd/issue-<n>-spec.md <test-path> <target-test-id> > .tdd/verify-red.reason 2> .tdd/verify-red.err
   $S/wait-leaf.sh verdict-red     # foreground; on exit 3 call it again
   $S/step-cost.sh "$($S/next-unchecked.sh < .tdd/issue-<n>.md)"   # the step's cost check — see *The step's cost check*
   ```
   That is the verifier shape from *Launching a leaf*: the wait returns the **verdict** —
   0 PASS, 1 REJECT, 2 malformed or killed-stuck — not the supervisor's status.
   On **`PASSES`** the criterion is **already satisfied** — never send that test to
   verify-red, whose verdict on a passing test can only be `REJECT`. Run the pin check
   instead and continue at *Already satisfied — the pin*:
   ```
   rm -f .tdd/verdict-pin.exit .tdd/verdict-pin.pid
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" $S/detach-leaf.sh $S/supervise.sh verdict-pin $S/run-verdict.sh --step "$(cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" pin .tdd/issue-<n>-spec.md <test-path> <target-test-id> > .tdd/verify-pin.reason 2> .tdd/verify-pin.err
   $S/wait-leaf.sh verdict-pin     # foreground; on exit 3 call it again
   ```
   Either way, note the **wait's exit code** — the verdict — and read the reason back out of
   `.tdd/verify-<phase>.reason` to narrate it. The file is named for the **verifier** that
   wrote it (`red`, `pin`, `green`, `refactor`), and each verification of that phase
   overwrites it — the newest objection is the only one a revise leaf should answer.
3. **Narrate + branch (the `FAILS` path).** Post a `### 🔴 Red` comment with the test, the
   failing output, the leaf's `PREDICTED_FAILURE:` and whether the prediction **matched or
   diverged** — with its `PREDICTION_NOTE:` when it diverged. Both halves, always: the
   prediction is what the failing output is read against, so a thread carrying only one of
   them cannot be read for divergence, and on a repository where the two keep diverging
   that thread is the evidence. Follow it with a `### 🔎 verify-red — PASS|REJECT` comment
   carrying the verifier's reason.
   - **PASS (exit 0):** continue to Green.
   - **REJECT (exit 1):** enter the **revise loop** — see *Revising on a REJECT*. It
     returns either PASS (continue to Green) or budget-exhausted (**bail**, process failure).
   - **Malformed / killed-stuck (exit 2):** the verdict could not be obtained (unparseable
     or the verifier leaf was killed) — **bail** as a system failure (see *Bailing*), not a
     clean process stop. A verifier that exited cleanly with no verdict has already been
     relaunched by `verify.sh` itself, up to `VERI_NO_VERDICT_RETRIES` times (default 1,
     ADR-0020), so exit 2 arrives here only once that budget is spent — never relaunch it
     again from the conductor.

#### Green — minimum implementation (developer leaf), then verify-green (blind)

1. **Develop.** Build the prompt from the `green` template — the **minimum** production
   code, no generality the test does not demand, the **test itself untouched**, full suite
   green — and launch **through the supervisor** (exit **2** → **bail**, after the stop
   check in *Launching a leaf*):
   ```
   $S/build-develop-prompt.sh green .tdd/issue-<n>-spec.md "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" '<test-cmd>' <test-path> '<target-test-id>' '<fast-cmd>' > .tdd/develop-green.prompt
   rm -f .tdd/develop-green.exit .tdd/develop-green.pid
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" $S/detach-leaf.sh $S/supervise.sh develop-green $S/run-leaf.sh .tdd/develop-green.prompt --permission-mode bypassPermissions > .tdd/develop-green.out 2> .tdd/develop-green.err
   $S/wait-leaf.sh develop-green    # foreground; on exit 3 call it again
   $S/step-cost.sh "$($S/next-unchecked.sh < .tdd/issue-<n>.md)"   # the step's cost check — see *The step's cost check*
   ```
   The test path and target test id are the ones Red's report gave you. The leaf's report is
   in `.tdd/develop-green.out`, and ends with `IMPL_PATH:` (the production files it created
   or changed) and `SUITE: GREEN | RED` plus the suite's final summary line; both go into the
   narration below.

   **`SPLIT:` lines in place of those two** — the step needed more than one new behaviour at
   once, so the leaf implemented nothing and named one to three smaller criteria instead.
   There is no implementation for verify-green to judge, so do not launch it. Restore the
   tree to `HEAD` first — Red's test is uncommitted, and left on disk it becomes the first
   split step's inherited red — then put the criteria into the plan ahead of this step, in
   **one** call, and commit the grown ledger:
   ```
   git reset --hard HEAD
   git clean -f -- <test-path>   # a test file Red created is untracked, so the reset leaves it; one git already tracked the reset restored
   VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/next-unchecked.sh < .tdd/issue-<n>.md)" $S/event.sh step-added anchor="$($S/next-unchecked.sh < .tdd/issue-<n>.md)" added=<count>
   VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/next-unchecked.sh < .tdd/issue-<n>.md)" $S/event.sh step-split anchor="$($S/next-unchecked.sh < .tdd/issue-<n>.md)" added=<count>
   $S/add-ledger-step.sh .tdd/issue-<n>.md before "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" '<SPLIT: value>' …   # every SPLIT: value in ONE call
   git add -A && git commit -m "plan: split <STEP summary> into <count> smaller steps (#<n>)"
   ```
   The two marks go first because they read the step's title out of the ledger, and the
   insertion puts the first split step ahead of it there (#437). One call and not one per criterion, under the script's own one-call rule above. A split is
   the one thing that changes a step's plan without a green commit of its own, so `step-split`
   is what tells the run log the step was split rather than silently restarted — beside the
   `step-added` mark the insertion owes as any other does, which says the plan grew but not
   why. Then loop back to `next-unchecked.sh`, which now hands over the first split step;
   **STEP** itself starts again from Red once the smaller steps ahead of it are done.

   **`add-ledger-step.sh` exit 1 → bail with cause `step-too-big`** — see *Bailing*. The
   insertion would take the ledger past `VERI_STEP_GROWTH`, so the script has already filed
   the criteria under `## Owed steps`: the step's own red is discarded and the smaller steps
   it needs are not in the plan, so there is nothing for the run to go on with.
2. **Verify (blind)** — the verifier shape again, and the wait's code is again the verdict:
   ```
   rm -f .tdd/verdict-green.exit .tdd/verdict-green.pid
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" $S/detach-leaf.sh $S/supervise.sh verdict-green $S/run-verdict.sh --step "$(cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" --fast-cmd '<fast-cmd>' green .tdd/issue-<n>-spec.md <test-path> <target-test-id> > .tdd/verify-green.reason 2> .tdd/verify-green.err
   $S/wait-leaf.sh verdict-green    # foreground; on exit 3 call it again
   $S/step-cost.sh "$($S/next-unchecked.sh < .tdd/issue-<n>.md)"   # the step's cost check — see *The step's cost check*
   ```
3. **Narrate + branch.** Post `### 🟢 Green` (implementation + green suite output) and
   `### 🔎 verify-green — PASS|REJECT` (the reason).
   - **PASS — check off the ledger step and commit atomically.** Tick STEP in the ledger,
     then commit the code **and** the ticked ledger in **one** commit so git and ledger
     never diverge. The tick carries `--refactor-pending`, which appends ` ⟂ refactor
     pending` to that same line: the step is green, but its refactor loop and
     verify-refactor are still ahead of it, so a run interrupted between here and them must
     resume into that loop rather than read the tick as *done*.
     ```
     $S/tick-ledger.sh --refactor-pending .tdd/issue-<n>.md "$($S/next-unchecked.sh < .tdd/issue-<n>.md)"
     git add -A && git commit -m "feat: <STEP summary> (#<n>)"
     $S/push-branch.sh
     gh pr edit --body "Closes #<n> — work in progress: <done> of <total> steps done. The ledger .tdd/issue-<n>.md is the source of truth."
     ```
     `<done>` is the ticked checkboxes of the run's ledger `.tdd/issue-<n>.md` and
     `<total>` all of its steps — `grep -c '^- \[x\]'` of `grep -c '^- \['` over that file,
     counted after the tick above so the step just closed is in the number. The draft PR
     opened at the plan commit is the only thing another machine can read for the hours a
     multi-step run takes, and a body written once there says the same at step 1 as at step
     7; the tick is where the count changes, so it is where the body is rewritten.
     **On a bug run that subject is `fix:`, not `feat:`** — `fix: <STEP summary> (#<n>)`.
     The run is a bug run when the issue carries the `bug` label, the same fact step 1 read
     to give the spec its `## Bug` section. A bug step's green repairs a reported failure
     rather than adding a capability, and the walkthrough's capability index is computed
     from the `feat:`/`fix:` subjects in each tag's range, so a bug step committed as
     `feat:` files a regression repair there as a new capability.
     The push is what stops the run living on one disk until it is review-ready: the first
     call creates the remote branch, later ones fast-forward, and no PR is opened, so
     nothing asks for review before the run is ready. An unreachable remote is **not** a
     bail — `push-branch.sh` retries it, records a `push-failed` event and exits 0, so the
     tick and the commit above stand whatever the network did. On exit **1** (the remote
     rejected a non-fast-forward) launch the reconcile leaf — see
     *Reconciling a rejected push*; on exit **2** (its
     event could not be written) **bail**.
     **Then run `$S/stop-requested.sh`**, immediately after that push: this ledger commit is
     the boundary `at-ledger` was waiting for, and `at-leaf` and `now` have nothing left to
     abandon, so on exit 0 any mode it printed goes to *Stopping* here. On exit 2 go to
     *Stopping* in mode `at-ledger`, narrating that the request was unreadable. On exit 3
     continue to the Refactor loop.
   - **REJECT (exit 1):** enter the **revise loop** — see *Revising on a REJECT*. On a
     recovered PASS, do the same atomic tick-and-commit and continue; on budget-exhausted,
     **bail**.
   - **Malformed / killed-stuck (exit 2):** **bail** — see *Bailing*.

#### Refactor loop — one leaf applies the step's transforms, then verify-refactor (blind, once)

1. **One refactor leaf for the step.** Ask the budget first, with a count of **0**: that
   call is what decides whether the leaf runs at all, since `VERI_REFACTOR_BUDGET=0`
   switches refactoring off. Then build the prompt from the `refactor` template — which
   carries the budget to the leaf as the number of transforms it may apply — and launch
   **through the supervisor** (exit **2** → **bail**, after the stop check in *Launching a
   leaf*):
   ```
   $S/refactor-budget.sh 0   # exit 0 ⇒ launch the leaf below; exit 3 ⇒ the budget is 0, go to 5
   touched="$($S/refactor-touched.sh HEAD)"
   $S/build-develop-prompt.sh refactor .tdd/issue-<n>-spec.md "$($S/next-pending-refactor.sh < .tdd/issue-<n>.md)" '<test-cmd>' "$touched" > .tdd/develop-refactor.prompt
   rm -f .tdd/develop-refactor.exit .tdd/develop-refactor.pid
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/next-pending-refactor.sh)" $S/detach-leaf.sh $S/supervise.sh develop-refactor $S/run-leaf.sh .tdd/develop-refactor.prompt --permission-mode bypassPermissions > .tdd/develop-refactor.out 2> .tdd/develop-refactor.err
   $S/wait-leaf.sh develop-refactor   # foreground; on exit 3 call it again
   ```
   **One leaf for the whole step**, not one per transform: the cold `claude -p` start and
   the re-read of the spec and of the touched files are paid once for the step instead of
   once for every transform it applies. That is what #150 measured — the refactor loop and
   verify-refactor took 2,147 of #144's 3,735 leaf-seconds, and one #137 step's five
   transforms took 49 minutes between them.
   `<touched-files>` is the **bounds of the tidy-up**: the files this cycle produced, as one
   comma-separated line. Compute it **once**, right after the step's atomic green commit —
   `$S/refactor-touched.sh HEAD` is exactly that commit's files at that moment — adding
   anything still uncommitted (`git diff --name-only HEAD`) if an interrupted run left work
   on disk.
   The template owns the rules — the leaf triages what it sees in those files into
   **structural** and **cosmetic** candidates and applies the structural ones, most valuable
   first, up to its budget; it runs the **suites covering the files it touched** after every
   transform and **reverts** one that turns them red rather than leave a red suite; it takes
   **no untested generality** (that comes only from **triangulation**) and **flags overfit**
   code as needing a triangulating test instead of hand-generalizing it. It also **commits
   its own transforms**, one commit each so a break stays attributable to one change:
   `git commit -m "refactor: <what> (#<n>)"`. The atomic tick-and-commit stays on green
   (ADR-0007); it is the refactor commit that moved to the leaf. The report is in
   `.tdd/develop-refactor.out` and ends with `RESULT:` (one line per transform applied, or
   `nothing left to tidy`), `CANDIDATES:` (one line per leftover it still sees, each
   carrying its class, or `none`) and `FLAGS:` (one finding per line, each carrying its
   class — `overfit`, `uncovered-spec` or `beyond-spec` — or `none`; 3 and 4 below route
   them).
2. **Check what the leaf left.** The leaf produced the result; the conductor's job in this
   phase is to **check** it, because verify-refactor judges the **settled tree** and can see
   neither of the two faults below. Ask git, not the report:
   ```
   git status --porcelain                   # any output ⇒ refuse to go on, see below
   git log --format=%s <green-sha>..HEAD    # every one must be a refactor:, or refuse to go on
   git rev-list --count <green-sha>..HEAD   # the transforms that landed, narrated against the budget
   ```
   `<green-sha>` is this step's atomic green commit — the one carrying the ledger tick — so
   the range holds exactly what the step's refactor produced.
   - **A dirty tree** is work no suite run and no verifier has seen: the transform a killed
     leaf left half-applied on disk. Do **not** continue to verify-refactor over it — `git
     reset --hard HEAD` drops it, leaving the last committed transform, which the leaf's own
     suite run found green — and say in the narration that it was dropped.
   - **A commit in that range whose subject is not `refactor:`** is production code carried
     into a behaviour-preserving phase: the blind verifier ahead is asked whether behaviour
     was preserved, and nothing there asks whether that code was earned by a test. Do
     **not** continue either — `git reset --hard <green-sha>` drops every commit the leaf
     made for this step, the well-formed ones with it, since a leaf that committed
     production code here is not one whose other commits can be taken on trust — and the
     step goes to verify-refactor on its green state, with what was dropped named in the
     narration.
3. **An `overfit` flag is answered inside this step.** The leaf's `FLAGS:` lines each carry
   their class. A line whose class is **overfit** names code that passes this step's test
   without implementing the criterion the step states, and names the case that would force
   the general implementation. Stop the refactor loop there and run, for that case, one
   triangulating **red → verify-red → green → verify-green** inside this same step, exactly
   as the **Red** and **Green** phases above run them. An overfit flag grows **no ledger
   step**, makes **no plan amendment** and posts **no second step-done comment**: a step is
   mirrored done once, at the end of its own cycle, and this is not that moment — the
   step is interrupted here, not finished, and the case is this step's own criterion
   caught late rather than a step the plan is missing. The triangulation's own green commit is this
   step's `<green-sha>` from here on — that is the state the tidying now starts from, so 2
   above still reads exactly what the step's refactor produced. Then **resume this step's
   refactor loop** at 1 with the **budget it had left**, asking
   `$S/refactor-budget.sh <count>` with the transforms already landed as `<count>`, so an
   overfit flag costs the step a triangulation and never a second budget.
   **A step's triangulation runs at most once.** The loop resumed there is another refactor
   leaf reading the files the triangulation just generalized, so it can raise an `overfit`
   flag about that same code a second time — and a conductor that answers the second flag
   the way it answered the first has rebuilt #107's chain inside one step, where each flag
   came from the refactor loop of the step the flag before it created. So a flag raised
   inside a triangulation's own refactor loop about the same code is **narrated** in the
   `### 🛠️ Refactor` comment at 6 as a follow-up, not triangulated again: the step keeps
   what the second leaf saw on the record and spends nothing more on it.
4. **An `uncovered-spec` flag is the one class that grows the plan.** A `FLAGS:` line
   whose class is **uncovered-spec** names a behaviour the issue's spec requires that **no
   ledger step covers** — the gap *Scope & plan* above asks the planner to
   catch, found late by a leaf reading the code. That is the **only** flag class a plan
   amendment is made from: its behaviour is carried, verbatim as a criterion, into the same
   `add-ledger-step.sh … after "<STEP>"` call the verdict's own `uncovered-spec` flags go in at
   6's PASS branch, so the missing step is planned and built like any other. No other class amends
   the plan — an **overfit** flag is answered inside the step at 3, and the plan never grows
   for what the spec did not ask for. A flag class turned into a step of its own is what
   #175 measured: six `plan: amend` commits on `origin/main`, each buying a whole cycle and
   a refactor loop that flagged the next one.
   - **A `beyond-spec` flag is narrated as a follow-up in the `### 🛠️ Refactor`
     comment at 6 and in the PR body, and is not planned and not built in this run.**
     It names an input class or an edge the issue's spec never asked for. The comment is
     where the step accounts for itself while the run is live and the PR body is what the
     human deciding the merge reads afterwards, so the follow-up outlives the run without
     costing it a step: one made from a `beyond-spec` flag would build behaviour no
     criterion of the issue states, and nothing ahead could judge it — the blind verifier
     is given the spec, and the spec is where that behaviour is not.
5. **Verify (blind, once) on the settled result.**
   ```
   rm -f .tdd/verdict-refactor.exit .tdd/verdict-refactor.pid
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/next-pending-refactor.sh || cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" $S/detach-leaf.sh $S/supervise.sh verdict-refactor $S/run-verdict.sh --step "$(cat .tdd/issue-<n>.md | $S/next-pending-refactor.sh || cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" --fast-cmd '<fast-cmd>' refactor .tdd/issue-<n>-spec.md <test-path> <green-sha> > .tdd/verify-refactor.reason 2> .tdd/verify-refactor.err
   $S/wait-leaf.sh verdict-refactor  # foreground; on exit 3 call it again
   ```
   — one verdict on the final state (**full suite** still green, code up to standard, no
   smuggled generality). This is where the full suite runs in this phase: the refactor leaf
   ran only the suites covering the files it touched, so a break in a suite none of its
   transforms touched surfaces here, as a REJECT the revise loop answers rather than a
   revert inside the leaf.
6. **Narrate + branch.** Post `### 🛠️ Refactor` (the transforms applied, or "no refactor
   warranted", plus any triangulation flagged) and `### 🔎 verify-refactor — PASS|REJECT`.
   Say **how many transforms landed** — the `git rev-list --count` figure, never the leaf's
   own account of what it did — against the budget, in `refactor-budget.sh`'s own shape
   (`refactor 2/5`). A count **above** the budget is narrated as an **overrun** (`refactor
   7/5 — overrun`), never clamped to the budget: the budget reaches the leaf as a number, so
   a count over it is the leaf ignoring it, and that is the one thing this narration exists
   to make visible. Say too **why the tidying stopped**: the leaf reported
   **nothing left to tidy**, it spent the **budget** it was given, or
   `$S/refactor-triage.sh < .tdd/develop-refactor.out` says so — exit **2**, a malformed
   report, is **narrated** as that rather than bailed on; exit **3**, nothing structural is
   left, so the tidying **stops** owing nothing; exit **0**, structural candidates remain
   and a follow-up owes them. Then **list what the step did not do**, taken verbatim from
   the leaf's `CANDIDATES:` lines and filed in **two separate lists** — the **structural**
   leftovers, which a follow-up owes, and the **cosmetic** ones, which nobody owes. Each
   list says **how many candidates** it holds and then **lists** them, one per line. A
   count with no items is not a backlog, and the two classes run together are a backlog
   nobody can size. Mark the same three figures in the log — the observed count, unclamped,
   the budget, and why it stopped (`nothing-left`, `budget`, `malformed`, `nothing-structural` for triage exit **3** or
   `structural-owed` for triage exit **0**):
   ```
   VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/next-pending-refactor.sh < .tdd/issue-<n>.md)" VERI_PHASE=refactor $S/event.sh refactor transforms=<count> budget=<VERI_REFACTOR_BUDGET> stopped=<reason>
   ```
   Then **record the leftovers themselves**, which is not a log mark and does not belong in
   that line: the narration above is a comment and `.tdd/develop-refactor.out` is overwritten
   by the next step's leaf, so **`append` is what makes the structural leftovers outlast the
   step**. It copies them — never the cosmetic ones — into the run's owed file under this
   step's name, where the Draft PR renders every step's, not just the last one's:
   ```
   $S/refactor-owed.sh append .tdd/issue-<n>-refactor-owed.md "<STEP>" < .tdd/develop-refactor.out
   ```
   - **PASS:** the step's cycle is complete — the step is tidied, not merely green, so
     **grow the plan with the behaviours of the leaf's `uncovered-spec` flags (4 above) and of
     the passing verify-refactor verdict's own `uncovered-spec` flags, then clear the refactor-pending mark and commit the grown, cleared
     ledger first**, before anything outside the repository says the step is done. The
     verifier's are the `FLAGS:` lines before the final `VERDICT:`/`REASON:` pair in
     `.tdd/verify-refactor.log` — the unhandled edge case it reports rather than REJECTs
     for, carrying the same three classes as the leaf's. Only its `uncovered-spec` lines go
     into the call, by 4's rule; its `overfit` and `beyond-spec` lines are narrated as
     follow-ups in the `### 🛠️ Refactor` comment and the PR body, since the step's refactor
     loop has already closed and no triangulation reopens it:
     ```
     VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/next-pending-refactor.sh < .tdd/issue-<n>.md)" $S/event.sh step-added anchor="$($S/next-pending-refactor.sh < .tdd/issue-<n>.md)" added=<count>
     $S/add-ledger-step.sh .tdd/issue-<n>.md after "$($S/next-pending-refactor.sh < .tdd/issue-<n>.md)" '<leaf or verdict uncovered-spec behaviour>' …   # every one in ONE call
     $S/clear-refactor-pending.sh .tdd/issue-<n>.md "$($S/next-pending-refactor.sh < .tdd/issue-<n>.md)"
     git add -A && git commit -m "chore: refactor verified for <STEP summary> (#<n>)"
     $S/push-branch.sh
     ```
     `git add -A` is what carries `.tdd/issue-<n>-refactor-owed.md` into that same commit:
     what `append` wrote is untracked until then, and a file left beside the worktree is
     lost with it.
     Every uncovered-spec behaviour, the leaf's and the verifier's, goes in **one**
     call, under the script's own one-call rule, anchored `after "<STEP>"` so the
     triangulating step lands next to the code it triangulates. Neither reporting one — no `uncovered-spec` flag
     from the leaf and none in the verdict — is no call and no mark at all.
     **exit 1** is that one call meeting the plan-growth budget: the values are filed as
     owed steps rather than planned — the script's own entry above says how — and
     `next-unchecked.sh` never finds them there, so the run does not plan what it recorded.
     Narrate it as the owed steps it is and carry on to the clear below — the step verified
     PASS and the values are recorded; the plan simply did not grow, which is nothing to
     stop a run for. That grown ledger rides the same commit as the clear.
     A clear left uncommitted is not a clear, and a step inserted into a ledger nothing
     commits is a step the next run never sees: resume reads the **committed** ledger, so
     until that commit exists the step still says pending and the plan is still the one the
     leaf grew from. The push copies the step's
     finished state to the remote on the same terms as Green's above: exit **1** launches
     the reconcile leaf (*Reconciling a rejected push*), exit **2** is a **bail**.
     **Then run `$S/stop-requested.sh`**, immediately after that push, as Green does after
     its own: on exit 0 any mode it printed goes to *Stopping* here; on exit 2 go to
     *Stopping* in mode `at-ledger`, narrating that the request was unreadable; on exit 3
     carry on.
     Then **mirror to the issue**:
     post a `### ✅ Step done` comment, then ask whether the step's criterion is finished
     (`$S/criterion-finished.sh <k> < .tdd/issue-<n>.md`, k from the step's `⟦criterion k⟧`):
     on exit **0** tick it in the **issue body** (`$S/tick-issue-criterion.sh <n>
     "$(gh issue view <n> --json body -q .body | sed -n '/^## Acceptance criteria/,/^## /s/^[[:space:]]*- \[[ x]\] //p' | sed -n '<k>p')"`, the human mirror); on exit **3** tick nothing, since a step serving it is
     still open or pending. Mark
     the same moment in the log —
     `VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$(sed -n 's/^[[:space:]]*- \[x\] //p' .tdd/issue-<n>.md | tail -1)" $S/event.sh step-done` — then
     loop back to the top of **step 3** for the next unchecked ledger step.
   - **REJECT (exit 1):** enter the **revise loop**; on recovered PASS, mirror and loop; on
     budget-exhausted, **bail**. (Earlier steps' commits are preserved.)
   - **Malformed / killed-stuck (exit 2):** **bail**. (Earlier steps' commits are preserved.)

### 4. Draft PR

Reached when `next-unchecked.sh` exits 3 — every ledger step is checked off. The full suite
must be green before this step: run `$S/detect-test-command.sh --tier all`'s command here,
exactly once — the only full-suite gate left in the cycle, since every leaf runs the fast
command, the affected suites, or both. That nothing is left uncommitted and no step is still only
green is not taken on trust here — sub-step 1 asks. Like every step since 1.2, this one runs
**from inside the worktree** — every command below is issued there, so each sees the issue
branch and its commits without any switching.

A red result on that full run does not bail: append a repair step to the ledger, commit it,
and return to step 3, *The cycle loop* — the failing suite is that step's red evidence. Its
developer adds a unit-tier test when the failure exposes a gap the fast tier missed, and its
verifier judges the fix against the full command, not the fast one.

A second red result on the full run after a repair step does **bail** — the repair step is
one more cycle, not a loop — and the bail names every suite still red, not only the first.

With a stop request pending, this step is **not interrupted** and runs to completion: once
`next-unchecked.sh` exits 3 there is no next ledger commit, and what remains launches no leaf
and loses nothing. So no checkpoint runs here — sub-step 4 asks once, clears the request with
`$S/stop-requested.sh --clear` and says so in the final comment. The exception is the repair
step a red full run appends: it launches leaves and ends in a ledger commit like any other
step, so both checkpoints apply to the repair step as they do in step 3.

1. **Ask the two questions that decide whether there is anything fit to push, and refuse to
   go on while either says no** — both from inside the worktree, before a human is asked to
   look:
   ```
   git status --porcelain
   $S/next-pending-refactor.sh < .tdd/issue-<n>.md
   ```
   A non-empty `git status --porcelain` is work no verifier has seen — the transform a
   killed refactor leaf left on disk — and an exit 0 from `next-pending-refactor.sh` is a
   step that is checked but still only green. On either, **do not ready the PR**: go to
   *Resume* sub-step 2, whose reset runs before its ask and so discards that work whatever
   the ask answers, and come back here only once both questions have gone quiet — an empty
   status, and `next-pending-refactor.sh` exiting 3. For a pending step sub-step 2 also
   re-enters that step's refactor loop. With **no step pending and none unchecked** the
   reset is the whole remedy: sub-steps 2 and 3 both exit 3, sub-step 4's `### ▶️ Resuming`
   comment names the paths the reset discarded, and the run comes back here and readies the
   PR — refusing the same tree for ever is not an outcome, discarding it loudly is.
2. **Close the run's log with the PR's URL, render the metrics, commit them, then rewrite the
   PR into its final form and mark it ready for review** — one sub-step, in this order, from
   inside the worktree. **This step opens no PR.** Step 2.3 opened it at the plan commit, so
   there is nothing left here for `gh pr create` to do: a second one against a branch that
   already has an open PR is either a refusal that ends the run at its last step, or a second
   PR for the same branch — and then the claim another machine reads and the page a human is
   asked to merge are two different pages. Read the existing PR's URL rather than assuming the
   run remembers it, so a resumed run edits the PR its branch already has:
   ```
   gh pr view --json url -q .url          # → <pr-url>, the PR step 2.3 opened
   VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh done pr=<pr-url>
   $S/metrics.sh <n> > .tdd/issue-<n>-metrics.md
   git add .tdd/issue-<n>-metrics.md
   git commit -m "metrics: what solving #<n> cost (#<n>)"
   $S/push-branch.sh
   $S/refactor-owed.sh render .tdd/issue-<n>-refactor-owed.md
   gh pr edit <pr-url> --title "<type>: <criterion summary> (#<n>)" --body "<Closes #<n> — summary: the plan's steps, each a blind-verified R→G→R cycle, ledger committed; followed by the contents of .tdd/issue-<n>-metrics.md, followed by that render's output, followed by the ledger's ## Owed steps bullets>"
   gh pr ready <pr-url>
   ```
   The `done` mark comes before the render because `metrics.sh` reads it for both the Outcome
   and the issue's wall time: a report rendered before it exists says `unknown` for both. The
   body is rewritten only after the `metrics:` commit is pushed, so it never quotes a file the
   branch does not yet carry. The title drops the `WIP:` prefix step 2.3 opened it with, and
   `gh pr ready` is what turns the run's claim into a review request: a finished run that left
   a draft behind asks nobody to look.
   `<type>` is **`fix`** on a bug run — the issue carries the `bug` label, so the title
   starts with the `fix:` prefix, the same prefix its green commits took — and `feat`
   otherwise. A bug run's PR titled `feat:` announces to the human deciding the merge a
   capability the run did not add.
   One `metrics:` commit, and the report sits beside the ledger it describes — the
   `issue-<n>-metrics.md` name is already on the keep side of the run-state ignore rule, so
   nothing else has to change for it to be tracked.
   The render is what puts every step's structural leftovers in front of the human who
   decides the merge, rather than leaving them in a committed file nobody is pointed at.
   When it exits 3 — no step left anything structural behind — it prints nothing, and the
   `## Refactor owed` section is **omitted** from the body: a heading over an empty list
   promises a backlog nobody left.
   The ledger's own owed steps are copied the same way, and out of the ledger itself: every
   plain bullet under the trailing `## Owed steps` heading of `.tdd/issue-<n>.md` — a step
   `add-ledger-step.sh` could not fit inside `VERI_STEP_GROWTH`, which nothing in the run
   reads again — goes into the PR body under a `## Owed steps` heading of its own. A ledger
   carrying no such heading adds no such section.
3. **Never merge the PR.** Landing the code is always the human's deliberate act.
4. Post a final `### ✅ Done — <pr-url>` comment with the same `### 📊 Metrics` block
   under it, pasted verbatim from the file just committed. It mirrors the
   `$S/event.sh done pr=<pr-url>` mark sub-step 2 already wrote, so it writes no second one.
   Before posting it, run `$S/stop-requested.sh`; on exit 0 or 2 run
   `$S/stop-requested.sh --clear` and add a line to the comment saying that a stop arrived
   after the last step, so the run finished rather than pausing — on exit 3 add nothing.

**The worktree stays.** Do not remove it here: it holds the run's leaf logs and is where a
resume would land if the PR comes back for more work. It is removed once the PR is **merged**
— by the `merge` skill's cleanup, or by the human — with
`$S/issue-worktree.sh --remove <n>`, which refuses (exit 2) if anything in it is still
uncommitted rather than destroying it.

Report back to the user with the branch name, the worktree path, and the PR URL — and say
that their own checkout was not switched.

## Already satisfied — the pin

A step whose criterion **earlier work already satisfies** has no failing test to write: the
honest test passes against the unmodified code. That is an **outcome** of the step, not a
failure of it — the behaviour exists and what it wants is a **regression pin**. You reach
this section from Red when the developer leaf reported `AGAINST_UNMODIFIED: PASSES` and you
ran `$S/verify.sh pin …` in place of verify-red. Its verdict replaces the
`### 🔴 Red` / `### 🔎 verify-red` pair:

- **PASS (exit 0) — commit the test as the pin, ticking the ledger atomically.** Same
  tick-and-commit shape as Green, but the commit carries the **test alone** and the `test:`
  type, because no production code was written (the verifier reverted its own mutation, so
  the tree holds only the new test and the ticked ledger):
  ```
  $S/tick-ledger.sh .tdd/issue-<n>.md "$($S/next-unchecked.sh < .tdd/issue-<n>.md)"
  git add -A && git commit -m "test: pin <STEP summary> (#<n>)"
  ```
  **Then run `$S/stop-requested.sh`**, immediately after that commit: it is a ledger commit
  like Green's, so on exit 0 any mode it printed goes to *Stopping* here; on exit 2 go to
  *Stopping* in mode `at-ledger`, narrating that the request was unreadable; on exit 3
  carry on.
  Then **mirror**: post a `### 📌 Already satisfied — <STEP>` comment carrying the
  verifier's reason, ask whether the step's criterion is finished
  (`$S/criterion-finished.sh <k> < .tdd/issue-<n>.md`) and on exit **0** tick it in the
  **issue body** (`$S/tick-issue-criterion.sh <n> "$(gh issue view <n> --json body -q .body | sed -n '/^## Acceptance criteria/,/^## /s/^[[:space:]]*- \[[ x]\] //p' | sed -n '<k>p')"`) — on exit **3** tick
  nothing — and mark it in the log —
  `VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$(sed -n 's/^[[:space:]]*- \[x\] //p' .tdd/issue-<n>.md | tail -1)" VERI_PHASE=pin $S/event.sh pin`.
  The step is **done** — **no Green and no Refactor**, since there is no new production
  code to write or to tidy. Loop back to the top of **step 3** for the next unchecked
  ledger step.
- **REJECT (exit 1):** enter the **revise loop** for the **red** phase — see *Revising on a
  REJECT* — building the prompt as `revise red … .tdd/verify-pin.reason`: the phase argument
  is the *developer* phase being redone, while the reason file is named for the *verifier*
  that rejected, here `pin`. The rejection reason is the carry-forward signal that tells the
  fresh leaf which way to go: either the pin is weak (trivial, over-coupled, or it survives
  the mutation) or a genuinely failing test exists after all. Re-verify with the phase the
  revise leaf's own `AGAINST_UNMODIFIED` line selects — `pin` on `PASSES`, `red` on `FAILS`.
  (That line's third value, `N/A`, cannot arise here: a revise of red always touches a
  test.) On a recovered `PASS` from `pin`, do the tick-and-commit above; from `red`,
  continue to Green. On budget-exhausted, **bail** as a **process** failure.
- **Malformed / killed-stuck (exit 2):** **bail** as a **system** failure (`no-verdict`) —
  see *Bailing*.

## Revising on a REJECT

A `REJECT` (verify.sh exit **1**) does **not** stop the run. The conductor gets a bounded
**attempt budget** — `REVISE_BUDGET` revise attempts, **default 2** — to satisfy the blind
verifier before bailing the step. The rejection **reason is the carry-forward signal**:
leaves never share context, so each revise leaf is told explicitly what to fix.

For attempt `k = 1 … REVISE_BUDGET`:

1. **Mirror.** Post a `### ♻️ Revise <phase> — attempt <k>/<REVISE_BUDGET>` comment carrying
   the verifier's **rejection reason verbatim**, and mark the same attempt in the log:
   ```
   VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/next-pending-refactor.sh < .tdd/issue-<n>.md || $S/next-unchecked.sh < .tdd/issue-<n>.md)" VERI_PHASE=<phase> VERI_ATTEMPT=<k> $S/event.sh revise budget=<REVISE_BUDGET>
   ```
2. **Fresh developer leaf.** Build the revise prompt from the `revise` template, naming the
   phase being redone and the **reason file** the verifier's stdout went to, then launch
   **through the supervisor** (exit **2 → bail**, system failure, after the stop check in
   *Launching a leaf*):
   ```
   $S/build-develop-prompt.sh revise <phase> .tdd/issue-<n>-spec.md "$($S/next-pending-refactor.sh < .tdd/issue-<n>.md || $S/next-unchecked.sh < .tdd/issue-<n>.md)" '<test-cmd>' .tdd/verify-<phase>.reason > .tdd/revise-<phase>-<k>.prompt
   rm -f .tdd/revise-<phase>-<k>.exit .tdd/revise-<phase>-<k>.pid
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/next-pending-refactor.sh || cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" $S/detach-leaf.sh $S/supervise.sh revise-<phase>-<k> $S/run-leaf.sh .tdd/revise-<phase>-<k>.prompt --permission-mode bypassPermissions > .tdd/revise-<phase>-<k>.out 2> .tdd/revise-<phase>-<k>.err
   $S/wait-leaf.sh revise-<phase>-<k>   # foreground; on exit 3 call it again
   $S/step-cost.sh "$($S/next-unchecked.sh < .tdd/issue-<n>.md)"   # the step's cost check — red or green only — see *The step's cost check*
   ```
   The `step-cost.sh` line runs only when `<phase>` is red or green: a refactor-phase revise
   never runs it, because the refactor phase comes after the step's green commit and *The
   step's cost check* runs no check past that commit.
   The reason travels as a **file**, not as prose you paste in — that is why the verify step
   redirected it. The template tells the leaf it is fresh, that the reason is the whole of
   what it has to work from, that the work is on disk, and that it must answer *that
   objection only*. Its report ends with `OUTCOME: REWRITTEN | IMPOSSIBLE` and
   `AGAINST_UNMODIFIED: FAILS | PASSES | N/A` — `N/A` whenever the leaf touched no test,
   which is every revise of green or refactor. `IMPOSSIBLE` is a legitimate answer, not a
   crash: the leaf says the objection cannot be met as stated. It still spends attempt `k` —
   re-verify below and let the blind verdict, not the leaf's own account, decide.
3. **Check the prediction first (red only).** When `<phase>` is red the revise leaf rewrote
   the failing test and reported its own `PREDICTED_FAILURE:` and `PREDICTION:` lines, so run
   the same gate the Red section runs before anything reaches a verifier:
   ```
   $S/red-divergence.sh < .tdd/revise-red-<k>.out > .tdd/verify-red.reason; echo $?
   ```
   - **Exit 3 — matched:** nothing was surprising; carry on to the re-verify below.
   - **Exit 0 or 2 — diverged, or a prediction nobody can read:** the rewritten test failed
     for a reason other than the one it was written to catch (exit 0), or its report carries
     no readable `PREDICTION:` line at all (exit 2), which is handled the same way. The test
     is the suspect, and verify-red is blind by construction, so spend attempt `k` **without
     re-verifying**: skip the re-verification entirely, keep the reason the script wrote to
     `.tdd/verify-red.reason` (on exit 2 write your own one-line reason there instead), mark
     it with `$S/event.sh prediction-diverged`, preserve the attempt beside that mark with
     `$S/preserve-attempt.sh <n> "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" revise-red <k> prediction-diverged` (best-effort:
     note it if it fails and carry on), and treat the attempt exactly as a `REJECT`
     does — if attempts remain, loop to attempt `k+1` with that reason; otherwise fall
     through to the budget-exhausted bail below.
   Every other phase's revise template writes no `PREDICTION:` line, so this sub-step is the
   red phase's alone.

4. **Re-verify (blind, same phase).**
   ```
   rm -f .tdd/verdict-<phase>.exit .tdd/verdict-<phase>.pid
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/next-pending-refactor.sh || cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" $S/detach-leaf.sh $S/supervise.sh verdict-<phase> $S/run-verdict.sh --step "$(cat .tdd/issue-<n>.md | $S/next-pending-refactor.sh || cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" --fast-cmd '<fast-cmd>' <phase> .tdd/issue-<n>-spec.md <test-path> [target] > .tdd/verify-<phase>.reason 2> .tdd/verify-<phase>.err
   $S/wait-leaf.sh verdict-<phase>      # foreground; on exit 3 call it again
   ```
   — overwriting the reason file, so attempt `k+1` carries the newest objection. The
   `--fast-cmd` rides along whatever the phase: green and refactor refuse to build without it
   (exit 2), and the other phases' prompts name no fast command, so it changes nothing there. Both `rm
   -f`s matter in this loop: every attempt re-verifies the **same** phase, so the previous
   attempt's completion files would otherwise be read as this one's answer.
   - **PASS (exit 0):** the step is recovered. Post `### 🔎 verify-<phase> (revised) — PASS`
     with the reason, and resume the cycle from where that phase's PASS would continue.
   - **REJECT (exit 1):** if attempts remain, loop; otherwise fall through to the bail below.
   - **Malformed / killed-stuck (exit 2):** **bail** (system failure).

If all `REVISE_BUDGET` attempts are still `REJECT`, the step is **not** bailed on the spot. A
criterion no blind verifier could be satisfied about in that many attempts is usually a
criterion carrying more than one behaviour — the very condition `SPLIT:` exists for — so send
one last leaf and ask it which of the two is true of this step, rather than deciding that
yourself. The reason file the last re-verify overwrote is the whole of what it is told:

```
$S/build-develop-prompt.sh exhausted .tdd/issue-<n>-spec.md "$($S/next-pending-refactor.sh < .tdd/issue-<n>.md || $S/next-unchecked.sh < .tdd/issue-<n>.md)" '<test-cmd>' .tdd/verify-<phase>.reason > .tdd/develop-exhausted.prompt
rm -f .tdd/develop-exhausted.exit .tdd/develop-exhausted.pid
VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/next-pending-refactor.sh || cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" $S/detach-leaf.sh $S/supervise.sh develop-exhausted $S/run-leaf.sh .tdd/develop-exhausted.prompt --permission-mode bypassPermissions > .tdd/develop-exhausted.out 2> .tdd/develop-exhausted.err
$S/wait-leaf.sh develop-exhausted   # foreground; on exit 3 call it again
```

That leaf answers in prose around its report lines, so **read its answer with the script, not
by eye** — which outcome it holds is an exit code, never a judgement made per run:

```
$S/exhausted-outcome.sh < .tdd/develop-exhausted.out > .tdd/exhausted-answer.txt; echo $?
```
**exit 0** is the split, **exit 1** the step needs the user and is parked, **exit 3** neither
answer. Each is a branch of its own:

- **exit 0 — split.** `.tdd/exhausted-answer.txt` holds the criteria the leaf named, one per
  line, and they **replace** the step nothing could satisfy rather than queue ahead of it —
  the criterion itself was what was wrong. Restore the tree first, since the step's rejected
  work is uncommitted and would otherwise become the first replacement step's inherited
  start, then grow the plan in **one** call and commit it:
  ```
  git reset --hard HEAD
  git clean -f -- <test-path>   # a test file Red created is untracked, so the reset leaves it
  VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/next-unchecked.sh < .tdd/issue-<n>.md)" $S/event.sh step-added anchor="$($S/next-unchecked.sh < .tdd/issue-<n>.md)" added=<count>
  VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/next-unchecked.sh < .tdd/issue-<n>.md)" $S/event.sh step-split at=exhausted anchor="$($S/next-unchecked.sh < .tdd/issue-<n>.md)" added=<count>
  $S/add-ledger-step.sh .tdd/issue-<n>.md instead-of "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" '<criterion>' …   # every line of the answer in ONE call
  git add -A && git commit -m "plan: replace <STEP summary> with <count> smaller steps (#<n>)"
  ```
  The marks go first for the reason the Green split's do: they read the title out of the
  ledger, and `instead-of` takes the step out of it (#437). The `at=exhausted` is what tells this split apart from a Green leaf's volunteered
  one: both grow the plan through `add-ledger-step.sh` and both write `step-added` and
  `step-split`, so without it a log reader cannot say whether the plan grew because a leaf
  asked or because the budget ran out — and those are different facts about the run.
  Then loop back to `next-unchecked.sh`, which now hands over the first of them. The ledger is
  committed before the run goes on because the committed ledger is what a resumed run reads:
  uncommitted, the replacement steps are lost and the step that could not be satisfied is
  handed out again. **`add-ledger-step.sh` exit 1 → bail with cause `step-too-big`** — see
  *Bailing* — exactly as a Green leaf's volunteered split does when it meets
  `VERI_STEP_GROWTH`: the criteria are filed under `## Owed steps` and the plan is unchanged.
- **exit 1 — the step needs the user.** `.tdd/exhausted-answer.txt` holds the leaf's answer:
  the criterion is wrong, contradicts another, or needs a decision this run has no authority
  to make. **Park the step** — stop the run there, carrying that answer and the verifier's
  last rejection reason (`.tdd/verify-<phase>.reason`), and leave the plan as it is so the
  user's decision picks the run back up. Post a `### ⏸️ Parked — <phase> (needs the user)`
  comment carrying `.tdd/exhausted-answer.txt` verbatim and that rejection reason, so what the
  user has to decide about is on the thread they already read rather than in a leaf log inside
  a worktree. This is a deliberate escalation, not a failure to split, so it carries a mark of
  its own rather than the split's or the bail's — it is the one outcome that stops the run
  without bailing it, and a log holding neither reads as a run that stopped saying nothing:
  ```
  VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/next-pending-refactor.sh < .tdd/issue-<n>.md || $S/next-unchecked.sh < .tdd/issue-<n>.md)" $S/event.sh step-escalated anchor="$($S/next-pending-refactor.sh < .tdd/issue-<n>.md || $S/next-unchecked.sh < .tdd/issue-<n>.md)"
  ```
- **exit 3 — neither answer.** The leaf volunteered no split and asked for no decision, so
  there is nothing new to act on: **bail the step** with cause `revise-exhausted` as a
  **process** failure (the methodology could not satisfy the blind verifier within budget),
  recording the **last rejection reason** — exactly the stop this section took before the
  leaf above existed.

A **supervisor exit 2** on that leaf is a bail like any other developer leaf's
(`killed-stuck`, a system failure): nothing answered, so no outcome was reported.

`REVISE_BUDGET` (verdict axis) is **independent** of the supervisor's `VERI_STUCK_RETRIES`
(liveness axis) and of `VERI_REFACTOR_BUDGET` (cost axis): the first governs a leaf that
finished with a bad verdict, the second a leaf that never produced one, the third how many
transforms one step's tidying is worth. A `REJECT` is veri working as designed — the blind verifier
refusing to rubber-stamp — so the bounded revise is a *correction*, never an excuse to keep
hammering past the budget.

## Reconciling a rejected push

`push-branch.sh` exit **1** means the remote holds a branch the run's HEAD does not
fast-forward — usually the run's own pre-rebase history, after a resume rebased onto
`origin/main`. Its stderr names the remote's sha. Whether those remote commits are the run's
own or someone else's is a judgement, so a leaf makes it, launched **through the
supervisor** like every other:

```
cp .tdd/issue-<n>.md .tdd/reconcile-ledger.before
$S/build-develop-prompt.sh reconcile .tdd/issue-<n>-spec.md "$($S/next-pending-refactor.sh < .tdd/issue-<n>.md || $S/next-unchecked.sh < .tdd/issue-<n>.md)" '<test-cmd>' <branch> <remote-sha> > .tdd/develop-reconcile.prompt
rm -f .tdd/develop-reconcile.exit .tdd/develop-reconcile.pid
VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/next-pending-refactor.sh || cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" $S/detach-leaf.sh $S/supervise.sh develop-reconcile $S/run-leaf.sh .tdd/develop-reconcile.prompt --permission-mode bypassPermissions > .tdd/develop-reconcile.out 2> .tdd/develop-reconcile.err
$S/wait-leaf.sh develop-reconcile   # foreground; on exit 3 call it again
```

After the leaf exits 0, re-run `$S/push-branch.sh` — it must now exit 0 — and check the
committed ledger `.tdd/issue-<n>.md` still carries every `[x]` tick and every
` ⟂ refactor pending` mark `.tdd/reconcile-ledger.before` had:

```
diff <(grep -F -e '[x]' -e '⟂ refactor pending' .tdd/reconcile-ledger.before) <(git show HEAD:.tdd/issue-<n>.md | grep -F -e '[x]' -e '⟂ refactor pending')
```

Then continue where the push was called. A leaf exit 1 or 2, a second `push-branch.sh` exit
other than 0, or a ledger whose ticks or marks changed → **bail** with cause
`reconcile-failed` (a system failure: where the branch lives broke, not the methodology).

## Bailing

A **bail** terminally stops this issue while preserving progress (ADR-0011). Each bail has
a **cause token** that maps to a classification via `$S/classify-bail.sh <cause>`:

- `killed-stuck` — `supervise.sh` exited **2** for a developer leaf even after its
  stuck-retry budget → **system** failure (plumbing broke).
- `no-verdict` — `verify.sh` exited **2** (unparseable verdict, or the verifier leaf was
  killed) → **system** failure.
- `revise-exhausted` — a step spent its `REVISE_BUDGET` and the blind verifier still says
  `REJECT` → **process** failure (methodology spoke).
- `untestable-criterion` — a Red developer leaf reported `AGAINST_UNMODIFIED: UNTESTABLE`:
  the step's criterion cannot be pinned as a lightweight, behavior-level test → **process**
  failure (the criterion as phrased cannot be tested as behavior, not that the plumbing
  broke).
- `step-too-big` — a split was refused for `VERI_STEP_GROWTH`, so the smaller steps are filed
  under `## Owed steps` rather than in the plan → **process** failure (the step was too big for
  one green; `add-ledger-step.sh` exit 1 says so, and nothing in the plumbing broke). Three
  splits lead here, because all three grow the plan and share that one budget: a Green
  developer leaf's `SPLIT:`, the split the revise-exhausted leaf answers, and the split the
  over-budget leaf answers.

**A bail reached first stays a bail**, whatever stop is waiting behind it: the methodology or
the plumbing has already answered, and a pause would hide that answer from the resume. Ask
`$S/stop-requested.sh` once before sub-step 1 and keep what it printed. A `REJECT` that
exhausts `REVISE_BUDGET` bails even with a stop pending, and a killed-stuck leaf with no `now`
pending bails as it always has — only a pending `now` turns a leaf's exit 2 into the stop
(see *Launching a leaf*). When exit 0 said one was waiting, the bail comment in sub-step 6
adds that a stop was pending, naming its mode.

To bail:

1. **Preserve the attempt first.** The tree the troubled leaf left is the evidence a reader
   of this bail will want, and the very next step throws it away — so snapshot it before the
   reset, from inside the worktree:
   ```
   $S/preserve-attempt.sh <n> "$($S/next-pending-refactor.sh < .tdd/issue-<n>.md || $S/next-unchecked.sh < .tdd/issue-<n>.md)" <phase> <attempt> bail
   ```
   `<phase>` is the leaf whose trouble caused the bail (`develop-green`, `verify-red`, …) and
   `<attempt>` its number (`1` outside the revise loop, `k` inside it). Best-effort: note it
   if it fails and bail anyway — a bail that stops for a failed snapshot loses the report too.
2. **Revert only the half-done step.** Completed steps are committed; the failing step's
   test/code is still uncommitted (the cycle bailed before its atomic green commit). Drop
   exactly that half-done work — `git reset --hard HEAD` — which leaves every completed
   step's commit (and the ledger's checked steps) intact.
3. **Classify deterministically.** `classification="$($S/classify-bail.sh <cause>)"`
   (`<cause>` is one of the tokens above). This keeps the label consistent rather than
   ad-hoc; an unknown token makes it exit non-zero — pick the right token.
4. **Render and commit the metrics**, from inside the worktree and before the push, so the
   branch carrying the progress carries the account of it too: `$S/metrics.sh <n> >
   .tdd/issue-<n>-metrics.md`, then `git add .tdd/issue-<n>-metrics.md && git commit -m
   "metrics: what bailing on #<n> cost (#<n>)"`. This is the ending the report is worth most
   at — every attempt a bailed step spent is waste, and only the file says how much.
5. **Push the branch** so completed steps, that metrics commit and the leaf logs are
   recoverable, from inside the worktree (where you already are):
   `git push -u origin tdd/<n>-<slug>` (best-effort; note if it fails).
6. Post a `### ⛔ Bailed — <phase> (<classification> failure)` comment that names the phase,
   carries the `### 📊 Metrics` block just committed, carries the last reason
   (`.tdd/verify-<phase>.reason` on a `revise-exhausted` bail, the develop-red leaf's `WHY:`
   line on an `untestable-criterion` bail, the kill cause otherwise),
   and points at the progress log (`.tdd/<phase>.log` or
   `.tdd/revise-<phase>-*.log`) for forensics. Mark the stop in the log too, with the cause
   token and the classification step 3 derived from it:
   ```
   VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/next-pending-refactor.sh < .tdd/issue-<n>.md || $S/next-unchecked.sh < .tdd/issue-<n>.md)" VERI_PHASE=<phase> $S/event.sh bail cause=<cause> classification="$classification"
   ```
7. **Leave the draft PR open, and put the bail diagnostic on it.** Step 2.3 opened it at the
   plan commit, and it is the run's claim on this issue: `solvable-issues.sh` leaves out an
   issue an open PR says `Closes #<n>` for, so taking it down would hand the issue back to
   the pool for the next machine to re-take and re-bail, and would discard the visible record
   a bail exists to leave. A bail also means a human has to look, and the draft PR is where
   they look — so the comment sub-step 6 posted to the issue thread reaches the PR too, or the
   page a reader opens still says a run is in progress when it stopped:
   ```
   gh pr view --json url -q .url          # → <pr-url>, the PR step 2.3 opened
   gh pr comment <pr-url> --body "<the same ### ⛔ Bailed — <phase> (<classification> failure) comment, or a link to the issue comment sub-step 6 posted>"
   ```
   It stays a **draft**: nobody is asked to review a run that stopped. The ledger's completed
   steps stay checked, so a re-run resumes from the failing step (see *Resume*) and edits this
   same PR rather than opening another.
8. Report to the user: the phase, the **classification** (system vs process), the reason,
   the branch name, and the **worktree path** — the logs named above are inside it, and it
   is where a re-run will resume. Leave it in place; only a merged PR retires it.

## Stopping

A **stop** is not a bail. A bail ends an issue; a stop pauses one, at an operator's word —
`stop-requested.sh` printed a mode (`at-ledger`, `at-leaf` or `now`) at a checkpoint — and
leaves the run resumable. Run this sequence in order.

1. **Settle the leaves before you touch the tree.** A live leaf owns the working tree
   (#170), so reset nothing while any `.tdd/<name>.pid` names a process still running
   `supervise.sh <name> …`. For each one that does, call `$S/wait-leaf.sh <name>` — again on
   an exit 3, as everywhere else — until it returns 0, 1 or 2. Under mode `now` that wait
   ends at once: `stop-run.sh` has already sent that supervisor its TERM, and
   `supervise.sh:350-355` recorded a 2 in the completion file.
2. **Settle the tree.** Ask first whether it is the run's to settle. If `git rev-parse
   --git-path rebase-merge` or `git rev-parse --git-path rebase-apply` names a directory
   that exists, or `MERGE_HEAD` resolves, an interrupted rebase or merge is in progress:
   **reset nothing**, record `at=unsettled`, say in the comment what a human must finish
   (`git rebase --continue` or `--abort`, `git merge --abort`) and skip the rest of this
   step. Dropping that tree would throw away conflict resolutions no commit holds yet, and
   `git reset --hard HEAD` cannot put a half-finished rebase back.
   Otherwise, and only with `git reset --hard HEAD` — a non-empty `git
   status --porcelain` is the half-done step, dropped exactly as *Bailing* step 1 drops it
   and for the reason given there. That reset is the only reach for the tree this section
   has: restoring a path out of some other tree is not what dropping a half-done step
   means. Say in the narration what was dropped.
3. **Push the branch**, `$S/push-branch.sh`, so the run's commits and leaf logs live
   somewhere a resume can reach. Exit **0** is the normal path. Exit **1** — the remote
   holds a branch this HEAD does not fast-forward — is answered here by **recording it, not
   by fixing it**: take the remote's sha from the script's stderr, record
   `push=rejected sha=<remote-sha>` and say so in the comment. A stop launches no leaves, so
   the reconcile leaf *Reconciling a rejected push* would otherwise launch is not an option;
   and a stop has no cause, so a rejected push is not a bail either — the run stays paused
   and resumable, and the resume reconciles. Exit **2** is recorded the same way.
4. **Mark the stop**, exactly once, with the boundary the run actually reached. `<at>` is
   read off the committed ledger: `at=unplanned` when there is no ledger yet, `at=planned`
   when the ledger is committed and no step is green, `at=green` when the newest ledger
   commit ticked a step that still carries `⟂ refactor pending`, `at=step-done` when every
   ticked step has had that mark taken off again, and `at=unsettled` when step 2 refused the
   tree — that last one wins over the others, because where the tree stands is the first
   thing a resume has to deal with.
   ```
   VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/next-pending-refactor.sh < .tdd/issue-<n>.md || $S/next-unchecked.sh < .tdd/issue-<n>.md)" $S/event.sh stop mode=<mode> at=<at>
   ```
   That is the whole record of the pause, and it is never a `bail` mark: a stop has no
   cause, so there is no system-versus-process label to derive and nothing to derive it
   from. Both keys ride on the one line — `mode` says which checkpoint the operator's stop
   was taken at, `at` says how far the work got — so a reader who asks "where did this run
   pause?" reads one mark, not two.
5. **Report.** Render `$S/metrics.sh <n>` — after the mark, so it reads it — straight into
   a `### 📊 Metrics` block, and post one `### ⏹️ Stopped — <mode>` comment carrying that
   block, the boundary reached (`at=<at>`), what step 2 dropped, the branch, the worktree
   path, any `push=rejected sha=<remote-sha>`, and the resume command
   `$S/run-conductor.sh <n>`. The metrics go into the comment and nowhere else: **no
   metrics file is written or committed**. Committing them marks an ending, as *Done* and
   *Bailing* do, and a stopped run will be resumed.
6. **Clear and end.** Run `$S/stop-requested.sh --clear`, so the request does not outlive
   the stop it asked for and pause the resumed run at its first checkpoint, then end the
   run. Open **no** PR and ready none; leave the worktree where it is; leave
   `.tdd/conductor.pid` in place. The resume picks all three up, and liveness is the whole
   rule (step 1.2): the conductor exiting is what frees the issue.

## Resume

The committed ledger makes a run **resumable**: re-running `/tdd <n>` picks up
where a previous run stopped (a bail, an interruption, or a human pause), without redoing
finished steps.

On re-run, step 1.2 calls `issue-worktree.sh` again; because it is **idempotent** it prints
the same `.tdd/wt/<n>` path and creates nothing, so the `cd` puts you back in the very
worktree the previous run committed in — the branch is already checked out there, and there
is nothing to re-create or switch. The **resume check** then finds an existing
`.tdd/issue-<n>.md`. When it does:

1. Do **not** re-plan — the ledger is the source of truth. Re-write only the blind spec
   file (`.tdd/issue-<n>-spec.md`) since it is run scratch, not committed.
2. **Reset the worktree, then ask for a pending refactor.** Whatever killed the previous
   run killed its leaf too, at whatever point the run had reached — a usage limit takes the
   conductor and every leaf together — so a resumed worktree may carry uncommitted work from
   a killed **Red** or **Green** leaf just as readily as from a killed refactor one. No
   verifier has seen any of it and none of it may reach the PR, so throw it away **before**
   the ask, not under one of its answers — and capture what it is about to discard first,
   because after the reset `git status --porcelain` has nothing left to report:
   ```
   stray="$(git status --porcelain)"
   git reset --hard HEAD
   ```
   `$stray` holds the paths that reset discarded, and sub-step 4 is what does the naming:
   a killed leaf's stray work is real work — the run that prompted this left a 235-line
   untracked test file behind — and it has to go loudly, not in silence.
   Then `$S/next-pending-refactor.sh < .tdd/issue-<n>.md` prints the first checked step whose
   refactor-pending mark is still there — a step the previous run left **green but not
   tidied**, because it was killed between that step's green commit and its
   verify-refactor. **Exit 3** means no step carries the mark: go to sub-step 3. Otherwise
   **STEP** is that description, and this step's refactor loop is re-entered where it
   stopped:
   ```
   green="$(git log -1 --format=%H -- .tdd/issue-<n>.md)"
   touched="$($S/refactor-touched.sh "$green")"
   count="$(git log --format=%s "$green"..HEAD | grep -c '^refactor:')"
   left=$(( ${VERI_REFACTOR_BUDGET:-5} - count )); (( left < 0 )) && left=0
   ```
   `$green` is the step's **green commit** — the last commit that changed the ledger, since
   the tick is atomic with it and the clear that would follow never happened. So `$touched`
   — that commit's `git diff --name-only`, through the same script the cycle loop calls —
   is the same bounds the interrupted loop had, and `$count` the transforms it already
   committed. Run the **Refactor loop** (the cycle loop's sub-section) with `$touched` as
   its bounds and **`VERI_REFACTOR_BUDGET=$left`** in the environment of every call that
   reads it — `refactor-budget.sh`, `build-develop-prompt.sh refactor` and
   `leaf-timeout.sh`. One leaf is handed the budget as a number and spends it, so the
   relaunched leaf gets the run's budget **reduced** by `$count`, never the ambient one:
   on the ambient number the interrupted step pays for its tidying twice over, which is the
   cost the budget exists to bound. A `$left` of 0 is a budget already spent, and
   `refactor-budget.sh 0` then skips the leaf — the step is tidied as far as it was funded
   to be. Run its **verify-refactor** after it — the check the interruption skipped — with
   `$green` as the cycle loop's `<green-sha>`:
   `verify.sh --step "<STEP>" --fast-cmd '<fast-cmd>' refactor <spec-file> <test-path> "$green"`, launched as there. Its
   PASS clears the mark and commits the cleared ledger exactly as in the cycle loop; then
   come back here and ask sub-step 2 again.
3. `next-unchecked.sh < .tdd/issue-<n>.md` gives the **first unchecked step** — the cycle
   loop continues from exactly there, so **STEP** is that step's description, bound here
   instead of at the top of the cycle loop. Already-checked steps (and their commits) are
   kept.
4. Post a `### ▶️ Resuming` comment naming that step and, when `$stray` is non-empty, the
   paths it lists, said as what they are: the stray work sub-step 2's reset discarded, seen
   by no verifier and now gone. Mark the pick-up in the log —
   `VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/next-pending-refactor.sh < .tdd/issue-<n>.md || $S/next-unchecked.sh < .tdd/issue-<n>.md)" $S/event.sh resume` — then
   **reuse the claim the previous run left on the branch**, which every tick of the cycle
   loop edits and step 4 rewrites:
   ```
   gh pr view --json url -q .url          # → <pr-url>, the PR step 2.3 opened
   ```
   A resumed run skips step 2 outright, so this is where the url comes from: it is read off
   the branch, never remembered. It edits that PR and opens **no second one** — a second
   `gh pr create` against a branch that already has an open PR is either a refusal that ends
   the resume where it started, or two pages claiming one issue, which is the failure #195
   exists to prevent. Only when this prints nothing is there **no open PR** to reuse: the
   previous run was killed inside step 2.3's own window, between the plan commit and the
   `gh pr create` that follows it. Then, and only then, run that sub-step's push and
   `gh pr create` here — opening the first PR a branch has ever had is not opening a second.
   Then run the cycle loop as normal. Go to the **draft PR** only when
   `next-pending-refactor.sh` and `next-unchecked.sh` have **both** exited 3: every step is
   checked, and every checked step's refactor is verified.

Because each step was checked off **atomically with its green commit**, the ledger and the
git history agree on exactly what is done — so resume never repeats or skips a step.

## Detecting the test command

Do not pick it by hand. Run `$S/detect-test-command.sh --issue <body-file> <repo-root>`
once, from the target repo's root, with the issue body preflight step 0.3 saved: it prints
the one full-suite command on stdout and exits 0. On **exit 3** it prints nothing — no
marker it trusts matched — so **ask the user** for the command rather than guessing.

That stdout is `<test-cmd>` everywhere it is needed: the baseline run in preflight (step
0.3) and the `<test-cmd>` argument of every `$S/build-develop-prompt.sh` call, so every
leaf runs the same suite. Detect it once, with `--issue`, and pass that one string on —
a second detection spelled without the flag would hand the leaves a different command from
the one the baseline proved green.

A `Test command: <cmd>` line in the issue body wins over everything else, for that issue's
run only: an issue that named its suite in words has already answered the question, and
that is what `--issue` puts in front of the rest. That is the per-issue escape hatch.

When the inference guesses wrong for a particular repo rather than for one issue, the fix
is that repo's, not this skill's: a human writes `.veri/test-command` there, and its first
non-empty line is used verbatim ahead of every inference. That file is the per-repo escape
hatch.

## Guardrails

- **You write no code.** Developer leaves write the test, the implementation, and the
  refactor; you orchestrate. Red and green are always performed by leaves **distinct from
  the verifier**.
- **Every leaf is launched through `supervise.sh`** — never `run-leaf.sh` or `claude`
  directly. The supervisor is the one place stuck-detection lives.
- **The run lives in its own worktree, made by `$S/issue-worktree.sh`** — never `git switch`
  or `git checkout` the caller's checkout onto the issue branch. Enter the worktree once in
  step 1.2 and stay there for the whole run; and never take over a branch another worktree
  already has checked out (the script's exit 2 is that refusal — honour it, do not work
  around it).
- **Every developer prompt is built by `$S/build-develop-prompt.sh`** — never composed from
  prose. A phase's instructions live in its template, so every run of that phase sends the
  same ones and only the variables differ; and the report lines you branch on are the
  template's own footer, not something you asked for this time.
- One failing test, then minimum code, then the refactor loop — in that order, per step.
  Never production code before its failing test.
- **A test that passes against unmodified code is never sent to verify-red**; it is either
  a blind-verified pin or a bail — never a Green.
- **The committed ledger is the source of truth.** Loop the cycle over its steps until none
  remain; check each step off **atomically with its green commit**; the issue thread only
  **mirrors** the ledger. Never hand-edit the ledger — use `tick-ledger.sh`.
- **Generality comes only from triangulation.** Overfit code is flagged for a triangulating
  test, never hand-generalized in a refactor.
- Every phase is **blind-verified** before you proceed, and **every verdict is mirrored**
  to the issue thread.
- The full suite must be green before you commit and before you open the PR: that is
  `detect-test-command.sh --tier all`'s command, run exactly once at the Draft PR step — the
  only full-suite gate left in the cycle.
- The PR is opened as a **draft** at the plan commit and readied for review at the Draft PR
  step, always carries `Closes #<n>`, and is **never merged** by you.
- On a `REJECT`, run the **bounded revise loop** (default 2 attempts, fresh leaf carrying
  the reason); if it exhausts, **bail** (process failure). On a **killed-stuck** leaf past
  its retry budget, or an unreadable verdict, **bail** (system failure). Always preserve
  commits and classify the cause. Never hand-fix the code yourself or loop past the budget.
