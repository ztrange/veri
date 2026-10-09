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
- `$S/tick-criterion.sh "<substring>"` — the pure text transform `tick-issue-criterion.sh`
  delegates to (`tick-ledger.sh` ticks through `lib/ledger.sh`'s `ledger_tick` instead): reads a checkbox body on stdin, flips the first unchecked `- [ ]` matching
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
- `$S/add-ledger-step.sh [--criterion <k>] <ledger> after|before|instead-of "<anchor substring>" '<text>' […]` — **grow
  the plan mid-run**: insert each text as `- [ ] <text> ⟦added⟧ ⟦criterion k⟧` directly after
  the anchor step, directly before it, or in its place, inheriting the anchor's criterion
  unless `--criterion <k>` names the criterion the added steps serve — any whole number k ≥ 1,
  whether or not a step already carries `⟦criterion k⟧`. `VERI_STEP_GROWTH`
  (default 5) bounds how many `⟦added⟧` steps one ledger may hold, on a **fifth axis** of its
  own — plan growth, never merged with the other four. **Exit 0** = inserted; **exit 1** = the
  budget cannot hold them, so nothing is inserted and every text is appended as a plain bullet
  under a trailing `## Owed steps` heading instead; **exit 2** = the anchor matches no step or
  more than one, the budget is unreadable, or `--criterion` names a k that is
  not a whole number ≥ 1, with the ledger left byte-identical. Every text
  one growth is made of goes in **one call**: the script takes them all at once and reads the
  budget once per call, so a call per text would refuse a third text that one call either fits
  whole or files whole. Every insertion is marked in the log beside the call it made —
  `VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current)" $S/event.sh step-added
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
  The fetch moves no local branch and touches no working tree. `<default>`'s **name** is read
  from `refs/remotes/origin/HEAD`; when that ref is absent (an origin does not guarantee one) it
  is resolved from the remote itself with `git ls-remote --symref origin HEAD`, and when the
  remote names none either it exits 2 naming `refs/remotes/origin/HEAD` — never a guessed
  `main`. A local `main`/`master` is the fallback only when there is **no origin remote** at all:
  then it supplies both the name and the **base** itself, as before. Prints the worktree's **absolute path on stdout** — the only
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
  wins: the issue body's own `Test command:` line (for `--tier all`, unless it equals the fast
  tier's command — #1225), then the repo's `.veri/test-command`,
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
  `gh`, which is what makes it testable with no network. `VERI_GH_DRIVER` picks the route
  every GitHub read and write takes, through `veri/github.py` and `lib/github.sh` alike:
  `rest` (the default when unset) runs only `gh api`, `graphql` runs only the `gh issue` /
  `gh pr` command with no fallback, and `auto` tries GraphQL then REST. Set but empty, or any
  other value, is **exit 2**, with a stderr line naming `VERI_GH_DRIVER` and the value, checked
  at call time. Operations with no GraphQL route — issue edit and create, `gh_rest_list`,
  `gh_json` with no gh args — use REST under every value, and `VERI_GH_JSON` takes precedence
  over it. A Claude Code cloud session, where GraphQL is refused, needs nothing set: the
  default is already `rest`. The conductor does not call this —
  it is rung 2's, driven by the loop branch of this skill.

## Launching a leaf — detach, then wait in the foreground

Every leaf launch below has the same three-part shape — clear the completion file, launch
detached, wait in the foreground — and each phase spells it out in full. A **developer
leaf** (red, green, refactor, revise) is launched straight through the supervisor:

```
rm -f .tdd/<name>.exit .tdd/<name>.pid
VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current)" $S/detach-leaf.sh $S/supervise.sh <name> <cmd> [args...] > .tdd/<name>.out 2> .tdd/<name>.err
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
they tick — once the step is ticked and cleared, as the text of the last `done` record
`ledger-steps.sh` prints for the ledger.
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
VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current)" $S/detach-leaf.sh $S/supervise.sh verdict-<phase> $S/run-verdict.sh --step "$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" <phase> … > .tdd/verify-<phase>.reason 2> .tdd/verify-<phase>.err
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

The same holds for the conductor's own long commands: no step backgrounds a command (the baseline or full-suite `make test` included) and ends its turn. They go through `detach-command.sh start`, then `detach-command.sh wait` in the foreground.

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
- **An `origin` remote with `refs/remotes/origin/HEAD` absent** (a cloud clone): the launch
  resolves the default branch from the remote itself (`git ls-remote --symref origin HEAD`)
  and pins to that branch's tip; when the remote's default cannot be resolved that way it is
  exit 2, stderr naming `refs/remotes/origin/HEAD`, never an unpinned run.
- **Taking the new skill is an explicit act:** `VERI_NEW_SKILL=1` on a resume replaces the
  recorded commit with the fresh tip and writes a `skill-repin` event to the run worktree's
  `.tdd/events.jsonl`, where `metrics.sh` reads it.
- **A fetch of origin that fails** before the snapshot is exit 2, since the tip it would pin
  may be stale. The one exception is `cannot lock ref`, which a parallel conductor's fetch of the
  same clone causes: that is retried, up to 60 fetches in all, `VERI_FETCH_RETRY_SLEEP` seconds
  apart (default 1, so about a minute).

**The record survives only a run that got past preflight.** After the conductor exits,
`run-conductor.sh` keeps `.tdd/issue-<n>-skill-commit` when `.tdd/wt/<n>` is registered as a
git worktree or a local `tdd/<n>-*` branch exists — what step 1.2, the first thing after
preflight, creates — and removes it otherwise, whatever the conductor's exit code. An
unregistered `.tdd/wt/<n>` directory, such as the one `VERI_NEW_SKILL=1` leaves, does not
count. So a launch that stopped at preflight pins nothing, and the next launch takes the
fresh tip.

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

These run **first**, before any cycle. If any fails, the baseline is poisoned —
**bail immediately**: report which check failed and stop. This is a degenerate bail (no
commits, nothing to revert or push) — just refuse to start. A red, dirty, or
unauthenticated baseline never gets a cycle.

1. **Git repo & clean tree.** `git rev-parse --is-inside-work-tree` succeeds and
   `git status --porcelain` is empty. If dirty, stop and ask the user to commit or stash.
   The run no longer commits in this checkout — step 1.2 moves into a worktree that is clean
   by construction — but the check **stays**: the conductor still reads the issue and the
   default branch from here, and a dirty caller's checkout means something else is mid-work
   in it.
2. **`gh` and `claude` authenticated.** `gh api user` succeeds — the same REST route every
   other GitHub read here takes; a non-zero exit from it is a preflight failure, so report it
   and stop — and `claude auth status` reports `"loggedIn": true`. Every leaf is a `claude -p` subprocess: with an expired
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
3. **Suite is green at baseline — and time it — on the commit the cycles build on.** Enter
   the issue's worktree first, as step 1.2 describes — slug from the title, exit 2 a
   preflight-class stop — and take its lock there before anything else:
   ```
   wt="$($S/issue-worktree.sh <n> <slug>)" && cd "$wt"
   mkdir -p .tdd && printf '%s\n' "$PPID" > .tdd/conductor.pid && $S/stop-requested.sh --clear
   ```
   The `--clear` beside it drops a stale stop request a killed run never got to clear, so a
   `.tdd/stop` left behind cannot stop the run that resumes it at its first checkpoint.
   Every run below happens in it, so the baseline proves the commit the branch is cut from —
   the freshly fetched `origin/<default>` for a new branch, the branch head on a resume — not
   whatever the caller's checkout has checked out.
   The issue may name its own test command,
   so read its body first — into a temp file, since the worktree must stay clean:
   ```
   body="$(mktemp)" && gh api repos/{owner}/{repo}/issues/<n> -q .body > "$body"
   ```
   Then, for `detach-command.sh`, get the fast tier's command from `$S/detect-test-command.sh --tier fast --issue "$body"` (see *Detecting the test command*),
   and run it through `$S/detach-command.sh start <name> <cmd>`, then `$S/detach-command.sh wait <name> 500` in the foreground, calling `wait` again each time it returns 3 (never background it and end the turn).
   `detach-command.sh wait` answers 0 the command passed, 1 it finished red with its code on stdout (a red suite: stop and report), 2 it died recording nothing, 3 still running (call again). If already red, stop and report a preflight
   failure, whatever the caller's checkout holds — a cycle must not start on a red baseline. Reading the body **here**, before the baseline runs, is what
   keeps the baseline and every later leaf on one command: detected after the baseline, the
   issue's line would arrive too late to be the command the baseline proved green. Note how
   long the run took and keep it as `baseline`, the elapsed wall time in whole seconds
   (round up). This measurement is free — the run happens anyway — and it is taken once, so
   a suite that gets slower mid-run does not move the timeout under a leaf.

   **Then time the full tier too.** Get its command from
   `$S/detect-test-command.sh --tier all --issue "$body"`, run it once through `detach-command.sh` in the same start-then-wait shape as the preflight baseline,
   and keep its elapsed
   wall time in whole seconds (round up) as `full`; step 7 sizes the run's hard timeout from
   that number, not from `baseline`. The full-tier run is the work a leaf actually does — a
   verifier runs this very command and a developer leaf runs the suites covering the files it
   touched — while no leaf runs the fast tier at all, so a timeout timed off the fast one
   bounds work nobody does: that is how #300's green leaf was killed at the 900 s floor
   twice over while it was working. It is timed here, with the same single-measurement rule,
   and costs one full-tier run the Draft PR gate pays for anyway. If it is red, stop and
   report, for the same reason a red fast tier stops the run.
4. **Default branch.** Capture it for the PR base:
   `gh api repos/{owner}/{repo} -q .default_branch`.
5. **Tunables parse.** Run `$S/refactor-budget.sh 0` once. **Exit 2** means
   `VERI_REFACTOR_BUDGET` is not a whole number ≥ 0 — stop and report its stderr diagnostic
   verbatim. A budget that cannot be read is a poisoned baseline like a red suite, not a
   decision, and catching it here is what lets the refactor loop treat exit 2 as impossible.
   Exit 0 and exit 3 both mean it parses (3 only says the budget is 0 — a run with the
   refactor loop switched off), so continue.

   Then run `$S/refactor-budget.sh --issue 0` once, which reads `VERI_ISSUE_REFACTOR_BUDGET`,
   the structural pass's budget, the same way: **exit 2** is the same stop, its stderr
   reported verbatim; exit 0 and exit 3 both mean it parses.

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
   and its `full` measurement to `$S/leaf-timeout.sh`, so every leaf of the run is launched
   under the result rather than under the supervisor's fixed 900 s default:
   ```
   timeout="$($S/leaf-timeout.sh "$baseline" --full "$full")"
   ```
   `--full` says which of the two measurements the timeout is sized from: the full-tier one
   displaces the fast one rather than mixing with it, because a leaf runs the full tier and
   never the fast one.
   The script keeps a quick suite on today's 900 s and gives a slow one 6 × its baseline —
   which is what stops a leaf whose own test command takes minutes being killed as stuck
   while it is working (#71: a 900 s cap against a 140-250 s suite, two bails, both steps
   reverted). An export would not survive: every Bash call is a fresh shell. So step 1.2,
   once it has entered the issue's worktree, calls the script again with the issue number,
   which records the settled number once per issue in `.tdd/issue-<n>-timeout` at the run
   worktree's root, and `supervise.sh` reads that file whenever `VERI_TIMEOUT` is unset —
   in every phase of every cycle below, and after a resume, without re-measuring; no launch
   line has to pass it. An explicit `VERI_TIMEOUT` is printed back as given, so setting one by hand still
   wins and the liveness axis stays yours. **Exit 2** means the number could not be read —
   a malformed measurement, or an explicit `VERI_TIMEOUT` that is not a whole number ≥ 1 —
   and is a preflight-class stop like step 5: report its stderr diagnostic verbatim and do
   not start, because a run whose timeout is garbage kills every leaf it launches.

### 1. Read the issue, enter the issue's worktree, capture the spec (or resume)

1. Read the issue: `gh api repos/{owner}/{repo}/issues/<n> -q '{number, title, body, url: .html_url}'`.
2. **Derive the slug and enter the issue's worktree.** Slug from the title — lowercase,
   non-alphanumerics to `-`, collapse and trim `-`, cap to ~6 words. Preflight step 3 has
   already let `issue-worktree.sh` make (or hand back) the worktree the issue branch lives
   in, and moved into it, so its baseline runs on the branch's own commit.
   Preflight step 3 took the worktree's lock there too, before the baseline: that lock is
   the **worktree guard**, and it guards this machine's worktree only: for
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
   cleanup step to forget, and a resume overwrites the dead pid with its own in preflight step 3.
   Then record the timeout preflight step 7 settled, here, where this run's `supervise.sh`
   reads it — never from the caller's checkout, where preflight ran:
   ```
   VERI_ISSUE=<n> $S/leaf-timeout.sh "$baseline" --full "$full" > /dev/null
   ```
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

**Order a step that brings in code after the steps that pin its branches.** A step that
introduces code — a port step, a new module — either comes after the steps whose tests pin
every branch it brings in, or brings in only the branches its own test requires, the rest
arriving with the steps that pin them. A branch an existing suite forces in (a fallback, a
usage header, a null guard) is still one no test of that step requires if only a later step
pins it, and the blind verify-green rejects it as unrequired code, as #760's port step was
three times over branches its ledger pinned on later lines.

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

   A criterion whose only observable is that the repository's test command passes — "the
   suites are green" — is not planned as a Red/Green step: it has no failing test to write,
   so a Red leaf could only answer `UNTESTABLE` and the run would bail. Write it as one line,
   `- [ ] <criterion> ⟦full-suite⟧ ⟦criterion k⟧`, recorded as covered by the full-suite run.

   A criterion whose deliverable is the record of a manual check — a suite broken on purpose,
   watched going red, restored — is a human's act, not code: it is not planned as a Red/Green
   step and is never handed to a developer leaf, which may not run another suite to produce
   it. Write it as one line, `- [ ] <criterion> ⟦human-owed⟧ ⟦criterion k⟧`, marked owed by a
   human.

   A criterion that is a property of the branch's own diff — something removed, something
   left unchanged, a change confined to named lines — is not planned as a Red/Green step: a
   test could only check it by reading another suite's source text or the history, which pins
   text, not behaviour. Write it as one line, `- [ ] <criterion> ⟦diff-checked⟧ ⟦criterion
   k⟧`, judged against the diff by a blind verifier; its step adds no test. A criterion
   stating a rule future changes must keep is still a Red/Green step, since it constrains
   every later diff, not only this branch's.

   A criterion replacing an implementation case under ADR 0027 with a pytest case asserting
   the same behaviour is planned as one step marked `⟦replaces-case⟧`, naming the suite path
   and a list of that suite's cases, each by its exact name: `- [ ] <criterion>: replaces
   '<case name>', '<case name>' in <suite path> ⟦replaces-case⟧ ⟦criterion k⟧`. Group
   related cases of one suite into one step, about a dozen at most; one case is a valid
   group of one. That step's Red is the pytest cases failing against the code before the
   change; its Green deletes the named bash cases and nothing else.

   A **refactor-kind** run — the spec carries the `## Refactor` section `capture-spec.sh`
   writes for the `refactor` label — changes no behaviour, so it has no failing test to plan
   around. Plan each step as one named refactoring whose criterion is a shell predicate,
   false before the step and true after it: the smell being present is the step's Red. The
   plan verifier REJECTs a refactor plan whose steps are not written that way. In a
   refactor-kind plan, fold a deletion into the step that makes the code dead: never leave a
   no-op in place for a later step to delete, whose Cover would run on code nothing reaches.
   Each step opens with a cover leaf, which mutates the code the step will move, runs the suite,
   expects red, restores and reports `COVERED:` and `CAUGHT_BY:`. If
   `git status --porcelain` prints anything once it exits, refuse to continue — stop the
   run: the transform would otherwise commit the leftover mutation as a refactoring.
   Read its report through `$S/cover-outcome.sh`: exit 2 bails as a **system** failure
   (`no-verdict`); exit 3 — `COVERED: unreachable` or `type-only` with its `PROOF:` — goes
   on to Transform without bailing or running `coverage-blocker.sh`, posting the proof it
   prints in the step's Cover comment, and for a `type-only` step saves to
   `.tdd/issue-<n>-proof` the text `cover-outcome.sh` printed after `type-only: ` — the
   proof command the transform is checked against; exit 1, `COVERED: no`, refuses the step:
   **bail with cause `uncovered`**, narrating the remedy —
   find a seam and surround the behaviour with tests first — and run
   `$S/coverage-blocker.sh <n>`, which files the coverage issue and blocks this one on it,
   so the queue cannot retake it only to refuse again.
   A refactor-kind step therefore runs **Cover → Transform → Verify**, not Red → Green →
   Refactor. After Cover, a transform leaf applies the step's one named refactoring and
   commits it; then `$S/transform-touches-tests.sh <base-sha>` reads every commit since the
   step's base sha, and exit 1 rejects the transform — a refactoring that edits a test file
   has moved the goalposts — while exit 2 is no answer. After the transform commits, the
   conductor itself — not a leaf — reruns a `type-only` step's saved proof command in
   `.tdd/issue-<n>-proof`: a non-zero exit rejects the transform as
   `transform-touches-tests.sh` exit 1 does. The blind `transform` verifier reads
   the diff from the same base sha. An abandoned refactor-kind step has no untracked test to
   clean — its transform commits are the work — so it is abandoned by resetting to its base
   sha, `git reset --hard <base-sha>`.
2. **Commit the ledger** as the run's starting point:
   `git add .tdd/issue-<n>.md && git commit -m "plan: scope #<n> into <k> steps (#<n>)"`.
   (The ledger is committed — step 1.4 guaranteed `.gitignore` tracks `.tdd/issue-*.md`
   while ignoring leaf logs.)
3. **Push the branch and open the draft PR** — the run's claim, made as the first act after
   the plan commit, from inside the worktree:
   ```
   $S/push-branch.sh
   gh api repos/{owner}/{repo}/pulls -F draft=true -f base=<default-branch> -f head="$(git branch --show-current)" \
     -f title="WIP: <type>: <criterion summary> (#<n>)" \
     -f body="Closes #<n> — work in progress: <k> steps planned. The ledger .tdd/issue-<n>.md is the source of truth." \
     -q .html_url                         # → <pr-url>; <pr-number> is its last path segment
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
`gh api repos/{owner}/{repo}/issues/<n>/comments -f body="..."`.

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

A crossing is not a failure, because the budget weighs what a step costs, not whether its work
is right — every verdict may still be a PASS — so no exit code changes meaning: `1` is still a
process failure, `2` still a system one, `3` still nothing to do.

On a crossing — the figure `step-cost.sh` printed is over the step budget — send one leaf the
`over-budget` prompt, carrying the two figures, and launch it through the supervisor the way
the `exhausted` leaf is launched. Record the crossing first, before the leaf starts: the
crossing and the leaf's answer are two facts, and a mark written only after the answer would
record nothing for a crossing whose leaf never came back:

```
VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/next-unchecked.sh < .tdd/issue-<n>.md)" $S/event.sh step-over-budget spent=<spent> budget=<step-budget>
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
  step="$($S/next-unchecked.sh < .tdd/issue-<n>.md)"; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh step-added anchor="$step" added=<count>
  step="$($S/next-unchecked.sh < .tdd/issue-<n>.md)"; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh step-split at=over-budget anchor="$step" added=<count>
  $S/add-ledger-step.sh .tdd/issue-<n>.md instead-of "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" '<criterion>' …   # every line of the answer in ONE call
  git add -A && git commit -m "plan: replace <STEP summary> with <count> smaller steps (#<n>)"
  ```
  The `at=over-budget` is what tells this split apart from the other two causes that grow a
  plan: a Green leaf volunteering one (no `at=`) and a spent revise budget (`at=exhausted`).
  The call passes no `--criterion`: a split keeps its anchor's criterion, because it is the
  same behaviour broken smaller.
  Then loop back to `next-unchecked.sh`, which now hands over the first of them.
  **`add-ledger-step.sh` exit 1 → bail with cause `step-too-big`**, as it already is on the
  other two paths that grow a plan — see *Bailing*. The split shares `VERI_STEP_GROWTH` with
  them, because all three are plan growth.
- **exit 1 — a decision for the user.** `.tdd/over-budget-answer.txt` holds the leaf's answer.
  **Park the step** — the same park the revise-exhausted path takes (see *Revise*): stop the
  run there, carrying that answer and the two figures, what the step has spent and the
  step budget, and leave the plan as it is so the user's decision picks the run back up:
  ```
  step="$($S/next-unchecked.sh < .tdd/issue-<n>.md)"; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh step-escalated at=over-budget anchor="$step"
  ```
  The `at=over-budget` is what tells this park apart from the revise-exhausted one: a verifier
  that could not be satisfied and a step that got expensive are different facts about the run.
- **exit 3 — neither answer: record the crossing and carry on with the step.** This is
  **not a bail**, and it is where this path parts from the revise-exhausted one, whose exit 3
  bails with cause `revise-exhausted` because a verifier that will not pass the work leaves
  nothing to go on with. Here nothing has failed, for the reason the section gives above, and
  bailing a converging step because it is expensive is exactly what this check exists not to do. The
  `step-over-budget` mark written before the launch already records the crossing, so this branch
  writes none of its own: leave the check disarmed, and let the step finish normally.

A **supervisor exit 2** on the over-budget leaf — `wait-leaf.sh` exits 2 — is a
**`killed-stuck` bail** like any other developer leaf's (see *Bailing*), and the step's budget
stays crossed: the check has fired for this step, and, as above, nothing re-arms it.

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
   code, no generality the test does not demand, the **test itself untouched**, the
   fast command and the affected suites green — and launch **through the supervisor** (exit **2** → **bail**, after the stop
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
   step="$($S/next-unchecked.sh < .tdd/issue-<n>.md)"; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh step-added anchor="$step" added=<count>
   step="$($S/next-unchecked.sh < .tdd/issue-<n>.md)"; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh step-split anchor="$step" added=<count>
   $S/add-ledger-step.sh .tdd/issue-<n>.md before "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" '<SPLIT: value>' …   # every SPLIT: value in ONE call
   git add -A && git commit -m "plan: split <STEP summary> into <count> smaller steps (#<n>)"
   ```
   The two marks go first because they read the step's title out of the ledger, and the
   insertion puts the first split step ahead of it there (#437). One call and not one per criterion, under the script's own one-call rule above. It passes no
   `--criterion`: a split keeps its anchor's criterion, because it is the same behaviour broken
   smaller. A split is
   the one thing that changes a step's plan without a green commit of its own, so `step-split`
   is what tells the run log the step was split rather than silently restarted — beside the
   `step-added` mark the insertion owes as any other does, which says the plan grew but not
   why. Then loop back to `next-unchecked.sh`, which now hands over the first split step;
   **STEP** itself starts again from Red once the smaller steps ahead of it are done.

   **`add-ledger-step.sh` exit 1 → bail with cause `step-too-big`** — see *Bailing*. The
   insertion would take the ledger past `VERI_STEP_GROWTH`, so the script has already filed
   the criteria under `## Owed steps`: the step's own red is discarded and the smaller steps
   it needs are not in the plan, so there is nothing for the run to go on with.
2. **Verify (blind)** — the verifier shape again, and the wait's code is again the verdict.
   Neither this verifier nor the develop leaf runs the full suite: a break outside the
   affected suites surfaces at the one full-suite run in *4. Draft PR*.
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
     gh api -X PATCH repos/{owner}/{repo}/pulls/<pr-number> -f body="Closes #<n> — work in progress: <done> of <total> steps done. The ledger .tdd/issue-<n>.md is the source of truth."
     ```
     `<done>` is the ticked checkboxes of the run's ledger `.tdd/issue-<n>.md` and
     `<total>` all of its steps — of the records `$S/ledger-steps.sh < .tdd/issue-<n>.md`
     prints, those whose second field is `done` of all of them, counted after the tick above so the step just closed is in the number. The draft PR
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
   amendment is made from: its behaviour is carried, verbatim as a criterion, into the
   `add-ledger-step.sh --criterion <k> … after "<STEP>"` call for the criterion it serves at
   6's PASS branch, one call per criterion, beside the verdict's own `uncovered-spec` flags, so
   the missing step is planned and built like any other. No other class amends
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
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current)" $S/detach-leaf.sh $S/supervise.sh verdict-refactor $S/run-verdict.sh --step "$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current)" --fast-cmd '<fast-cmd>' refactor .tdd/issue-<n>-spec.md <test-path> <green-sha> > .tdd/verify-refactor.reason 2> .tdd/verify-refactor.err
   $S/wait-leaf.sh verdict-refactor  # foreground; on exit 3 call it again
   ```
   — one verdict on the final state (the **fast tier** plus the **affected suites** still
   green, code up to standard, no smuggled generality).
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
   leftovers, which a follow-up owes, and the **cosmetic** ones, which nobody owes. A
   **test-only** or **out-of-scope** candidate is in neither list: it is recorded through
   `refactor-owed.sh`, below and at the Draft PR, and is not narrated as a backlog. Each
   list says **how many candidates** it holds and then **lists** them, one per line. A
   count with no items is not a backlog, and the two classes run together are a backlog
   nobody can size. Mark the same three figures in the log — the observed count, unclamped,
   the budget, and why it stopped (`nothing-left`, `budget`, `malformed`, `nothing-structural` for triage exit **3** or
   `structural-owed` for triage exit **0**) — and which pass of the step's refactor this is,
   `pass`: `1` for the step's first pass, and one more each time the triangulation path at 3
   resumes the refactor loop and reaches this sub-step again:
   ```
   VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/next-pending-refactor.sh < .tdd/issue-<n>.md)" VERI_PHASE=refactor $S/event.sh refactor transforms=<count> budget=<VERI_REFACTOR_BUDGET> stopped=<reason> pass="$pass"
   ```
   Then **record the leftovers themselves**, which is not a log mark and does not belong in
   that line: the narration above is a comment and `.tdd/develop-refactor.out` is overwritten
   by the next step's leaf, so **`append` is what makes the structural leftovers outlast the
   step**. It copies them — never the cosmetic ones — into the run's owed file under this
   step's name, where the Draft PR renders every step's, not just the last one's:
   ```
   $S/refactor-owed.sh append .tdd/issue-<n>-refactor-owed.md "<STEP>" "$touched" < .tdd/develop-refactor.out
   ```
   `$touched` is the step's bounds: when all are test files, a structural candidate is
   recorded test-only — "test file" being `transform-touches-tests.sh`'s rule, under `tests/`
   or named `*.test.*`, so no transform could land it.
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
     step="$($S/next-pending-refactor.sh < .tdd/issue-<n>.md)"; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh step-added anchor="$step" added=<count>
     $S/add-ledger-step.sh --criterion <k> .tdd/issue-<n>.md after "$($S/next-pending-refactor.sh < .tdd/issue-<n>.md)" '<leaf or verdict uncovered-spec behaviour>' …   # one call per criterion
     $S/clear-refactor-pending.sh .tdd/issue-<n>.md "$($S/next-pending-refactor.sh < .tdd/issue-<n>.md)"
     git add -A && git commit -m "chore: refactor verified for <STEP summary> (#<n>)"
     $S/push-branch.sh
     ```
     `git add -A` is what carries `.tdd/issue-<n>-refactor-owed.md` into that same commit:
     what `append` wrote is untracked until then, and a file left beside the worktree is
     lost with it.
     `<k>` is the number of the issue's numbered acceptance criterion the behaviour serves,
     read from the issue's `## Acceptance criteria`, not inherited from the anchor. The
     uncovered-spec behaviours, the leaf's and the verifier's, serving one criterion go in
     **one** call, under the script's own one-call rule — one call per criterion when they
     serve different ones — anchored `after "<STEP>"` so the triangulating step lands next to
     the code it triangulates. Each per-criterion call emits its own step-added event, the
     line above run once per call, anchored on the step and carrying `added=<that call's count>`. **`add-ledger-step.sh` exit 2** here means the call itself was
     malformed — a `<k>` that is not a whole number ≥ 1 — and is a **bail**. A criterion no
     ledger step serves yet is no obstacle: the script tags the new step `⟦criterion k⟧` all
     the same. Neither reporting one — no `uncovered-spec` flag
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
     "$(gh api repos/{owner}/{repo}/issues/<n> -q .body | $S/ledger-steps.sh criterion <k>)"`, the human mirror); on exit **3** tick nothing, since a step serving it is
     still open or pending. Mark
     the same moment in the log —
     `VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/ledger-steps.sh last-done < .tdd/issue-<n>.md)" $S/event.sh step-done`.
     **Then ask whether the run can still afford to finish** — this step boundary is where
     the run first knows what is left. When `next-unchecked.sh` exits 3 there is no next
     step and nothing to ask; otherwise pass it the count of steps it has still to hand
     over — the ledger's unchecked boxes under the same grammar, leaving out the
     `⟦full-suite⟧` and `⟦human-owed⟧` lines it skips, since no cycle closes those and
     counting them would overstate what is left and park a run about to finish:
     ```
     $S/next-unchecked.sh < .tdd/issue-<n>.md > /dev/null && $S/run-affordable.sh "$($S/ledger-steps.sh < .tdd/issue-<n>.md | awk -F'\t' '$2 == "open" && $3 == "step" {c++} END {print c+0}')"
     ```
     On exit **0** — or exit **3**, when no full step has completed yet and so there is no
     median to project with — loop back to the top of **step 3** for the next unchecked
     ledger step.
     On exit **1** the projection is over the ceiling: **park the run** here, while parking
     is still cheap — the ledger is committed, so a resume loses none of what was spent.
     Post a `### ⏸️ Parked — run budget (needs the user)` comment carrying the projection
     rather than the fact: the spent, steps remaining, median and projection figures
     `run-affordable.sh` printed, the ceiling (`VERI_RUN_BUDGET`, the second line
     `step-budget.sh` printed), and the two answers available — raise `VERI_RUN_BUDGET` and
     resume, or split the issue, since a run projected far past its ceiling is usually one
     whose issue was too big, a decision no leaf has the authority to make.
     This park is **not a bail**: nothing failed, and the ledger is at a state a resume
     already handles — so `classify-bail.sh` is not called on it.
     On exit **2** no answer could be obtained — a missing event log, a bad
     `VERI_RUN_BUDGET`, a count that is not a whole number — a system failure, not a
     projection: **bail**. (Earlier steps' commits are preserved.)
   - **REJECT (exit 1):** enter the **revise loop**; on recovered PASS, mirror and loop; on
     budget-exhausted, **bail**. (Earlier steps' commits are preserved.)
   - **Malformed / killed-stuck (exit 2):** **bail**. (Earlier steps' commits are preserved.)

Neither the refactor leaf nor verify-refactor runs the full suite: a break in a suite none of
the step's transforms touched surfaces at the one full-suite run in *4. Draft PR*, where a red
result appends a repair step.

#### A `⟦diff-checked⟧` step — develop-diff, then verify-diff (blind)

A `⟦diff-checked⟧` step runs no Red leaf, and no Green or Refactor phase either: its
criterion is a property of the branch's own diff, so there is no failing test to write and
its step adds none. On a fresh run and on a resume alike, the step base sha is the last
commit that changed the ledger — the previous step's tick — never a `HEAD` taken after a
killed `develop-diff` attempt's commit: record it with `git log -1 --format=%H -- .tdd/issue-<n>.md` before the `develop-diff` leaf
runs. On a fresh step, `git rev-parse HEAD` taken before the `develop-diff` leaf runs names
that same commit, since every step ends in a ledger commit; on a resume it may not. That leaf, built by `build-develop-prompt.sh diff <spec-file>
"<STEP>" '<test-cmd>' '<fast-cmd>'`, makes the change the criterion names — or makes no
commit, when the criterion is that something stays unchanged — and keeps the fast tier and
then the affected suites green before it reports. Then the blind `diff` verifier,
`run-verdict.sh --step "<STEP>" --fast-cmd '<fast-cmd>' diff <spec-file> <branch-base-sha> <step-base-sha>`, runs the fast tier and then the affected suites, rejecting the step when
either is red, and judges it against the run's branch point, `git merge-base HEAD
origin/<default>`, and its own diff from the step base sha. Both are launched through the supervisor and waited on as
*Launching a leaf* sets out, the leaf as `develop-diff` and the verifier as `verdict-diff`.

A supervisor exit 2 on the `develop-diff` leaf is a `killed-stuck` bail, as for any developer
leaf. The verifier's verdict closes the `⟦diff-checked⟧` step:

- **PASS (exit 0):** tick the `⟦diff-checked⟧` step with `tick-ledger.sh` — without
  `--refactor-pending`, since no refactor loop follows — commit the ledger and push it as
  Green does, post `### ✅ Step done`, then tick its criterion in the issue body with `tick-issue-criterion.sh` on
  `criterion-finished.sh` exit 0, ticking nothing on exit 3, exactly as a Refactor loop's
  PASS does.
- **REJECT (exit 1):** a revise of the `⟦diff-checked⟧` step's `develop-diff` work under
  `REVISE_BUDGET` — see *Revising on a REJECT*; on a recovered PASS tick as above, on
  budget-exhausted **bail**.
- **Malformed / killed-stuck (exit 2):** no verdict on the `⟦diff-checked⟧` step could be
  obtained, so **bail** as a system failure (`no-verdict`) — see *Bailing*.

### 4. Draft PR

Reached when `next-unchecked.sh` exits 3 — every ledger step is checked off but the
`⟦full-suite⟧` and `⟦human-owed⟧` lines, which that script skips and no cycle closes: an
unchecked line carrying either does not hold the run back from this step. The full suite
must be green before this step: run `$S/detect-test-command.sh --tier all`'s command via `detach-command.sh` here,
in the same start-then-wait shape as the preflight baseline, exactly once — the branch's own full-suite gate, since every leaf runs the fast
command, the affected suites, or both. That nothing is left uncommitted and no step is still only
green is not taken on trust here — sub-step 1 asks. Like every step since 1.2, this one runs
**from inside the worktree** — every command below is issued there, so each sees the issue
branch and its commits without any switching.

A red result on that full run does not bail: append a repair step to the ledger, commit it,
and return to step 3, *The cycle loop* — the failing suites are that step's red evidence. The
repair step's text lists every suite the full run left red, each with its first `FAIL -` line;
the develop and verify prompts take that list from the step's text through their templates,
and the conductor never edits a built prompt to add a suite one of them left out. Its
developer adds a unit-tier test when the failure exposes a gap the fast tier missed, and its
verifier judges the fix against the full command, not the fast one.
```
step="$($S/ledger-steps.sh last-done < .tdd/issue-<n>.md)"; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh step-added anchor="$(printf %s "$step")" added=1
$S/add-ledger-step.sh .tdd/issue-<n>.md after "$($S/ledger-steps.sh last-done < .tdd/issue-<n>.md)" '<fix the full-suite failure: <suite> — <its FAIL - line>> ⟦suite-repair⟧'
git add .tdd/issue-<n>.md
git commit -m "plan: repair the red full suite (#<n>)"
```
That call passes no `--criterion` on purpose: the repair step serves its anchor's criterion.

A second red result on the full run after a repair step does **bail** — the repair step is
one more cycle, not a loop — and the bail names every suite still red, not only the first.
A `⟦suite-repair⟧` line already in the ledger is what says the red run is the second:
```
grep -F '⟦suite-repair⟧' .tdd/issue-<n>.md > /dev/null && VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=suite-red classification="$($S/classify-bail.sh suite-red)" suites='<every suite still red>'
```

The branch's own full run comes first, and it, with any `⟦suite-repair⟧` step it adds, has to
finish green before sub-step 1 runs `rebase-onto-default.sh`: the rebased tip's run there is
the extra run a rebase owes, never a replacement for the branch's own.

A `⟦full-suite⟧` ledger line is the one step no cycle ticks — `next-unchecked.sh` skips it,
so it is still unchecked here — and this step ticks it, only once the run's last full-suite
run before the PR is readied is green: the rebased tip's run when sub-step 1 rebased the
branch, this step's own run otherwise. Tick each with `tick-ledger.sh`, handed the literal
matcher `'⟦full-suite⟧'` and called again until it exits 3, and without `--refactor-pending`,
so the line carries no refactor-pending mark (it has no refactor loop to clear one); for each
line's `⟦criterion k⟧` tick the issue criterion it finishes (`$S/tick-issue-criterion.sh <n>
"$(gh api repos/{owner}/{repo}/issues/<n> -q .body | $S/ledger-steps.sh criterion <k>)"`),
and commit the ledger before sub-step 2. A red run ticks nothing: never tick a `⟦full-suite⟧` line after a
red full-suite run, whatever an earlier run said.

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
   Once both have gone quiet, bring the branch up to the default one, which may have moved
   while the run worked:
   ```
   $S/rebase-onto-default.sh
   ```
   An exit 3 from `rebase-onto-default.sh` — the branch already contains `origin/<default>` —
   continues unchanged to sub-step 2. An exit 2 from `rebase-onto-default.sh` — no answer
   could be obtained, such as an origin that cannot be fetched — does **bail**, as a
   **system** failure (`no-verdict`), with the PR left a draft. An exit 0 — the branch was
   behind and the rebase applied cleanly — has changed the tree, and the first line it
   printed is `<pre-rebase-sha>`, the sha the branch held before the rebase. The rebased tip
   is a tree no suite has run on, and two green branches can combine into a red one, so run
   the full test command (`$S/detect-test-command.sh --tier all`'s, via `detach-command.sh`) once on the rebased tip,
   in the same start-then-wait shape as the preflight baseline, and read its exit code from `wait`.
   A red result on the rebased tip does **bail**, as a **process** failure
   (`rebased-tip-red`), with the PR left a draft: it is never readied. Before *Bailing*'s push,
   `git reset --hard <pre-rebase-sha>` puts the branch back where it stood, so that push is a
   fast-forward and the un-rebased branch is what is kept. On green, publish the rewritten history:

       $S/push-branch.sh --force-with-lease=<branch>:<pre-rebase-sha>

   The lease is pinned to `<pre-rebase-sha>`, so a remote copy another writer moved in the
   meantime is refused rather than clobbered. Never a bare force, which replaces the remote
   copy whatever is there.

   An exit 1 from `rebase-onto-default.sh` — the rebase conflicted and was aborted, so HEAD
   is back where it stood with a clean tree — prints the conflicting files, one per line.
   Resolving them writes new code no verifier has seen, so a `develop-rebase` leaf does it,
   launched **through the supervisor** like every other, and a blind `verify-rebase` judges
   the resolution before the PR is readied:
   ```
   git rev-parse origin/<default>   # → <onto-sha>
   git rev-parse HEAD               # → <pre-rebase-sha>
   $S/build-develop-prompt.sh rebase .tdd/issue-<n>-spec.md "$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" '<test-cmd>' <onto-sha> <pre-rebase-sha> "<conflicting-files>" > .tdd/develop-rebase.prompt
   rm -f .tdd/develop-rebase.exit .tdd/develop-rebase.pid
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" $S/detach-leaf.sh $S/supervise.sh develop-rebase $S/run-leaf.sh .tdd/develop-rebase.prompt --permission-mode bypassPermissions > .tdd/develop-rebase.out 2> .tdd/develop-rebase.err
   $S/wait-leaf.sh develop-rebase   # foreground; on exit 3 call it again
   rm -f .tdd/verdict-rebase.exit .tdd/verdict-rebase.pid
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" $S/detach-leaf.sh $S/supervise.sh verdict-rebase $S/run-verdict.sh --step "$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" rebase .tdd/issue-<n>-spec.md <onto-sha> <pre-rebase-sha> > .tdd/verify-rebase.reason 2> .tdd/verify-rebase.err
   $S/wait-leaf.sh verdict-rebase   # foreground; on exit 3 call it again
   ```
   A verify-rebase `REJECT` goes round *Revising on a REJECT* with phase `rebase`, within
   `REVISE_BUDGET` like any other phase; a malformed verdict does **bail** as a **system**
   failure (`no-verdict`).
   Only on a verify-rebase `PASS` does the run go on to ready the PR, and first as on exit 0:
   the full test command once on the rebased tip, a bail on red (`rebased-tip-red`) with
   `git reset --hard <pre-rebase-sha>` before *Bailing*'s push, and on green the push under
   the lease pinned to `<pre-rebase-sha>`.

   A rebase not resolved within budget — the leaf reports `REBASE: FAILED` or exits 1 or 2,
   a killed leaf among them, or `REVISE_BUDGET` runs out on verify-rebase `REJECT`s — has
   left a resolution no verifier passed on the branch, so first put the branch back where it
   stood:
   ```
   git reset --hard <pre-rebase-sha>
   ```
   The branch is left un-rebased, and the run does **bail** with the PR left a draft, its
   bail comment naming every conflicting file `rebase-onto-default.sh` printed, so the human
   it hands the conflict to knows where it is.

   Then run the issue's **one structural pass**, once, before the PR is readied: the
   structural candidates the steps recorded rather than applied, each taken up by one
   `structural` transform leaf, bounded to every file the issue touched and counted against
   the issue's budget, not a step's. The conductor runs the pass whenever
   `refactor-owed.sh list` prints a candidate, and never skips or shortens it for cost: the
   way to spend less is to set a lower `VERI_ISSUE_REFACTOR_BUDGET` before launch, and the
   candidates past the budget are filed by `refactor-overflow.sh`:
   ```
   git merge-base HEAD origin/<default>                 # → <issue-base>
   $S/refactor-touched.sh --issue <issue-base>          # → <issue-touched-files>
   $S/refactor-owed.sh list .tdd/issue-<n>-refactor-owed.md   # one candidate per line; exit 3 ⇒ no pass
   ```
   A candidate recorded test-only is never listed, so it launches no predicate or
   transform leaf; `render` still shows it under `### Test-only` in the PR body.
   For each candidate, in the order `refactor-owed.sh list` prints them — most valuable first —
   `<count>` being the transforms the pass has already landed:
   ```
   $S/refactor-budget.sh --issue <count>   # exit 0 ⇒ launch; exit 3 ⇒ the pass is over
   git rev-parse HEAD                      # → <base-sha>
   ```
   This is where each candidate's predicate comes from: before its transform leaf, a
   predicate leaf, prompted by `build-develop-prompt.sh predicate` with the same four
   arguments and launched through the supervisor as `develop-predicate`, reports one
   `PREDICATE:` line, which the conductor checks and records:
   ```
   $S/structural-predicate.sh .tdd/issue-<n>-predicate < <leaf-report>   # exit 0 ⇒ recorded; 1 ⇒ already applied; 3 ⇒ skip
   ```
   That record is the test path the transform verifier runs, in place of the prose
   candidate. A candidate with no predicate is skipped — only exit 3, for
   `PREDICATE: NONE`, appends it to `.tdd/issue-<n>-predicate-skipped`, the
   `<skipped-file>`, rather than handing it to a transform leaf; exit 1, a command already
   true, means the candidate is already applied, and it is recorded as applied below
   without a transform leaf; exit 2 is no answer.
   Each transform leaf's prompt is `build-develop-prompt.sh structural`'s, handed the spec, the candidate as
   `list` printed it, the test command and `<issue-touched-files>`, written to
   `.tdd/develop-structural.prompt`; the leaf is launched through the supervisor as
   `develop-structural`. Its commits are checked with
   `$S/transform-touches-tests.sh <base-sha>` — exit 1 rejects the transform, exit 2 is no
   answer — then judged by the long
   refactor's blind `transform` verifier against `<base-sha>`, one commit per transform —
   both before the next candidate's leaf is launched. A `REJECT` resets to `<base-sha>` and moves on to the next candidate.
   ```
   rm -f .tdd/verdict-transform.exit .tdd/verdict-transform.pid
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" $S/detach-leaf.sh $S/supervise.sh verdict-transform $S/run-verdict.sh --step "$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" transform .tdd/issue-<n>-spec.md .tdd/issue-<n>-predicate <base-sha> > .tdd/verify-transform.reason 2> .tdd/verify-transform.err
   $S/wait-leaf.sh verdict-transform   # foreground; on exit 3 call it again
   ```
   A `PASS` records the candidate as applied, with the commit that applied it, so `render`
   lists it as applied rather than owed; a candidate `structural-predicate.sh` exited 1 for
   launches no transform leaf and is recorded the same way, at the current HEAD, so
   `refactor-overflow.sh` never files it:
   ```
   $S/refactor-owed.sh applied .tdd/issue-<n>-refactor-owed.md '<candidate>' "$(git rev-parse HEAD)"
   git add .tdd/issue-<n>-refactor-owed.md
   git commit -m "chore: record the structural pass's applied candidate (#<n>)"
   ```
   Once the pass ends — the candidates run out, or the budget is spent — mark it once, with
   the transforms it landed, its budget and why it stopped. `stopped=` takes only
   `candidates-done`, `budget-spent` or `nothing-structural`, and `budget-spent` is marked
   only when `refactor-budget.sh --issue` exited 3, i.e. `transforms` equals the budget:
   ```
   VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh structural-pass transforms=<count> budget=<VERI_ISSUE_REFACTOR_BUDGET> stopped=<reason>
   ```
   Before any `refactor-overflow.sh` call below, every out-of-scope candidate is re-checked
   against the tree, since a later plan step may have applied it:
   ```
   $S/refactor-owed.sh out-of-scope .tdd/issue-<n>-refactor-owed.md   # one candidate per line; exit 3 ⇒ none
   ```
   For each, a `develop-predicate` leaf is launched as above and its report checked with
   `structural-predicate.sh`; exit 1 records it applied, with its marker, so the filing leaves
   it out:
   ```
   $S/refactor-owed.sh applied .tdd/issue-<n>-refactor-owed.md 'out-of-scope | <candidate>' "$(git rev-parse HEAD)"
   ```
   Any other exit leaves it to be filed.
   A pass marked `stopped=budget-spent` left candidates no leaf reached, and a pass that
   skipped a candidate left one no leaf worked; file them as one unlabelled issue naming
   this one, `<taken>` being the candidates the pass took up, skipped ones included, and
   `<skipped-file>` passed only when it exists:
   ```
   $S/refactor-overflow.sh <n> .tdd/issue-<n>-refactor-owed.md <taken> <skipped-file>   # → <overflow-url>
   ```
   With nothing skipped, a pass that ends `candidates-done` or `nothing-structural` files nothing
   but the owed file's out-of-scope candidates, still handed to `refactor-overflow.sh` with
   `<taken>` being every candidate it took up:
   ```
   $S/refactor-overflow.sh <n> .tdd/issue-<n>-refactor-owed.md <taken>   # exit 3 ⇒ nothing to file
   ```
   The filing applies no label to this issue and commits no debt file: the PR body's owed
   list is the record.
   No candidate — `list` exits 3, and a missing `.tdd/issue-<n>-refactor-owed.md` is the
   `list` exit-3 case — skips the pass with no bail: it is marked `stopped=nothing-structural`
   before the PR is readied:
   ```
   VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh structural-pass stopped=nothing-structural
   ```
   A candidate recorded out-of-scope is never listed either, so it launches no leaf; when
   `list` exits 3 the owed file's out-of-scope candidates are still handed to
   `refactor-overflow.sh` with `<taken>` 0, and filed as `Refactor owed by #<n>`:
   ```
   $S/refactor-overflow.sh <n> .tdd/issue-<n>-refactor-owed.md 0   # exit 3 ⇒ nothing to file
   ```
2. **Mark the PR ready for review and read its CI, then close the run's log with the PR's
   URL, render the metrics, commit them, and rewrite the PR into its final form** — one
   sub-step, in this order, from inside the worktree. **This step opens no PR.** Step 2.3 opened it at the plan commit, so
   there is nothing left here for a PR-creating `gh api` call to do: a second one against a branch that
   already has an open PR is either a refusal that ends the run at its last step, or a second
   PR for the same branch — and then the claim another machine reads and the page a human is
   asked to merge are two different pages. Read the existing PR's URL rather than assuming the
   run remembers it, so a resumed run edits the PR its branch already has:
   ```
   gh api 'repos/{owner}/{repo}/pulls?head={owner}:{branch}' -q '.[0].html_url // empty'   # → <pr-url>, the PR step 2.3 opened; <pr-number> is its last path segment
   . $S/lib/github.sh && gh_pr_ready <pr-number> "$(git rev-parse HEAD)"
   $S/wait-ci.sh <pr-url> 540 "" "$(git rev-parse HEAD)" 2> .tdd/wait-ci.err; ci=$?    # exit 3 → run this line again, in a new Bash call
   grep -F 'conflicts with its base branch' .tdd/wait-ci.err > /dev/null; conflict=$?
   [ "$ci" != 2 ] || [ "$conflict" = 0 ] || VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=ci-timeout classification="$($S/classify-bail.sh ci-timeout)"
   [ "$ci" != 2 ] || [ "$conflict" != 0 ] || [ ! -e .tdd/ci-conflict-rebased ] || VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=ci-conflict classification="$($S/classify-bail.sh ci-conflict)"
   gh api "repos/{owner}/{repo}/commits/$(git rev-parse HEAD)/check-runs" -q '.check_runs[] | {name, status, conclusion}'
   gh run view <run-id> --log-failed          # a failed check only → its suite and FAIL - line
   grep -F '⟦ci-repair⟧' .tdd/issue-<n>.md > /dev/null && VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=ci-red classification="$($S/classify-bail.sh ci-red)" failed="$(gh api "repos/{owner}/{repo}/commits/$(git rev-parse HEAD)/check-runs" -q '[.check_runs[] | select(.conclusion != null and (.conclusion | ascii_upcase | IN("SUCCESS", "NEUTRAL", "SKIPPED") | not)) | .name] | join(",")')"
   step="$($S/ledger-steps.sh last-done < .tdd/issue-<n>.md)"; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh step-added anchor="$(printf %s "$step")" added=1
   $S/add-ledger-step.sh .tdd/issue-<n>.md after "$($S/ledger-steps.sh last-done < .tdd/issue-<n>.md)" '<fix the CI failure: <suite> — <its FAIL - line>> ⟦ci-repair⟧'
   git add .tdd/issue-<n>.md
   git commit -m "plan: repair the red CI check (#<n>)"
   ```
   That call passes no `--criterion` on purpose: the repair step serves its anchor's criterion.
   A `ci-timeout` or `ci-red` bail ends the step there and goes to *Bailing*: neither the
   `done` mark nor the `metrics:` commit below follows it. Otherwise:
   ```
   VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh done pr=<pr-url>
   $S/metrics.sh <n> > .tdd/issue-<n>-metrics.md; metrics=$?
   if [ "$metrics" = 0 ]; then
     git add .tdd/issue-<n>-metrics.md
     git commit -m "metrics: what solving #<n> cost (#<n>)"
   fi
   $S/push-branch.sh
   $S/wait-ci.sh <pr-url> 540 "" "$(git rev-parse HEAD)"; ci=$?    # exit 3 → run this line again, in a new Bash call
   [ "$ci" != 1 ] || VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=ci-red classification="$($S/classify-bail.sh ci-red)" failed="$(gh api "repos/{owner}/{repo}/commits/$(git rev-parse HEAD)/check-runs" -q '[.check_runs[] | select(.conclusion != null and (.conclusion | ascii_upcase | IN("SUCCESS", "NEUTRAL", "SKIPPED") | not)) | .name] | join(",")')"
   [ "$ci" != 2 ] || VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=ci-timeout classification="$($S/classify-bail.sh ci-timeout)"
   $S/refactor-owed.sh render .tdd/issue-<n>-refactor-owed.md
   gh api -X PATCH repos/{owner}/{repo}/pulls/<pr-number> -f title="<type>: <criterion summary> (#<n>)" -f body="<Closes #<n> — summary: the plan's steps, each a blind-verified R→G→R cycle, ledger committed; followed by the contents of .tdd/issue-<n>-metrics.md (or, when $metrics is not 0, the line 'metrics could not be rendered: metrics.sh exited $metrics' in its place), followed by that render's output, followed by the ledger's ## Owed steps bullets, followed by its ⟦human-owed⟧ lines under ## Owed by a human, followed by <overflow-url>, the issue refactor-overflow.sh filed, when the pass filed one>"
   ```
   The readied PR's CI is read fail-closed, the way the `merge` skill reads it: an empty
   rollup is never a pass, and a completed check whose conclusion is anything other than
   `SUCCESS`, `NEUTRAL` or `SKIPPED` counts as failed. A pending check never counts as
   green, and the wait is `wait-ci.sh`, one bounded slice per Bash call, given the sha just
   pushed (`git rev-parse HEAD`) so a rollup still reporting the previous head reads as pending: its exit 3 means a
   check is still pending, so call it again in a new Bash call; its exit 2 — a check still
   pending past the deadline its first call recorded, or no answer from `gh` — does
   **bail**, with cause `ci-timeout`, rather than waiting on.
   That deadline is `wait-ci.sh`'s own bound, since the call gives no total-seconds: twice the
   mean of the last 5 completed CI runs, capped at 10 minutes, or 540 s when fewer than 5
   exist or `gh` cannot answer.
   A failed check does not bail: read its run's log with `gh run view <run-id> --log-failed`,
   append a repair step to the ledger whose text quotes the failing suite and its `FAIL -`
   line — or the error line, when the suite died before writing one — commit the ledger, and
   return to step 3, *The cycle loop*, without the `done` mark: the quoted line is that
   step's red evidence, the same way a red full run's repair step is.
   A second red CI result after a CI repair step does **bail**, with cause `ci-red`, the way
   a second red full run does — the repair step is one more cycle, not a loop.
   A conductor never re-runs a failed CI job — no `gh run rerun`, no re-run of a failed
   check: a red check is answered only by the repair step or the `ci-red` bail above, since
   a re-run can turn a real failure into one that reads as a flake. Re-running a known flake
   is the operator's decision, made outside a run.
   That bail greps for `⟦ci-repair⟧` only: a ledger holding a `⟦suite-repair⟧` step and no
   `⟦ci-repair⟧` step still gets its one CI repair attempt.
   A `wait-ci.sh` exit 2 whose stderr names a conflict — the PR conflicts with its base
   branch, so no workflow will start on it — is not a timeout. Rebase onto
   `origin/<default>` once, through the existing rebase path of sub-step 1: `touch
   .tdd/ci-conflict-rebased`, then `$S/rebase-onto-default.sh`, its `develop-rebase` leaf and
   rebase verifier (`verify-rebase`) when it conflicts, the full suite once on the rebased
   tip, and the push under the lease pinned to `<pre-rebase-sha>` — then wait for CI again
   with the same `wait-ci.sh` line. A second conflict, with `.tdd/ci-conflict-rebased`
   already present, does **bail**, with cause `ci-conflict`, rather than rebasing again.
   The `metrics:` push starts a CI run of its own on the readied PR, so it is read the same
   way, by `wait-ci.sh` after the push; the commit carries no code, so its red is not a
   repair step: exit 1 bails with cause `ci-red` and exit 2 with cause `ci-timeout`.
   The `done` mark comes before the render because `metrics.sh` reads it for both the Outcome
   and the issue's wall time: a report rendered before it exists says `unknown` for both. The
   body is rewritten only after the `metrics:` commit is pushed, so it never quotes a file the
   branch does not yet carry. The title drops the `WIP:` prefix step 2.3 opened it with, and
   `gh_pr_ready` is what turns the run's claim into a review request: a finished run that left
   a draft behind asks nobody to look.
   `<type>` is **`fix`** on a bug run — the issue carries the `bug` label, so the title
   starts with the `fix:` prefix, the same prefix its green commits took — **`refactor`** on
   a refactor-kind run, the issue labelled `refactor`, so the title starts with the
   `refactor:` prefix — and `feat` otherwise. A bug run's PR titled `feat:` announces to the
   human deciding the merge a capability the run did not add, and so does a refactor run's.
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
   What a human still owes is copied last: every `⟦human-owed⟧` ledger line — a record of a
   manual check, which no cycle ticks — goes into the PR body under an `## Owed by a human`
   heading, each listed with its criterion number from its `⟦criterion k⟧` mark, so the
   reviewer sees which issue criterion is still waiting on them. A ledger holding no
   `⟦human-owed⟧` line adds no such section.
3. **Never merge the PR.** Landing the code is always the human's deliberate act.
4. Post a final `### ✅ Done — <pr-url>` comment with the same `### 📊 Metrics` block
   under it, pasted verbatim from the file just committed — or, when `$metrics` is not 0,
   the PR body's failed-render line for `metrics.sh` and `$metrics` in place of that block.
   It mirrors the
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
  **issue body** (`$S/tick-issue-criterion.sh <n> "$(gh api repos/{owner}/{repo}/issues/<n> -q .body | $S/ledger-steps.sh criterion <k>)"`) — on exit **3** tick
  nothing — and mark it in the log —
  `VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/ledger-steps.sh last-done < .tdd/issue-<n>.md)" VERI_PHASE=pin $S/event.sh pin`.
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
   VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" VERI_PHASE=<phase> VERI_ATTEMPT=<k> $S/event.sh revise budget=<REVISE_BUDGET>
   ```
2. **Fresh developer leaf.** Build the revise prompt from the `revise` template, naming the
   phase being redone and the **reason file** the verifier's stdout went to, then launch
   **through the supervisor** (exit **2 → bail**, system failure, after the stop check in
   *Launching a leaf*):
   ```
   $S/build-develop-prompt.sh revise <phase> .tdd/issue-<n>-spec.md "$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" '<test-cmd>' .tdd/verify-<phase>.reason '<fast-cmd>' > .tdd/revise-<phase>-<k>.prompt
   rm -f .tdd/revise-<phase>-<k>.exit .tdd/revise-<phase>-<k>.pid
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" $S/detach-leaf.sh $S/supervise.sh revise-<phase>-<k> $S/run-leaf.sh .tdd/revise-<phase>-<k>.prompt --permission-mode bypassPermissions > .tdd/revise-<phase>-<k>.out 2> .tdd/revise-<phase>-<k>.err
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
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" $S/detach-leaf.sh $S/supervise.sh verdict-<phase> $S/run-verdict.sh --step "$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" --fast-cmd '<fast-cmd>' <phase> .tdd/issue-<n>-spec.md <test-path> [target] > .tdd/verify-<phase>.reason 2> .tdd/verify-<phase>.err
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

**The `diff` phase.** A REJECT on a `⟦diff-checked⟧` step runs the same loop with `<phase>`
set to `diff`, with two differences: no `step-cost.sh` line and no prediction check, since the
step has no failing test, and a re-verify that is the blind `diff` verifier rather than one
with a test path. The revise leaf is built as:
```
$S/build-develop-prompt.sh revise diff .tdd/issue-<n>-spec.md "$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" '<test-cmd>' .tdd/verify-diff.reason '<fast-cmd>' > .tdd/revise-diff-<k>.prompt
```
and launched as `revise-diff-<k>` like any revise leaf. The re-verify is `run-verdict.sh
--step "<STEP>" --fast-cmd '<fast-cmd>' diff <spec-file> <branch-base-sha> <step-base-sha>`, launched as `verdict-diff`
with its stdout overwriting `.tdd/verify-diff.reason`, and each `<base-sha>` is the same base sha
the original verify-diff verdict ran against — the run's branch point, and the step base sha
recorded before the step's develop-diff leaf ran, not one recorded before the revise leaf — so
the revised work is judged against the diff the rejection was about. A
recovered PASS on the `⟦diff-checked⟧` step is ticked exactly as the `⟦diff-checked⟧` PASS
bullet in *A `⟦diff-checked⟧` step* describes.

If all `REVISE_BUDGET` attempts are still `REJECT`, the step is **not** bailed on the spot. A
criterion no blind verifier could be satisfied about in that many attempts is usually a
criterion carrying more than one behaviour — the very condition `SPLIT:` exists for — so send
one last leaf and ask it which of the two is true of this step, rather than deciding that
yourself. The reason file the last re-verify overwrote is the whole of what it is told:

```
$S/build-develop-prompt.sh exhausted .tdd/issue-<n>-spec.md "$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" '<test-cmd>' .tdd/verify-<phase>.reason > .tdd/develop-exhausted.prompt
rm -f .tdd/develop-exhausted.exit .tdd/develop-exhausted.pid
VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" $S/detach-leaf.sh $S/supervise.sh develop-exhausted $S/run-leaf.sh .tdd/develop-exhausted.prompt --permission-mode bypassPermissions > .tdd/develop-exhausted.out 2> .tdd/develop-exhausted.err
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
  step="$($S/next-unchecked.sh < .tdd/issue-<n>.md)"; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh step-added anchor="$step" added=<count>
  step="$($S/next-unchecked.sh < .tdd/issue-<n>.md)"; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh step-split at=exhausted anchor="$step" added=<count>
  $S/add-ledger-step.sh .tdd/issue-<n>.md instead-of "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" '<criterion>' …   # every line of the answer in ONE call
  git add -A && git commit -m "plan: replace <STEP summary> with <count> smaller steps (#<n>)"
  ```
  The marks go first for the reason the Green split's do: they read the title out of the
  ledger, and `instead-of` takes the step out of it (#437). Like every split, the call passes
  no `--criterion`: a split keeps its anchor's criterion, because it is the same behaviour
  broken smaller. The `at=exhausted` is what tells this split apart from a Green leaf's volunteered
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
  step="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)"; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh step-escalated anchor="$step"
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
$S/build-develop-prompt.sh reconcile .tdd/issue-<n>-spec.md "$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" '<test-cmd>' <branch> <remote-sha> > .tdd/develop-reconcile.prompt
rm -f .tdd/develop-reconcile.exit .tdd/develop-reconcile.pid
VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" $S/detach-leaf.sh $S/supervise.sh develop-reconcile $S/run-leaf.sh .tdd/develop-reconcile.prompt --permission-mode bypassPermissions > .tdd/develop-reconcile.out 2> .tdd/develop-reconcile.err
$S/wait-leaf.sh develop-reconcile   # foreground; on exit 3 call it again
```

After the leaf exits 0, re-run `$S/push-branch.sh` — it must now exit 0 — and check the
committed ledger `.tdd/issue-<n>.md` still carries every `[x]` tick and every
` ⟂ refactor pending` mark `.tdd/reconcile-ledger.before` had:

```
diff <($S/ledger-steps.sh < .tdd/reconcile-ledger.before | awk -F'\t' '$2 == "done" {print $4 "\t" $7}') <(git show HEAD:.tdd/issue-<n>.md | $S/ledger-steps.sh | awk -F'\t' '$2 == "done" {print $4 "\t" $7}')
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
- `ci-timeout` — a readied PR's check was still pending when the Draft PR step's bounded CI
  wait ran out → **system** failure (CI never answered, not the methodology).
- `ci-conflict` — a readied PR still conflicted with its base branch after the CI step's one
  rebase, so no workflow could start → **system** failure (CI could not answer, not the
  methodology).
- `ci-red` — a readied PR's CI check failed again after a CI repair step → **process**
  failure (CI answered, and the repair did not fix what it said).
- `suite-red` — the Draft PR step's full run was red again after a `⟦suite-repair⟧` step →
  **process** failure (the suite answered, and the repair did not fix what it said).
- `rebased-tip-red` — the Draft PR step's full run was red on the tip `rebase-onto-default.sh`
  rebased → **process** failure (the suite answered on the rebased tip).

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
   $S/preserve-attempt.sh <n> "$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" <phase> <attempt> bail
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
   ad-hoc; an unknown token makes it exit non-zero — pick the right token. Then mark the stop
   in the log — the mark sub-step 6's `### ⛔ Bailed` comment mirrors — with the cause token
   and that classification, before anything renders it:
   ```
   VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" VERI_PHASE=<phase> $S/event.sh bail cause=<cause> classification="$classification"
   ```
4. **Render and commit the metrics**, from inside the worktree and before the push, so the
   branch carrying the progress carries the account of it too: `$S/metrics.sh <n> >
   .tdd/issue-<n>-metrics.md; metrics=$?`, then `if [ "$metrics" = 0 ]; then git add
   .tdd/issue-<n>-metrics.md && git commit -m "metrics: what bailing on #<n> cost (#<n>)";
   fi`. This is the ending the report is worth most at — every attempt a bailed step spent is waste, and only the file says how much.
5. **Push the branch** so completed steps, that metrics commit and the leaf logs are
   recoverable, from inside the worktree (where you already are):
   `git push -u origin tdd/<n>-<slug>` (best-effort; note if it fails).
6. Post a `### ⛔ Bailed — <phase> (<classification> failure)` comment that names the phase,
   carries the `### 📊 Metrics` block just committed (or, when `$metrics` is not 0, the line
   `metrics could not be rendered: metrics.sh exited $metrics` in its place), carries the last reason
   (`.tdd/verify-<phase>.reason` on a `revise-exhausted` bail, the develop-red leaf's `WHY:`
   line on an `untestable-criterion` bail, the kill cause otherwise; a `ci-red` bail's reason
   names each CI check that failed, the `failed=` field its bail mark read from the head's
   check runs),
   then, after the reason, the skill-drift block — the stdout of `drift="$($S/skill-drift.sh)";
   drift_exit=$?`, or, when `$drift_exit` is not 0, the line `Skill drift: unavailable —
   skill-drift.sh exited $drift_exit` in its place, and the bail goes on either way —
   and points at the progress log (`.tdd/<phase>.log` or
   `.tdd/revise-<phase>-*.log`) for forensics.
7. **Leave the draft PR open, and put the bail diagnostic on it.** Step 2.3 opened it at the
   plan commit, and it is the run's claim on this issue: `solvable-issues.sh` leaves out an
   issue an open PR says `Closes #<n>` for, so taking it down would hand the issue back to
   the pool for the next machine to re-take and re-bail, and would discard the visible record
   a bail exists to leave. A bail also means a human has to look, and the draft PR is where
   they look — so the comment sub-step 6 posted to the issue thread reaches the PR too, or the
   page a reader opens still says a run is in progress when it stopped:
   ```
   gh api 'repos/{owner}/{repo}/pulls?head={owner}:{branch}' -q '.[0].html_url // empty'   # → <pr-url>, the PR step 2.3 opened; <pr-number> is its last path segment
   gh api repos/{owner}/{repo}/issues/<pr-number>/comments -f body="<the same ### ⛔ Bailed — <phase> (<classification> failure) comment, or a link to the issue comment sub-step 6 posted>"
   ```
   Either way the PR carries sub-step 6's skill-drift block: a link-only comment quotes that
   block alongside the link.
   It stays a **draft**: nobody is asked to review a run that stopped. The ledger's completed
   steps stay checked, so a re-run resumes from the failing step (see *Resume*) and edits this
   same PR rather than opening another.
8. Report to the user: the phase, the **classification** (system vs process), the reason,
   sub-step 6's skill-drift block, the branch name, and the **worktree path** — the logs named above are inside it, and it
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
   VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" $S/event.sh stop mode=<mode> at=<at>
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

On re-run, preflight step 3 calls `issue-worktree.sh` again; because it is **idempotent** it
prints the same `.tdd/wt/<n>` path and creates nothing, so the `cd` puts you back in the very
worktree the previous run committed in — the branch is already checked out there, nothing is
re-created or switched, and a resumed run's baseline runs on the branch head there, before
any cycle of the resumed run starts. The **resume check** then finds an existing
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
   `VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" $S/event.sh resume` — then
   **reuse the claim the previous run left on the branch**, which every tick of the cycle
   loop edits and step 4 rewrites:
   ```
   gh api 'repos/{owner}/{repo}/pulls?head={owner}:{branch}' -q '.[0].html_url // empty'   # → <pr-url>, the PR step 2.3 opened; <pr-number> is its last path segment
   ```
   A resumed run skips step 2 outright, so this is where the url comes from: it is read off
   the branch, never remembered. It edits that PR and opens **no second one** — a second
   PR-creating `gh api` call against a branch that already has an open PR is either a refusal that ends
   the resume where it started, or two pages claiming one issue, which is the failure #195
   exists to prevent. Only when this prints nothing is there **no open PR** to reuse: the
   previous run was killed inside step 2.3's own window, between the plan commit and the
   PR-creating `gh api` call that follows it. Then, and only then, run that sub-step's push and
   PR-creating `gh api` call here — opening the first PR a branch has ever had is not opening a second.
   Then run the cycle loop as normal. Go to the **draft PR** only when
   `next-pending-refactor.sh` and `next-unchecked.sh` have **both** exited 3: every step is
   checked, and every checked step's refactor is verified. An unchecked `⟦full-suite⟧` or
   `⟦human-owed⟧` line does not hold the run back from its draft PR — no cycle ticks either,
   and `next-unchecked.sh` skips both.

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
that is what `--issue` puts in front of the rest. That is the per-issue escape hatch. One
exception (#1225): for `--tier all`, a line equal to the command the fast tier resolves to
is dropped, and the full tier falls through to CLAUDE.md's `veri: all tests:` line and then
the usual detection, so an issue naming the fast tier never stops the full suite running.

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
- **Signal only processes you started**, by the pid you recorded when you started them —
  never by name or pattern (`pkill`, `killall`, `kill $(pgrep …)`), which matches every
  process on the machine whose command line fits, another live run's supervisor included.
  An experiment's processes and leaf names carry the `exp-` prefix, which no live run uses.
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
  `detect-test-command.sh --tier all`'s command, run through `detach-command.sh` at the Draft PR step — the
  branch's own full run, again after each `⟦suite-repair⟧` step a red result adds, and one
  more on the rebased tip when sub-step 1 rebased the branch.
- The PR is opened as a **draft** at the plan commit and readied for review at the Draft PR
  step, always carries `Closes #<n>`, and is **never merged** by you.
- On a `REJECT`, run the **bounded revise loop** (default 2 attempts, fresh leaf carrying
  the reason); if it exhausts, **bail** (process failure). On a **killed-stuck** leaf past
  its retry budget, or an unreadable verdict, **bail** (system failure). Always preserve
  commits and classify the cause. Never hand-fix the code yourself or loop past the budget.
