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

- `$S/supervise.sh <name> <cmd> [args...]` — **the leaf launcher.** Spawns `<cmd>` under a
  heartbeat + hard-timeout watchdog, owns the `.tdd/<name>.log` progress log, and returns
  the captured output on stdout. **Exit 0 = success, 1 = leaf-failure, 2 = killed-stuck**
  (hung past the heartbeat window or over the hard timeout, **after** its stuck-retry
  budget). A one-line status goes to stderr. Tunables: `VERI_HEARTBEAT` (silence window s,
  default 180), `VERI_TIMEOUT` (hard cap s, default 900), `VERI_STUCK_RETRIES` (extra
  attempts after a killed-stuck, default 1 — the **liveness** axis, independent of both the
  conductor's verdict-axis `REVISE_BUDGET` and its cost-axis `VERI_REFACTOR_BUDGET`).
  Because leaves **stream** (below), the default
  `VERI_HEARTBEAT` is a real silence window — a working leaf keeps it fresh, a genuinely
  hung one trips it — so just use the defaults; no need to pin heartbeat to the timeout.
  **Every leaf is launched through this — never call `run-leaf.sh` or `claude` directly.**
  It records its own final code in the completion file `.tdd/<name>.exit` on **every** path,
  killed-stuck included — that is what makes a detached launch waitable. And because a
  killed-stuck leaf is relaunched (`VERI_STUCK_RETRIES`), one call can take **more than one**
  `VERI_TIMEOUT` of wall time, which is why the wait below loops rather than naming one long
  timeout.
- `$S/wait-leaf.sh <name> [max-seconds]` — **the foreground half of a detached launch.**
  Blocks polling for that completion file and exits with the code recorded in it as soon as
  it lands (0 / 1 / 2, the launcher's own contract), or **exit 3** — nothing to report yet —
  once `max-seconds` pass with no completion file. The default is 540 s, comfortably inside
  Claude Code's 10-minute cap on a single foreground Bash call. On a **3, call it again**:
  the leaf is still running. A 3 with no leaf running means no result was ever recorded —
  never success.
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
- `$S/build-verify-prompt.sh <red|green|refactor|pin> <spec-file> <test-path> [target]` —
  assemble the blind verifier prompt. Used by `verify.sh`; you rarely call it directly.
- `$S/verify.sh <red|green|refactor|pin> <spec-file> <test-path> [target]` — the **verify
  verb**: build the blind prompt → launch the verifier leaf **through the supervisor** →
  parse the verdict. Prints the verifier's **reason** on stdout; **exit 0 = PASS, 1 =
  REJECT, 2 = malformed or killed-stuck**. The `pin` phase is the *already satisfied*
  check: the verifier confirms the test passes now, **fails** under a behaviour-removing
  mutation it applies and then reverts itself, and is behaviour-level — the same trivial
  / over-coupled / too-complex bar as `red`.
- `$S/parse-verdict.sh` — extracts `PASS|REJECT` + reason from a leaf's output (used by
  `verify.sh`).
- `$S/tick-criterion.sh '<substring>'` — the pure text transform both tick wrappers
  delegate to: reads a checkbox body on stdin, flips the first unchecked `- [ ]` matching
  the substring, writes it back on stdout. **Exit 3** if nothing matched.
- `$S/tick-issue-criterion.sh <n> '<substring>'` — tick a criterion checkbox in the
  issue body (the human-facing mirror).
- `$S/next-unchecked.sh < .tdd/issue-<n>.md` — print the **first unchecked ledger step**'s
  description; **exit 3** when none remain (the loop-done / nothing-to-resume signal).
- `$S/tick-ledger.sh [--refactor-pending] .tdd/issue-<n>.md '<substring>'` — check a step off
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
- `$S/clear-refactor-pending.sh .tdd/issue-<n>.md '<substring>'` — the counterpart of
  `tick-ledger.sh --refactor-pending`: **strip the ` ⟂ refactor pending` mark** from the first
  ticked step matching the substring, in place, once that step's refactor has been verified.
  Nothing on stdout. **Exit 0** when it cleared the mark; **exit 3** when no ticked step both
  matched and carried it — the file is left byte-identical, because nothing is written unless
  the transform found its line.
- `$S/classify-bail.sh <cause>` — deterministically classify a bail cause
  (`killed-stuck`/`no-verdict` → `system`, `revise-exhausted` → `process`; unknown → exit
  non-zero). Used in the *Bailing* step so the classification is consistent, not ad-hoc.
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
  Creates (or hands back) `<repo-root>/.tdd/wt/<n>` on branch `tdd/<n>-<slug>`, cut from the
  **default** branch (`origin/HEAD`, else a local `main`/`master`) and never from the
  caller's `HEAD`, and prints the worktree's **absolute path on stdout** — the only thing on
  stdout; git's chatter goes to stderr, so the path is safe to capture. **Idempotent**: a
  second call for the same issue prints the same path and creates nothing, which is what
  makes a resume land in the worktree the first run made. **Exit 0** = the path. **Exit 2** =
  no answer could be obtained — either the branch is **already checked out in another
  worktree** (it names that path and touches nothing: **never steal a checkout**, another
  conductor owns that run) or the default branch cannot be named. `$S/issue-worktree.sh
  --remove <n>` removes the worktree once the PR has landed, and **refuses** (exit 2) one
  holding uncommitted changes.
- `$S/detect-test-command.sh [--issue <body-file>] [repo-root]` — print the one command that
  runs the **target repo's** full suite on stdout; **exit 3** — the repo-wide *nothing to do*
  code — when no marker it trusts matched, which is your cue to ask the user. First match
  wins: the issue body's own `Test command:` line, then the repo's `.veri/test-command`,
  then every inference (see *Detecting the test command*).
- `$S/solvable-issues.sh [--repo <owner/name>]` — the **selection layer**: prints the
  numbers of the issues veri may take right now — open, labelled `ready-for-agent`, every
  issue under their `## Blocked by` heading closed, and not already claimed by an open PR
  saying `Closes #<n>` — one per line, ascending. **Exit 0** when it printed at least one,
  **exit 3** with empty stdout when none is takeable (nothing to do, not an error).
  `VERI_GH_JSON=<dir>` reads `issues.json` / `prs.json` fixtures instead of shelling out to
  `gh`, which is what makes it testable with no network. The conductor does not call this —
  it is rung 2's, driven by the loop branch of this skill.

## Launching a leaf — detach, then wait in the foreground

Every leaf launch below has the same three-part shape — clear the completion file, launch
detached, wait in the foreground — and each phase spells it out in full. A **developer
leaf** (red, green, refactor, revise) is launched straight through the supervisor:

```
rm -f .tdd/<name>.exit
nohup $S/supervise.sh <name> <cmd> [args...] > .tdd/<name>.out 2> .tdd/<name>.err &
$S/wait-leaf.sh <name>
```

The `rm -f` first, because the completion file is named for the **phase**, not the cycle: a
`.tdd/develop-red.exit` left by the previous step's red leaf would end the next wait
instantly, with the previous cycle's code. Then the launch, **detached** — `nohup` and a
trailing `&`, so the call returns at once. Then `wait-leaf.sh` in the **foreground**, which
blocks until the leaf finishes and exits with its code. On **exit 3** the leaf is still
running and you have only spent the wait's budget: **call `wait-leaf.sh` again**, as many
times as it takes. Only a 0, 1 or 2 is an answer. Read the leaf's report from
`.tdd/<name>.out` — the captured stdout — instead of from the launcher's stdout, which the
detached call no longer hands you.

A **verifier** (`verify.sh`, which goes through the supervisor too) takes the same shape
with one wrinkle: the code that matters is the verifier's **verdict**, not the supervisor's
status, so the detached shell records that verdict in a completion file of its own —

```
rm -f .tdd/verdict-<phase>.exit
nohup bash -c "$S/verify.sh <phase> … > .tdd/verify-<phase>.reason 2> .tdd/verify-<phase>.err; echo \$? > .tdd/verdict-<phase>.exit" > /dev/null 2>&1 &
$S/wait-leaf.sh verdict-<phase>
```

— named `verdict-<phase>`, never `verify-<phase>`, which the verifier leaf's own supervisor
already owns. `wait-leaf.sh` then returns **the verdict**: 0 PASS, 1 REJECT, 2 malformed or
killed-stuck. The reason is read back from `.tdd/verify-<phase>.reason`, the file the revise
step takes as a path.

**Never launch a leaf in a background Bash call and then wait for its notification.** The
conductor often runs as a print-mode session (`claude -p "/tdd <n>"` — the only way
to run it unattended), and in print mode that notification never arrives: the turn ends, the
`claude -p` process exits, and the leaf is orphaned. The supervisor keeps running it under
`.tdd/`, but nothing will ever read its result, tick the ledger or narrate the outcome (this
is how #70 was lost). The detach-then-wait shape behaves identically interactively and
unattended, so it is the only one this procedure uses.

## Inputs

There is one command, so what the user typed after it is what decides which of the two
procedures below runs. No shape of argument is ever a question to put back to the user: a
word that is not a number is never a malformed issue number, and an empty argument is never
a missing one. Read the first word of `$ARGUMENTS` and resolve it three ways — there is no
fourth case:

- **An integer** — it is an issue **number** `<n>`, and this invocation is the
  single-issue procedure: run *Procedure* below on that issue, end to end.
- **Any other word** — it is a **scope** to drain: run *Draining a scope — the loop*
  below, which selects the issues in that scope and runs the single-issue procedure over
  them one at a time.
- **No argument at all** — a bare invocation is the scope `plain`, so it takes the scope
  branch above with `plain` as its scope.

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
3. **Suite is green at baseline — and time it.** The issue may name its own test command,
   so read its body first — into a temp file, since the caller's checkout must stay clean:
   ```
   body="$(mktemp)" && gh issue view <n> --json body -q .body > "$body"
   ```
   Then get the test command from `$S/detect-test-command.sh --issue "$body"` (see
   *Detecting the test command*) and run it. If already red, stop and report — a cycle must
   not start on a red baseline. Reading the body **here**, before the baseline runs, is what
   keeps the baseline and every later leaf on one command: detected after the baseline, the
   issue's line would arrive too late to be the command the baseline proved green. Note how
   long the run took and keep it as `baseline`, the elapsed wall time in whole seconds
   (round up); step 6 sizes the run's hard timeout from it. This measurement is free — the
   run happens anyway — and it is the only one taken, so a suite that gets slower mid-run
   does not move the timeout under a leaf.
4. **Default branch.** Capture it for the PR base:
   `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`.
5. **Tunables parse.** Run `$S/refactor-budget.sh 0` once. **Exit 2** means
   `VERI_REFACTOR_BUDGET` is not a whole number ≥ 0 — stop and report its stderr diagnostic
   verbatim. A budget that cannot be read is a poisoned baseline like a red suite, not a
   decision, and catching it here is what lets the refactor loop treat exit 2 as impossible.
   Exit 0 and exit 3 both mean it parses (3 only says the budget is 0 — a run with the
   refactor loop switched off), so continue.
6. **Size the run's hard timeout from the baseline.** Hand step 3's `baseline` to
   `$S/leaf-timeout.sh` and **export** the result, so every leaf of the run is launched
   under it rather than under the supervisor's fixed 900 s default:
   ```
   timeout="$($S/leaf-timeout.sh "$baseline")" && export VERI_TIMEOUT="$timeout"
   ```
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
   **Every later step of the run happens inside that worktree**: the blind spec
   (`.tdd/issue-<n>-spec.md`), the ledger (`.tdd/issue-<n>.md`), every leaf log and prompt,
   every commit, the push and the PR. All the `.tdd/…` paths below are **relative to the
   worktree**, so once you have `cd`'d there they read exactly as written — do not prefix
   them with the caller's path.
   The **caller's checkout is left exactly as it was**, still on whatever branch it was on:
   it is never switched and never committed in. That is the point — a skill symlinked out of
   it or a dev server serving it must not silently start seeing the issue branch (ADR-0013).
   **Exit 2 is a preflight-class stop**: either the branch is already checked out in another
   worktree (another conductor owns that run — never steal it) or the default branch cannot
   be named. Report the script's diagnostic verbatim and **do not start** — no branch of your
   own, no cycle, nothing to revert.
3. **Write the behavior spec to a file** the verifier leaves will read — inside the worktree,
   which you are now in:
   `mkdir -p .tdd && gh issue view <n> --json body -q .body > .tdd/issue-<n>-spec.md`.
   (The verifier is blind; this on-disk spec — never your narration — is what it sees.)
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

   - [ ] <step 1: a behaviour-level criterion, one cycle's worth>
   - [ ] <step 2: …>
   ```
   Each step's text should be a distinctive, behaviour-level description — it doubles as the
   substring you will pass to `tick-ledger.sh`. Prefer the issue's own acceptance-criteria
   wording where it maps cleanly to one cycle.
2. **Commit the ledger** as the run's starting point:
   `git add .tdd/issue-<n>.md && git commit -m "plan: scope #<n> into <k> steps (#<n>)"`.
   (The ledger is committed — step 1.4 guaranteed `.gitignore` tracks `.tdd/issue-*.md`
   while ignoring leaf logs.)
3. **Mirror the plan** to the issue thread: post a `### 🗺️ Plan` comment listing the steps,
   naming the test command preflight detected and every leaf will run, and noting that the
   ledger is the source of truth and each step will be blind-verified. The test command is
   in that comment so a wrong one is visible on the thread before the first leaf starts,
   rather than after a cycle has paid for it. The comment also states the hard timeout
   preflight step 6 settled on and where it came from — `timeout 1200 s (6 × a 200 s
   baseline)`, or `timeout 900 s (floor; 5 s baseline)`, or `timeout 900 s (VERI_TIMEOUT set
   by hand)` — so a reader of the thread can see which number every leaf of this run is
   under and why. On #71 that had to be reconstructed from the timestamps of two bails.

### 2b. Start comment

Post a short comment announcing veri has started, naming the branch (and the worktree it is
running in) and the number of plan steps, and noting each phase will be blind-verified:
`gh issue comment <n> --body "..."`.

### 3. The cycle loop

Loop until the ledger has no unchecked step. Each iteration runs **one full cycle** (Red →
Green → Refactor) for the next step; let **STEP** be that step's description:

```
$S/next-unchecked.sh < .tdd/issue-<n>.md        # exit 3 ⇒ all steps done → go to step 4 (PR)
VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP='<STEP>' $S/event.sh step-start
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

#### Red — one failing test (developer leaf), then verify-red (blind)

1. **Develop.** Build the prompt from the `red` template — it already instructs the leaf to
   write **exactly one** failing test pinning the criterion to **observable external
   behavior**, with **no production code**, and to run **the suite holding that case**, not
   the full suite, against the unmodified code, since the only question Red asks is whether
   that one case fails — and launch the leaf **through the supervisor**:
   ```
   $S/build-develop-prompt.sh red .tdd/issue-<n>-spec.md '<STEP>' '<test-cmd>' > .tdd/develop-red.prompt
   rm -f .tdd/develop-red.exit
   nohup $S/supervise.sh develop-red $S/run-leaf.sh .tdd/develop-red.prompt --permission-mode bypassPermissions > .tdd/develop-red.out 2> .tdd/develop-red.err &
   $S/wait-leaf.sh develop-red     # foreground; on exit 3 call it again
   ```
   You supply only those variables; the instructions are the template's, identical every
   run. The leaf's report is in `.tdd/develop-red.out`, and ends with the lines you branch on — `TEST_PATH:`, `TARGET_TEST:`,
   `AGAINST_UNMODIFIED: FAILS | PASSES`, `FAIL_OUTPUT:` — so take the **test path** and
   **target test id** from the first two and read the third for the next sub-step.
   `AGAINST_UNMODIFIED` exists because a criterion earlier work already satisfies cannot
   yield a failing test, and that fact has to reach you as data: in #30's step 3 it did not,
   and a faithful test spent two verify-red `REJECT`s and two revise leaves reporting
   IMPOSSIBLE before the run bailed and the revert discarded it.
   If the wait exits **2 (killed-stuck)**, the leaf hung or ran away — **bail**
   cleanly (see *Bailing*); do not retry.
2. **Verify (blind).** Branch on the leaf's `AGAINST_UNMODIFIED` line. On **`FAILS`**, run
   the red verifier against the on-disk test and spec, **redirecting its stdout (the
   reason) to a file** — the revise step takes the reason as a *path*, not as text you
   retype:
   ```
   rm -f .tdd/verdict-red.exit
   nohup bash -c "$S/verify.sh red .tdd/issue-<n>-spec.md <test-path> <target-test-id> > .tdd/verify-red.reason 2> .tdd/verify-red.err; echo \$? > .tdd/verdict-red.exit" > /dev/null 2>&1 &
   $S/wait-leaf.sh verdict-red     # foreground; on exit 3 call it again
   ```
   That is the verifier shape from *Launching a leaf*: the wait returns the **verdict** —
   0 PASS, 1 REJECT, 2 malformed or killed-stuck — not the supervisor's status.
   On **`PASSES`** the criterion is **already satisfied** — never send that test to
   verify-red, whose verdict on a passing test can only be `REJECT`. Run the pin check
   instead and continue at *Already satisfied — the pin*:
   ```
   rm -f .tdd/verdict-pin.exit
   nohup bash -c "$S/verify.sh pin .tdd/issue-<n>-spec.md <test-path> <target-test-id> > .tdd/verify-pin.reason 2> .tdd/verify-pin.err; echo \$? > .tdd/verdict-pin.exit" > /dev/null 2>&1 &
   $S/wait-leaf.sh verdict-pin     # foreground; on exit 3 call it again
   ```
   Either way, note the **wait's exit code** — the verdict — and read the reason back out of
   `.tdd/verify-<phase>.reason` to narrate it. The file is named for the **verifier** that
   wrote it (`red`, `pin`, `green`, `refactor`), and each verification of that phase
   overwrites it — the newest objection is the only one a revise leaf should answer.
3. **Narrate + branch (the `FAILS` path).** Post a `### 🔴 Red` comment with the test and
   the failing output, followed by a `### 🔎 verify-red — PASS|REJECT` comment carrying the
   verifier's reason.
   - **PASS (exit 0):** continue to Green.
   - **REJECT (exit 1):** enter the **revise loop** — see *Revising on a REJECT*. It
     returns either PASS (continue to Green) or budget-exhausted (**bail**, process failure).
   - **Malformed / killed-stuck (exit 2):** the verdict could not be obtained (unparseable
     or the verifier leaf was killed) — **bail** as a system failure (see *Bailing*), not a
     clean process stop.

#### Green — minimum implementation (developer leaf), then verify-green (blind)

1. **Develop.** Build the prompt from the `green` template — the **minimum** production
   code, no generality the test does not demand, the **test itself untouched**, full suite
   green — and launch **through the supervisor** (exit **2** → **bail**):
   ```
   $S/build-develop-prompt.sh green .tdd/issue-<n>-spec.md '<STEP>' '<test-cmd>' <test-path> '<target-test-id>' > .tdd/develop-green.prompt
   rm -f .tdd/develop-green.exit
   nohup $S/supervise.sh develop-green $S/run-leaf.sh .tdd/develop-green.prompt --permission-mode bypassPermissions > .tdd/develop-green.out 2> .tdd/develop-green.err &
   $S/wait-leaf.sh develop-green    # foreground; on exit 3 call it again
   ```
   The test path and target test id are the ones Red's report gave you. The leaf's report is
   in `.tdd/develop-green.out`, and ends with `IMPL_PATH:` (the production files it created
   or changed) and `SUITE: GREEN | RED` plus the suite's final summary line; both go into the
   narration below.
2. **Verify (blind)** — the verifier shape again, and the wait's code is again the verdict:
   ```
   rm -f .tdd/verdict-green.exit
   nohup bash -c "$S/verify.sh green .tdd/issue-<n>-spec.md <test-path> <target-test-id> > .tdd/verify-green.reason 2> .tdd/verify-green.err; echo \$? > .tdd/verdict-green.exit" > /dev/null 2>&1 &
   $S/wait-leaf.sh verdict-green    # foreground; on exit 3 call it again
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
     $S/tick-ledger.sh --refactor-pending .tdd/issue-<n>.md '<distinctive substring of STEP>'
     git add -A && git commit -m "feat: <STEP summary> (#<n>)"
     ```
     Continue to the Refactor loop.
   - **REJECT (exit 1):** enter the **revise loop** — see *Revising on a REJECT*. On a
     recovered PASS, do the same atomic tick-and-commit and continue; on budget-exhausted,
     **bail**.
   - **Malformed / killed-stuck (exit 2):** **bail** — see *Bailing*.

#### Refactor loop — behavior-preserving transforms until none, then verify-refactor (blind, once)

1. **Loop the transforms.** Repeatedly launch a developer leaf that applies **one**
   behavior-preserving transformation (naming, duplication, clarity) and runs the **suites
   covering the files it touched**, keeping them green. **Ask the budget before each leaf**: `<count>` is how many
   transforms this step has applied so far — start at **0**, and count only leaves that
   reported `RESULT: applied …`, never one that reported `nothing left to tidy`. Build each
   prompt from the `refactor` template and launch **through the supervisor** (exit **2** →
   **bail**):
   ```
   $S/refactor-budget.sh <count>   # exit 0 ⇒ launch the leaf below; exit 3 ⇒ stop, go to 2
   touched="$(git diff --name-only HEAD~1 HEAD | paste -sd, -)"
   $S/build-develop-prompt.sh refactor .tdd/issue-<n>-spec.md '<STEP>' '<test-cmd>' "$touched" > .tdd/develop-refactor.prompt
   rm -f .tdd/develop-refactor.exit
   nohup $S/supervise.sh develop-refactor $S/run-leaf.sh .tdd/develop-refactor.prompt --permission-mode bypassPermissions > .tdd/develop-refactor.out 2> .tdd/develop-refactor.err &
   $S/wait-leaf.sh develop-refactor   # foreground; on exit 3 call it again
   ```
   The `rm -f` matters most here: every iteration of this loop reuses the name
   `develop-refactor`, so a completion file left by the previous transform would end the
   next wait before the next leaf had done anything.
   `<touched-files>` is the **bounds of the tidy-up**: the files this cycle produced, as one
   comma-separated line. Compute it **once**, right after the step's atomic green commit —
   `git diff --name-only HEAD~1 HEAD` is exactly that commit's files at that moment — adding
   anything still uncommitted (`git diff --name-only HEAD`) if an earlier iteration left
   work on disk. Reuse the same list for every iteration: a transform's own commit moves
   `HEAD`, but it does not widen what this cycle is allowed to touch.
   The template owns the rules — one transform per leaf so a break is attributable, revert
   rather than leave a red suite, **no untested generality** (it comes only from
   **triangulation**), and code that is **overfit** (e.g. hard-codes the one tested case)
   **flagged as needing a triangulating test**, never hand-generalized. Each leaf's report
   ends with `RESULT:` (`applied <transform>, suite green` or `nothing left to tidy`),
   `FLAGS:` (overfit code and the case that would force the generality, or `none`) and one
   `CANDIDATES:` line per transform it still sees left in those files (or `none`). The loop
   has **two** stop conditions, and either ends it: a leaf reports **nothing left to tidy**,
   or `refactor-budget.sh` exits **3** (the budget is spent). Carry the flags of every leaf
   into the narration, then go to sub-step 2. Exit **2 cannot occur here** — preflight ran
   the script once, so a `VERI_REFACTOR_BUDGET` that does not parse stopped the run before
   any branch existed. The budget exists because a refactor leaf asked for one transform
   almost always finds one, each smaller than the last: without it the conductor ends the
   loop by judgement, which is the ad-hoc decision veri exists to remove. The leaf leaves its
   transform **uncommitted**; you commit it, and only if it changed something:
   `git add -A && git commit -m "refactor: <what> (#<n>)"`.
2. **Verify (blind, once) on the settled result.**
   ```
   rm -f .tdd/verdict-refactor.exit
   nohup bash -c "$S/verify.sh refactor .tdd/issue-<n>-spec.md <test-path> > .tdd/verify-refactor.reason 2> .tdd/verify-refactor.err; echo \$? > .tdd/verdict-refactor.exit" > /dev/null 2>&1 &
   $S/wait-leaf.sh verdict-refactor  # foreground; on exit 3 call it again
   ```
   — one verdict on the final state (**full suite** still green, code up to standard, no
   smuggled generality). This is where the full suite runs in this phase: the transform
   leaves ran only the suites covering their files, so a break in a suite none of them
   touched surfaces here, as a REJECT the revise loop answers rather than a revert inside
   the loop.
3. **Narrate + branch.** Post `### 🛠️ Refactor` (the transforms applied, or "no refactor
   warranted", plus any triangulation flagged) and `### 🔎 verify-refactor — PASS|REJECT`.
   Say **how many transforms ran** and **which stop condition ended the loop**, mirroring
   `refactor-budget.sh`'s own status line (`refactor 2/2 — budget spent`): a step that ran
   dry says **nothing left to tidy**, and a step the budget stopped says **how many
   candidates** the last leaf left and **lists** them, one per line, taken verbatim from its
   `CANDIDATES:` lines — a count with no items is not a backlog, and the backlog is the
   whole point of recording what the budget dropped.
   - **PASS:** the step's cycle is complete — the step is tidied, not merely green, so
     **clear the refactor-pending mark and commit the cleared ledger first**, before
     anything outside the repository says the step is done:
     ```
     $S/clear-refactor-pending.sh .tdd/issue-<n>.md '<distinctive substring of STEP>'
     git add -A && git commit -m "chore: refactor verified for <STEP summary> (#<n>)"
     ```
     A clear left uncommitted is not a clear: resume reads the **committed** ledger, so
     until that commit exists the step still says pending. Then **mirror to the issue**:
     post a `### ✅ Step done` comment, and tick the matching acceptance criterion in the
     **issue body** (`$S/tick-issue-criterion.sh <n> '<substring>'`, the human mirror). Mark
     the same moment in the log —
     `VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP='<STEP>' $S/event.sh step-done` — then
     loop back to the top of **step 3** for the next unchecked ledger step.
   - **REJECT (exit 1):** enter the **revise loop**; on recovered PASS, mirror and loop; on
     budget-exhausted, **bail**. (Earlier steps' commits are preserved.)
   - **Malformed / killed-stuck (exit 2):** **bail**. (Earlier steps' commits are preserved.)

### 4. Draft PR

Reached when `next-unchecked.sh` exits 3 — every ledger step is checked off. The full suite
must be green before this step; that nothing is left uncommitted and no step is still only
green is not taken on trust here — sub-step 1 asks. Like every step since 1.2, this one runs
**from inside the worktree** — every command below is issued there, so each sees the issue
branch and its commits without any switching.

1. **Ask the two questions that decide whether there is anything fit to push, and refuse to
   go on while either says no** — both from inside the worktree, before the branch leaves
   it:
   ```
   git status --porcelain
   $S/next-pending-refactor.sh < .tdd/issue-<n>.md
   ```
   A non-empty `git status --porcelain` is work no verifier has seen — the transform a
   killed refactor leaf left on disk — and an exit 0 from `next-pending-refactor.sh` is a
   step that is checked but still only green. On either, **do not push and do not open the
   PR**: for a pending step go to *Resume* sub-step 2, which resets the stray work and
   re-enters that step's refactor loop, and come back here only once both questions have
   gone quiet — an empty status, and `next-pending-refactor.sh` exiting 3.
2. Push the branch, from the worktree: `git push -u origin tdd/<n>-<slug>`.
3. Open a **draft** PR linked to the issue; the body must contain `Closes #<n>`:
   ```
   gh pr create --draft --base <default-branch> \
     --title "<type>: <criterion summary> (#<n>)" \
     --body "Closes #<n>

   <summary: the plan's steps, each a blind-verified R→G→R cycle, ledger committed>"
   ```
4. **Never merge the PR.** Landing the code is always the human's deliberate act.
5. Post a final `### ✅ Done — <pr-url>` comment, and close the run's log with the same URL:
   ```
   VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh done pr=<pr-url>
   ```

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
  $S/tick-ledger.sh .tdd/issue-<n>.md '<distinctive substring of STEP>'
  git add -A && git commit -m "test: pin <STEP summary> (#<n>)"
  ```
  Then **mirror**: post a `### 📌 Already satisfied — <STEP>` comment carrying the
  verifier's reason, tick the matching acceptance criterion in the **issue body**
  (`$S/tick-issue-criterion.sh <n> '<substring>'`), and mark it in the log —
  `VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP='<STEP>' VERI_PHASE=pin $S/event.sh pin`.
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
   VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP='<STEP>' VERI_PHASE=<phase> VERI_ATTEMPT=<k> $S/event.sh revise budget=<REVISE_BUDGET>
   ```
2. **Fresh developer leaf.** Build the revise prompt from the `revise` template, naming the
   phase being redone and the **reason file** the verifier's stdout went to, then launch
   **through the supervisor** (exit **2 → bail**, system failure):
   ```
   $S/build-develop-prompt.sh revise <phase> .tdd/issue-<n>-spec.md '<STEP>' '<test-cmd>' .tdd/verify-<phase>.reason > .tdd/revise-<phase>-<k>.prompt
   rm -f .tdd/revise-<phase>-<k>.exit
   nohup $S/supervise.sh revise-<phase>-<k> $S/run-leaf.sh .tdd/revise-<phase>-<k>.prompt --permission-mode bypassPermissions > .tdd/revise-<phase>-<k>.out 2> .tdd/revise-<phase>-<k>.err &
   $S/wait-leaf.sh revise-<phase>-<k>   # foreground; on exit 3 call it again
   ```
   The reason travels as a **file**, not as prose you paste in — that is why the verify step
   redirected it. The template tells the leaf it is fresh, that the reason is the whole of
   what it has to work from, that the work is on disk, and that it must answer *that
   objection only*. Its report ends with `OUTCOME: REWRITTEN | IMPOSSIBLE` and
   `AGAINST_UNMODIFIED: FAILS | PASSES | N/A` — `N/A` whenever the leaf touched no test,
   which is every revise of green or refactor. `IMPOSSIBLE` is a legitimate answer, not a
   crash: the leaf says the objection cannot be met as stated. It still spends attempt `k` —
   re-verify below and let the blind verdict, not the leaf's own account, decide.
3. **Re-verify (blind, same phase).**
   ```
   rm -f .tdd/verdict-<phase>.exit
   nohup bash -c "$S/verify.sh <phase> .tdd/issue-<n>-spec.md <test-path> [target] > .tdd/verify-<phase>.reason 2> .tdd/verify-<phase>.err; echo \$? > .tdd/verdict-<phase>.exit" > /dev/null 2>&1 &
   $S/wait-leaf.sh verdict-<phase>      # foreground; on exit 3 call it again
   ```
   — overwriting the reason file, so attempt `k+1` carries the newest objection. Both `rm
   -f`s matter in this loop: every attempt re-verifies the **same** phase, so the previous
   attempt's completion files would otherwise be read as this one's answer.
   - **PASS (exit 0):** the step is recovered. Post `### 🔎 verify-<phase> (revised) — PASS`
     with the reason, and resume the cycle from where that phase's PASS would continue.
   - **REJECT (exit 1):** if attempts remain, loop; otherwise fall through to the bail below.
   - **Malformed / killed-stuck (exit 2):** **bail** (system failure).

If all `REVISE_BUDGET` attempts are still `REJECT`, **bail the step** as a **process
failure** (the methodology could not satisfy the blind verifier within budget), recording
the **last rejection reason**.

`REVISE_BUDGET` (verdict axis) is **independent** of the supervisor's `VERI_STUCK_RETRIES`
(liveness axis) and of `VERI_REFACTOR_BUDGET` (cost axis): the first governs a leaf that
finished with a bad verdict, the second a leaf that never produced one, the third how many
transforms one step's tidying is worth. A `REJECT` is veri working as designed — the blind verifier
refusing to rubber-stamp — so the bounded revise is a *correction*, never an excuse to keep
hammering past the budget.

## Bailing

A **bail** terminally stops this issue while preserving progress (ADR-0011). Each bail has
a **cause token** that maps to a classification via `$S/classify-bail.sh <cause>`:

- `killed-stuck` — `supervise.sh` exited **2** for a developer leaf even after its
  stuck-retry budget → **system** failure (plumbing broke).
- `no-verdict` — `verify.sh` exited **2** (unparseable verdict, or the verifier leaf was
  killed) → **system** failure.
- `revise-exhausted` — a step spent its `REVISE_BUDGET` and the blind verifier still says
  `REJECT` → **process** failure (methodology spoke).

To bail:

1. **Revert only the half-done step.** Completed steps are committed; the failing step's
   test/code is still uncommitted (the cycle bailed before its atomic green commit). Drop
   exactly that half-done work — `git reset --hard HEAD` — which leaves every completed
   step's commit (and the ledger's checked steps) intact.
2. **Classify deterministically.** `classification="$($S/classify-bail.sh <cause>)"`
   (`<cause>` is one of the tokens above). This keeps the label consistent rather than
   ad-hoc; an unknown token makes it exit non-zero — pick the right token.
3. **Push the branch** so completed steps and the leaf logs are recoverable, from inside the
   worktree (where you already are): `git push -u origin tdd/<n>-<slug>` (best-effort; note
   if it fails).
4. Post a `### ⛔ Bailed — <phase> (<classification> failure)` comment that names the phase,
   carries the last reason (`.tdd/verify-<phase>.reason` on a `revise-exhausted` bail, the
   kill cause otherwise), and points at the progress log (`.tdd/<phase>.log` or
   `.tdd/revise-<phase>-*.log`) for forensics. Mark the stop in the log too, with the cause
   token and the classification step 2 derived from it:
   ```
   VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP='<STEP>' VERI_PHASE=<phase> $S/event.sh bail cause=<cause> classification="$classification"
   ```
5. **Open no PR.** The ledger's completed steps stay checked, so a re-run resumes from the
   failing step (see *Resume*).
6. Report to the user: the phase, the **classification** (system vs process), the reason,
   the branch name, and the **worktree path** — the logs named above are inside it, and it
   is where a re-run will resume. Leave it in place; only a merged PR retires it.

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
2. **Ask for a pending refactor before anything else.**
   `$S/next-pending-refactor.sh < .tdd/issue-<n>.md` prints the first checked step whose
   refactor-pending mark is still there — a step the previous run left **green but not
   tidied**, because it was killed between that step's green commit and its
   verify-refactor. **Exit 3** means no step carries the mark: go to sub-step 3. Otherwise
   **STEP** is that description, and this step's refactor loop is re-entered where it
   stopped — starting by throwing away whatever the killed leaf left uncommitted, which no
   verifier has seen and which must never reach the PR:
   ```
   git reset --hard HEAD
   green="$(git log -1 --format=%H -- .tdd/issue-<n>.md)"
   touched="$(git diff --name-only "$green^" "$green" | paste -sd, -)"
   count="$(git log --format=%s "$green"..HEAD | grep -c '^refactor:')"
   ```
   `$green` is the step's **green commit** — the last commit that changed the ledger, since
   the tick is atomic with it and the clear that would follow never happened. So `$touched`
   is the same bounds the interrupted loop had, and `$count` the transforms it already
   committed, so the budget is not spent twice. Run the **Refactor loop** (the cycle loop's
   sub-section) with those two inputs, and its **verify-refactor** after it — the check the
   interruption skipped. Its PASS clears the mark and commits the cleared ledger exactly as
   in the cycle loop; then come back here and ask sub-step 2 again.
3. `next-unchecked.sh < .tdd/issue-<n>.md` gives the **first unchecked step** — the cycle
   loop continues from exactly there, so **STEP** is that step's description, bound here
   instead of at the top of the cycle loop. Already-checked steps (and their commits) are
   kept.
4. Post a `### ▶️ Resuming` comment naming that step, and mark the pick-up in the log —
   `VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP='<STEP>' $S/event.sh resume` — then run
   the cycle loop as normal. Go to the **draft PR** only when
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
- The full suite must be green before you commit and before you open the PR.
- The PR is always a **draft**, always carries `Closes #<n>`, and is **never merged** by
  you.
- On a `REJECT`, run the **bounded revise loop** (default 2 attempts, fresh leaf carrying
  the reason); if it exhausts, **bail** (process failure). On a **killed-stuck** leaf past
  its retry budget, or an unreadable verdict, **bail** (system failure). Always preserve
  commits and classify the cause. Never hand-fix the code yourself or loop past the budget.

## Draining a scope — the loop

Everything above drives **one** issue. A **scope** asks instead for a drain: the same
single-issue procedure, run repeatedly, wrapped in a loop whose only new job is
**selection** — deciding which issue is next and when to stop. This is rung 2 of the scope
ladder, and it lives here rather than in a second skill so the selection layer and the
scripts it calls are one thing; its steps are numbered `Loop 0`–`Loop 5` because they are
its own sequence, not the *Procedure* steps above.

Everything below the selection layer is unchanged, and **the loop adds no new failure mode
of its own**: every outcome of it is one of rung 1's outcomes (draft PR, or a bail
classified system or process), and the committed ledger makes any interrupted run resumable
by re-invoking the same command.

**You never merge anything.** Each solved issue ends on a draft PR for a human, exactly as
rung 1 leaves it.

### Loop inputs

- `$ARGUMENTS` may carry `--continue-on-bail` (or the user may say "keep going past
  bails") — see *Loop 4*. It may also carry `--repo <owner/name>` to select a repository
  other than the current one; pass it straight through to `solvable-issues.sh`.
- `VERI_MAX_ISSUES` — a cap on how many issues one invocation will attempt. Read it as
  `${VERI_MAX_ISSUES:-0}`; **0 means no cap**, which is the default, because the solvable
  set is finite and the `ready-for-agent` label is already the human's opt-in. Set it when
  you want a short, watchable run.
- **The scope's selection label**, derived from the scope's own word: the scope `plain`
  drains the bare `ready-for-agent` label — every issue opted in today carries that, so the
  bare invocation keeps draining them — and any other scope `<s>` drains
  `ready-for-agent:<s>`. That colon is the namespacing which lets **one label per loop** be
  the rule without anyone spelling a label: `/tdd docs` and `/tdd scripts` draw from
  disjoint pools instead of racing for the same issues. `solvable-issues.sh` knows nothing
  of scopes — it reads a label from the environment — so deriving it is yours: put the
  derived label in `VERI_LABEL` before *Loop 1* calls it.
- `VERI_LABEL` — an **override** of that derivation, so the label this loop drains is
  `${VERI_LABEL:-<the scope's label>}`. It is read by `solvable-issues.sh`, so pass it
  through the environment rather than as an argument. Set, it **moves** the gate, it does
  not widen it: the pool becomes exactly the issues carrying that name, whatever the scope
  derived — which is what a launcher needs when the pool it wants is one no scope word
  spells. Two loops given the *same* value still collide; that is the human's choice. Set
  but empty is refused with exit 2 rather than matching every issue.

### Loop 0. Preflight — none of its own

Do **not** duplicate the *Procedure*'s preflight. The first single-issue run performs it
(git repo, clean tree, `gh` and `claude` authenticated, suite green at baseline, default
branch captured), and a poisoned baseline makes that run refuse to start before any branch
or cycle exists. That refusal is a bail like any other, so it stops the loop here too —
with nothing done and nothing to revert.

### Loop 1. Select

```
$S/solvable-issues.sh [--repo <owner/name>]
```

It prints the numbers veri may take right now, one per line, ascending; **exit 0** when
there is at least one, **exit 3** with empty stdout when there is none.

- **Exit 3:** report `nothing solvable` and stop, **naming the label you drained** —
  `${VERI_LABEL:-<the scope's label>}`, as in `nothing solvable under ready-for-agent:docs`. A
  loop that says `no ready-for-agent issue` while it was launched on another label sends
  the reader to the wrong list. Not an error — no issue is open, carrying that label,
  unblocked and unclaimed. Nothing was started.
- **Exit 0:** take the **first** number. Do not keep the rest of the list.

### Loop 2. Solve one issue

Run the *Procedure* above for that number end to end — its preflight, branch, ledger, cycle
loop, bail semantics and draft PR, unchanged and un-second-guessed. You are the same agent;
the run happens wherever that procedure puts it, so do not relocate it or invent a branch of
your own.

Record its outcome: the **PR url**, or the **phase and classification** of its bail.

### Loop 3. Re-select, do not walk the list

After each run, go back to **Loop 1** and run `solvable-issues.sh` again. Never continue
down the list you printed last iteration — it is stale. The issue you just solved now has
an open PR saying `Closes #<n>`, which removes it from the set, and closing its
dependencies may have **unblocked others** that were not solvable a moment ago. The list
is recomputed every iteration; that is the whole of the loop's state.

### Loop 4. Stop conditions

Stop and report when any of these holds:

- **A bail.** The first bail — **system or process, either one** — stops the loop, unless
  the user passed `--continue-on-bail` or said to keep going past bails. In that case
  record the bail and continue at *Loop 1*; the bailed issue leaves a pushed branch and no
  PR, so it stays in the solvable set and would be retried immediately — **skip it** for
  the rest of this invocation rather than re-running it.
- **An empty list.** `solvable-issues.sh` exits 3 — the drain is complete.
- **The cap.** `${VERI_MAX_ISSUES:-0}` is non-zero and that many issues have been
  attempted. Say the cap stopped the loop and that re-invoking the same command continues.

### Loop 5. Report

One line per issue attempted, in the order attempted:

```
#<n> — <PR url> | bailed: <phase> (<system|process> failure) | skipped: <why>
```

Then one line naming **what stopped the loop**: the bail, the empty list, or the cap. If
a run was left mid-issue, say that re-invoking the same command resumes it from its
committed ledger — no step is repeated and none is skipped.

### Loop guardrails

- **The loop adds no new failure mode.** Every outcome is one of rung 1's. If you find
  yourself inventing a state this loop can be in, you are doing rung 1's job over again —
  don't.
- **Never merge, and never mark a draft PR ready.** A human lands the code.
- **Never hand-pick an issue** that `solvable-issues.sh` did not print, and never re-order
  the ones it did. The `ready-for-agent` label is the opt-in and `## Blocked by` is the
  ordering; neither is yours to override.
- **Recompute, never cache.** The stale-list bug is the one mistake available here.
- **Do not touch a bailed issue's branch.** It is pushed and diagnostic; the human reads
  it, or a later single-issue run resumes it from the ledger.
