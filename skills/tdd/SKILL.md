---
name: tdd
description: >-
  One GitHub issue under strict TDD: `/tdd <number>`. Normally launched by `/vdev`, not typed.
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
(process vs system; see `<base directory>/BAIL.md`).

## The two roles, and why the verifier is blind

- A **developer leaf** writes the failing test, the implementation, or the refactor. It
  is allowed to see everything: the issue, the repo, the prior phases.
- A **verifier leaf** confirms one developer claim. It is **blind**: it receives only the
  test, the issue's behavior spec, and the repo — never the developer's rationale — and
  it establishes ground truth by **running the test itself**. Blindness is enforced
  structurally: the verifier prompt is built by `build-verify-prompt.sh`, and no input it
  takes can carry the developer's rationale (the `refactor` phase's base sha, a hex commit
  name, is one such input that holds no prose, #151), so the developer's reasoning
  physically cannot reach it (see ADR-0003). No input may be added to `build-verify-prompt.sh`
  that could carry the developer's rationale.

You — the conductor — must keep these roles distinct. Do **not** write the test or the
implementation yourself, and do **not** pass a developer leaf's explanation into a
verification.

## The scripts (this skill's `scripts/` directory)

Let `S=<base directory>/scripts`, where *base directory* is the path the harness printed
when this skill loaded (`Base directory for this skill: …/tdd`). It is the same
skill whether it lives in the target repo's `.claude/skills/` or is symlinked into
`~/.claude/skills/` for use from any repo — never assume a repo-relative path. All leaf
machinery lives there and is unit-tested (`$S/tests/*.test.sh`).

`$S` is pinned: a run launched through `$S/run-conductor.sh` executes the skill snapshot —
the commit recorded in `.tdd/issue-<n>-skill-commit` and exported to every leaf as
`VERI_SKILL_COMMIT` — not the clone's current tip, so a PR landing on `main` while you work
does not change the scripts and templates under a running conductor (see *The skill
snapshot* in the repository's `README.md`, *Launching the conductor*). Every launch `supervise.sh` makes also writes the commit it ran under to
the event log (`.tdd/events.jsonl`, key `skill_commit`), so a run that took a newer skill
with `VERI_NEW_SKILL=1` is the sha changing partway down that file.

The catalogue of every script (arguments, output, exit codes) is `<base directory>/SCRIPTS.md`.
Read it before calling a script whose arguments, output or exit codes the step at hand does
not spell out.

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
budget: **call `wait-leaf.sh` again**, as many times as it takes. Make every foreground
`wait-leaf.sh` call with no max-seconds argument and the Bash tool's maximum `timeout` of 600000 ms:
the 600 s foreground cap is the limit, so a wait costs one call per 590 s and no fewer. Only a 0, 1 or 2 is an
answer. Read the leaf's report from `.tdd/<name>.out` — the captured stdout — instead of
from the launcher's stdout, which the detached call no longer hands you.

A leaf's `BASH_DEFAULT_TIMEOUT_MS` and `BASH_MAX_TIMEOUT_MS` follow its effective timeout, the one
`supervise.sh` enforces (`VERI_TIMEOUT`, else the run's `.tdd/issue-<n>-timeout`, else 900 s),
unless the caller set them, so a foreground suite is not cut off at the Bash tool's default.

Never `nohup … &` in place of that detach: `nohup` makes the leaf ignore a hang-up (SIGHUP),
but it leaves it in the **process group** of the Bash call that launched it, so a harness
that signals that group when the call ends takes the leaf with it. A leaf killed that way
writes no completion file, so the wait above returns exit 3 forever and you read that as
"still running" — the run stalls with nothing to say why.

**Before every leaf launch, ask whether a stop was requested: run `$S/stop-requested.sh`**
ahead of the `rm -f`, for a developer leaf and a verifier alike. On exit 3 no stop is
pending: launch as normal. On exit 0 branch on the mode it printed — `at-ledger` launches the
leaf anyway, because every leaf between two ledger commits is on the way to the next one, and
`at-leaf` or `now` launch nothing and go to *Stopping*: `Read` and run `<base directory>/STOPPING.md`. On exit 2 treat it as a stop in mode
`at-ledger` (read that file likewise), narrating that the request was unreadable: a `.tdd/stop` exists, so somebody
meant to stop this run, and only how urgently is in doubt — the mode that cannot be wrong is
the one that loses nothing.

**Before reading any leaf's exit 2 as killed-stuck, run `$S/stop-requested.sh`.** A pending `at-leaf` or `now`
stop makes `supervise.sh` refuse the launch with exit 2 (and a `now` stop also kills a live leaf), so the wait comes back 2 exactly as a hung leaf's does: either pending
mode explains the 2, and the run goes to *Stopping* instead of bailing: when that happens, `Read` and run `<base directory>/STOPPING.md`. Any other answer
leaves the 2 to be read as the phase below reads it, with one check first, for a developer leaf and whatever the phase: when
`.tdd/<name>.err` carries the supervisor's status line `supervise[<name>]: killed-external`, the leaf died with no recorded exit
and veri did not kill it, so do not relaunch the leaf, and **bail** with cause `killed-external`, a system failure: `Read` and run `<base directory>/BAIL.md`. Any other exit 2 is left to be read as the phase below reads it.

Whenever this procedure says **bail**, with the cause the bailing line names, `Read` and run `<base directory>/BAIL.md`.

**A conductor never asks the user a question, and never declines the procedure's next instruction.** No
one answers a headless run, so a turn that ends on a question leaves a run that looks in progress. If you
would ask, or would decline, **bail** with cause `needs-user` (a process failure) instead — this covers
every place the procedure itself says to ask the user, preflight check 1's dirty-tree stop and
*Detecting the test command*'s exit-3 ask among them — writing the
question in full into the bail comment so a resume or the human can answer it (`Read` `<base directory>/BAIL.md`).

The launch carries `VERI_TEST_CMD`: the run's test command, reaching the leaf through its
**environment** rather than its prompt, so the verifier stays blind. It is a prefix on the
launch line and not a one-off `export` because every Bash call you make is a fresh shell, so
nothing set in preflight survives to a launch three steps later.

It carries `VERI_ISSUE` and `VERI_STEP` for the same reason, and they are the same two
values your own marks below spell: the supervisor's `launch` and `exit` events and the
verifier's `verdict` event are written by `event.sh`'s module, `veri/event.py`, called
in-process by the supervisor and the verifier, which reads the run context out of their
environment. Nothing downstream can supply it — `leaf-role.sh` derives
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
killed developer leaf: **bail** cleanly, do not retry, and do not quote the
reason file for a verdict nothing wrote (see `<base directory>/BAIL.md`).

**Never launch a leaf in a background Bash call and then wait for its notification.** The
conductor often runs as a print-mode session (`claude -p "/tdd <n>"` — one of the two
unattended modes `README.md`'s *Launching the conductor* describes), and in print mode that notification never arrives: the turn ends, the
`claude -p` process exits, and the leaf is orphaned. The supervisor keeps running it under
`.tdd/`, but nothing will ever read its result, tick the ledger or narrate the outcome (this
is how #70 was lost). The detach-then-wait shape behaves identically interactively and
unattended, so it is the only one this procedure uses.

The same holds for the conductor's own long commands: no step backgrounds a command (the baseline or full-suite `make test` included) and ends its turn. They go through `detach-command.sh start`, then `detach-command.sh wait` in the foreground.

The conductor never ends its turn while anything it started is still running: a subagent, a background command or a background task. Ending the turn ends the process and kills it, so it waits for each one inside the turn (`detach-command.sh wait` for a command, the subagent's own result for a subagent). That covers the mutation-parity pairs table, which it builds inline or waits for inside the turn.

## Inputs

There is one command, so what the user typed after it is what decides which of the two
procedures below runs. No shape of argument is ever a question to put back to the user: a
word that is not a number is never a malformed issue number, and an empty argument is never
a missing one. Read the first word of `$ARGUMENTS` and resolve it three ways — there is no
fourth case:

- **An integer** — it is an issue **number** `<n>`, and this invocation is the
  single-issue procedure: run *Procedure* below on that issue, end to end.
- **Any other word** — it is a **scope** to drain: `Read` this skill's `SCOPE-LOOP.md`
  and run *Draining a scope — the loop* from it (beside this file, at
  `<base directory>/SCOPE-LOOP.md`). That loop selects the issues in that scope and runs the single-issue
  procedure over them one at a time. It lives in its own file because only this branch ever
  executes it, and an integer argument takes *Procedure* and never comes back — so keeping
  it here would bill every single-issue conductor for procedure it will not read (#202).
- **No argument at all** — a bare invocation is the scope `plain`, so it takes the scope
  branch above with `plain` as its scope.

A session born as a **worker** `<name>` takes none of those three: `Read` this skill's `WORKER.md`
and run *The worker loop* from it, which works the issues the work queue assigns to `<name>`
through the single-issue procedure (beside this file, at `<base directory>/WORKER.md`). It
lives in its own file for the same reason `SCOPE-LOOP.md` does: only a worker ever reads it.

## Procedure

Work through these steps in order. If a **preflight** step fails, stop and tell the user
what is wrong — do not start a cycle on a poisoned baseline. Once the cycle is underway,
drive it to a draft PR or to a clean stop on a `REJECT`.

### 0. Preflight — baseline checks (bail before any cycle)

`Read` `<base directory>/PREFLIGHT.md` and run it.

### 1. Read the issue, enter the issue's worktree, capture the spec (or resume)

1. Read the issue: `gh api repos/{owner}/{repo}/issues/<n> -q '{number, title, body, url: .html_url}'`.
2. **Derive the slug and enter the issue's worktree.** Slug from the title — lowercase,
   non-alphanumerics to `-`, collapse and trim `-`, cap to ~6 words. Preflight step 3 has
   already let `issue-worktree.sh` make (or hand back) the worktree the issue branch lives
   in, and moved into it, so its baseline runs on the branch's own commit.
   Preflight step 3 took the worktree's lock there too, before the baseline: that lock is
   the **worktree guard**, and it guards this machine's worktree only: for
   exactly as long as the pid in there answers `kill -0` and that process's start time matches the one recorded on the lock's second line, `issue-worktree.sh` refuses this
   worktree to a second conductor on this computer, so none can land in a live run's tree and
   resume it (#170), and a `git reset --hard HEAD` on a `⟂ refactor pending` step throws your
   leaf's uncommitted work away, per `<base directory>/RESUME.md`. It is **not** the claim on the issue. A pid is a
   machine-local name, veri is developed from more than one computer, and `origin` is all they
   share: what keeps the issue out of `solvable-issues.sh`'s pool is the draft PR step 2.3
   opens as the first act after the plan commit — minutes from here, and open for the rest of
   the run, a bail included (ADR-0024). Until that PR exists this lock is the only mark of the
   run there is, which is why the window between this worktree and the plan commit is the one
   place two machines can still collide.
   `run_conductor.py` writes the pid of the `claude -p` process, which lives as long as this run, rather
   than a shell's `$$`, which is gone when anyone reads the lock, so the guard is never dead on arrival
   or left naming a number since handed to a stranger. `run_conductor.py` deletes the lock when the run it launched ends; a crash
   or a `kill` that skips that leaves a lock no live process matches, which frees the worktree — never the issue, which its PR goes on holding — and a resume's `run_conductor.py` overwrites it with its own before preflight.
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
   What it writes is enumerated in its entry in `SCRIPTS.md`, the one place that list
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
   comment naming the next unchecked step, and go straight to the cycle loop (step 3), once you `Read` and follow `<base directory>/RESUME.md`.
   Otherwise continue to step 2 to scope and plan. This check needs no special casing for a
   re-run: `issue-worktree.sh` is **idempotent**, so a second invocation puts you back in the
   same worktree the first run built, with its committed ledger already on disk.
6. **Claim the issue on a fresh run.** Preflight has passed; before step 2's planning, run
   `$S/unlabel-issue.sh <n>`, which removes the opt-in label (`VERI_LABEL`) so `solvable-issues.sh`
   stops listing the issue, and adds the label `taken:<lane>`, `<lane>` being the text after
   `VERI_LABEL`'s last `:`, or `main` when it has none. This is the run's **first claim**; the
   draft PR is its **durable claim**. A bailed or parked issue keeps `taken:<lane>`, so it never
   looks like one nobody opted in, as parking already does. A human re-queues a claimed issue by
   restoring the opt-in label and removing `taken:<lane>`: `solvable-issues.sh` never lists an
   issue carrying any `taken:*` label, so both edits are needed (#2030).
   A resume skips this: it already ran. On a resume the issue's missing opt-in label is
   expected, since the claim removed it at the first launch, so never stop or ask about it.

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

**A step whose code cannot be written without a branch only a later step's test pins is ordered after that step, or merged with it.** A loop's fall-through return, a required `else`: the code cannot be written without the branch, and no test of this step requires it, so the blind verify-green rejects it as unrequired code (#775). The pinning step comes first, or the two are one step (#2607).

**A step that makes code produce a new outcome an existing caller does not yet handle is ordered after the step that adds that caller's handling.** A new rejection, error or empty result reaching a caller that cannot yet take it turns that caller's existing cases red the moment the producer starts producing it, and Green may not edit a test to put them right (#946, #2607).

**The step that adds a script owes its contract in that same step.** A step that adds a script under `skills/tdd/scripts/` also gives it a no-argument usage line and exit 2, and a declared caller, in that same step, so the step can go green against the repo-wide audits (the `run_cli` no-argument case in `tests/py/unit/test_missing_argument_cli.py`, unreachable); a usage or caller left to a later step leaves the first step red whatever its green does, as #1621's did.

**A step that changes text older cases pin is preceded by the step that updates them.** When a criterion changes text or output that existing cases outside the step's own Red pin (a usage string, a constant, the text of a prompt compared verbatim or by checksum), the plan holds a step that updates those older cases, placed ahead of the step that changes the text (except a sentence a `⟦skill-edit⟧` step changes, below: that step carries its own pin updates); Green may not edit a test, so without it the older cases turn red and no leaf allowed to edit them is ever launched, as #1719's step 8 and #1718's first runs found.

**A step names exactly one observable outcome.** A behaviour and each distinct refusal, exit code or fail-closed branch its criterion names are planned as separate steps, one outcome per step: the Red phase's one-case rule ("One criterion, one case") allows a step exactly one new case, and verify-green's demand that every guard be pinned by a case rejects a guard no case pins, so a step naming two outcomes cannot satisfy both and cannot go green. The rule is keyed on the count of named outcomes, never on the mere presence of a guard: a step naming one outcome alone, a behaviour or one guard, is not split (#2553).

**One step never both renames a pytest case and changes its body.** Work that does both is planned as two steps: the body amended under the old name first, then the rename with the body otherwise unchanged (#2594).

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

   A criterion that changes rendered prompt text, or a SKILL.md sentence that a suite pins by checksum or verbatim outside a unit with a requirements list (that unit is a `⟦skill-edit⟧` step, below), is planned as a `⟦diff-checked⟧` step, never as Red/Green: a Red leaf cannot compute a checksum of text that does not exist yet. The text and every checksum or verbatim pin it moves land in one commit, judged blind against the diff.

   When that criterion also asks for a case pinning that text, the plan holds a `⟦diff-checked⟧` step for the text and a separate step for the case, both tagged with the same `⟦criterion k⟧`, the case's step after the text's: the `⟦diff-checked⟧` step adds no test, so it cannot carry the pin.

   For each criterion that changes a unit with a requirements list, or for each unit an issue's `## Requirements` section names, the plan holds one `⟦skill-edit⟧` step naming the unit. A change to a unit with a requirements list is planned as its `⟦skill-edit⟧` step whatever kind of step the change would otherwise be, `⟦diff-checked⟧` included; no other step kind (Red, Green, Refactor, `⟦diff-checked⟧`, pin or phased) edits such a unit. A run signs a requirements list only inside a `⟦skill-edit⟧` step: the conductor never runs `grade-prose.sh` and commits a `GRADED` line on its own, except the Draft PR step's regrade of a unit the run already signed. When a `⟦skill-edit⟧` step changes a sentence that cases outside the unit pin by checksum or verbatim, the plan names those test files on the step, and that step updates the pins and commits them in its one commit with the unit, its list and `GRADED`; the separate pin-update step above is not planned for that sentence.

   On a `⟦skill-edit⟧` step, in place of Red, Green and Refactor, `Read` and run `<base directory>/SKILL-EDIT.md`.

   A criterion replacing an implementation case under ADR 0027 with a pytest case asserting
   the same behaviour is planned as one step marked `⟦replaces-case⟧`, naming the suite path
   and a list of that suite's cases, each by its exact name: `- [ ] <criterion>: replaces
   '<case name>', '<case name>' in <suite path> ⟦replaces-case⟧ ⟦criterion k⟧`. Group
   related cases of one suite into one step, about a dozen at most; one case is a valid
   group of one. That step's Red is the pytest cases failing against the code before the
   change; its Green deletes the named bash cases and nothing else. A replacement that drives
   unchanged code passes against it by design:
   when a Red reports `AGAINST_UNMODIFIED: PASSES`, the step takes the pin path, verify-pin and then a green leaf that deletes exactly the named cases (`Read` `<base directory>/PIN.md`).
   Refactor and the ` ⟂ refactor pending` mark follow that deletion green as they follow any Green.

   A criterion about behaviour that lives in a guard suite (such as
   `skills/tdd/scripts/tests/py/test_no_tracked_artifacts.py`) or a test helper a suite uses (such as
   `skills/tdd/scripts/tests/py/conftest.py`), so that only editing that file can meet it, is
   marked `⟦guard-subject: <path>⟧`, naming that file: the test freeze then lets Green
   edit it. The path is the full repo-relative path, matched exactly: a directory or a glob
   exempts nothing. The case pinning the behaviour stays frozen, and any other unrecorded test file is still flagged.
   A guard-subject that is also its step's Red test file is never exempted, because `tests-frozen` records the Red's test file whole: the plan puts that step's Red case in a different file, and verify-plan rejects a plan whose step names one file as both.

   An **interface change** — a production interface replaced by a new one, its callers moved
   across, the old one removed (ADR 0030) — is planned as one step listing the phases it
   needs, in the order they run: `- [ ] <criterion> ⟦phases: expand, cover-new, migrate,
   contract-a, contract-b⟧ ⟦criterion k⟧`. `cover-new` is listed for every interface change
   that adds a new interface; a phase with nothing to do is left out of the list.
   When the criterion also asks for a test case (a case that refuses a sibling script's
   start at the process boundary, say), plan that case as a separate Red/Green step tagged
   with the same `⟦criterion k⟧`, so the case never exists only inside the phased step.

   Each step's text carries every constraint the issue attaches to the cases that step covers,
   because the leaves work from the step text and not from the issue: the case size it must
   keep (a medium case, with a real process), "no production change", and any end-to-end path
   through real processes that must stay covered. A step that can be satisfied only by editing
   a test is planned as a test-only step, never as Red/Green, since Green may not edit a test.
   A step whose work adds a test case for behaviour that already holds is a pin step (an
   ordinary step whose Red reports "already passes"), never `⟦diff-checked⟧`: that mark is
   reserved for steps that leave no test behind.

   The one exception is a defect in a test's own fixture, stub or harness whose script under
   test is correct. Plan it as `- [ ] <criterion>: repairs the fixture '<fixture or stub name>' in
   <fixture file>, reproduced by a case in <test file> ⟦fixture-repair⟧ ⟦criterion k⟧`. Name the
   fixture by a function, stub or helper, never a line range; `<fixture file>` must be a test file
   by the rule of transform-touches-tests. Use the mark for nothing else: a defect in the script
   under test is an ordinary step. Such a step is an ordinary Red/Green step whose criterion is
   that the reproducing case passes against the unchanged script under test; Green may edit only
   the named fixture.

   An issue whose work changes only tests (extracting a repeated helper, sharing a fixture,
   production untouched) is planned as `⟦diff-checked⟧` steps, whatever its label, refactor-kind or not.

   When the spec carries the `## Refactor` section `capture-spec.sh` writes for the `refactor`
   label: when you plan, and on a resume before the first step since a resume skips the plan, and
   not before, `Read` and run `<base directory>/REFACTOR-KIND.md`.
2. **Commit the ledger** as the run's starting point. Before committing, run
   `$S/scope-check.sh .tdd/issue-<n>.md .`: it exits 1 when a step names a new `test_<x>.py` under
   `skills/tdd/scripts/tests/py/` whose basename already exists anywhere under it (pytest refuses
   two modules of one basename) and its stderr names both paths, so rename the step's module with
   a `_process` or `_cli` suffix and run it again. It also exits 1 when a step line carries more than
   one `⟦criterion k⟧` tag, naming the line on stderr: rewrite the plan so each such step serves one
   criterion, splitting it where needed, and run the check again. The plan is never committed with a
   multi-tag step:
   `git add .tdd/issue-<n>.md && git commit -m "plan: scope #<n> into <k> steps (#<n>)"`.
   (The ledger is committed — step 1.4 guaranteed `.gitignore` tracks `.tdd/issue-*.md`
   while ignoring leaf logs.)

   **Every ledger commit after this plan commit is checked for growth.** Before it is made, run
   `$S/ledger-growth.sh <plan-ledger-file> .tdd/issue-<n>.md`, the plan-ledger being the ledger as the
   plan commit holds it (`git show <plan-sha>:.tdd/issue-<n>.md` into a temp file). `<plan-sha>` is the
   newest plan commit, as `git log --format='%H %s' | $S/ledger-growth.sh plan-sha` prints it: after a
   verify-plan REJECT, the `plan: rewrite` commit is that baseline, so a rewritten plan's own lines
   are never checked as added. Each step line the plan commit did not hold must have a matching
   record written by `add-ledger-step.sh` itself, never one the conductor wrote by hand with
   `event.sh`. The records the check reads are the ones `ledger-growth.sh` reads: the tracked
   `.tdd/issue-<n>-added.md` that `add-ledger-step.sh` writes, and the run's `step-added` events
   it wrote. So every commit that inserts a ledger step stages that file with the ledger
   (`git add .tdd/issue-<n>.md .tdd/issue-<n>-added.md`, or `git add -A`), the `⟦suite-repair⟧` and
   `⟦ci-repair⟧` plan commits and the resume's `--planned` commit included. Each such line must
   carry `⟦added⟧` unless that record shows it was inserted as a `⟦suite-repair⟧` or
   `⟦ci-repair⟧` step or with `--planned`; and the
   `⟦added⟧` lines never exceed `VERI_STEP_GROWTH`. A line that fails either check — exit 1, the
   line named on stderr — is **a bail with cause `step-added-off-route`** (a process failure): the plan
   grew by a route other than `add-ledger-step.sh`, and no commit is made over it (see `<base directory>/BAIL.md`). `ledger-growth.sh` exit 2 — no answer could be obtained (an unreadable
   ledger, plan file or record, a bad `VERI_STEP_GROWTH`, no plan commit for `plan-sha`) — is **a bail
   with cause `no-verdict`** (a system failure), never `step-added-off-route`, and no commit is
   made over it (see `<base directory>/BAIL.md`).
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

Right before verify-plan launches, refresh the captured spec from the live issue:
`$S/refresh-spec.sh <n> .tdd/issue-<n>-spec.md`. Exit 0 (refreshed) and exit 3 (nothing to
refresh) go on. Exit 2 (no answer) goes on with the capture as it stands. Exit 1 means the
live criteria count differs from the capture's: **bail** with cause `needs-user`, naming both
counts in the bail comment, before the verifier launches (`Read` `<base directory>/BAIL.md`).

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
  last re-verification is still `REJECT`, **bail** as a process failure —
  the plan, not a leaf, is what the methodology rejected (see `<base directory>/BAIL.md`).
- **Malformed / killed-stuck (exit 2):** no verdict could be obtained — **bail** as a system
  failure, after the stop check in *Launching a leaf* (see `<base directory>/BAIL.md`). A plan nobody looked
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
in the environment as `SCRIPTS.md` sets out, so one instruction carries the whole
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

- **exit 0 — split.** Exactly the revise-exhausted path's split:
  `.tdd/over-budget-answer.txt` holds the criteria, one per line, and they replace the step (when a verifier answers `REJECT`, `Read` `<base directory>/REVISE.md`).
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
  other two paths that grow a plan — see `<base directory>/BAIL.md`. The split shares `VERI_STEP_GROWTH` with
  them, because all three are plan growth. **`add-ledger-step.sh` exit 2 → bail with cause
  `step-add-refused`** — see `<base directory>/BAIL.md`.
- **exit 1 — a decision for the user.** `.tdd/over-budget-answer.txt` holds the leaf's answer.
  **Park the step** — the same park the revise-exhausted path takes: stop the
  run there, carrying that answer and the two figures, what the step has spent and the
  step budget, and leave the plan as it is so the user's decision picks the run back up (when a verifier answers `REJECT`, `Read` `<base directory>/REVISE.md`):
  ```
  step="$($S/next-unchecked.sh < .tdd/issue-<n>.md)"; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh step-escalated at=over-budget anchor="$step"
  ```
  The `at=over-budget` is what tells this park apart from the revise-exhausted one: a verifier
  that could not be satisfied and a step that got expensive are different facts about the run.
- **exit 3 — neither answer: record the crossing and carry on with the step.** This is
  **not a bail**, and it is where this path parts from the revise-exhausted one, whose exit 3
  bails with cause `revise-exhausted` because a verifier that will not pass the work leaves
  nothing to go on with (`Read` `<base directory>/BAIL.md`). Here nothing has failed, for the reason the section gives above, and
  bailing a converging step because it is expensive is exactly what this check exists not to do. The
  `step-over-budget` mark written before the launch already records the crossing, so this branch
  writes none of its own: leave the check disarmed, and let the step finish normally.

A **supervisor exit 2** on the over-budget leaf — `wait-leaf.sh` exits 2 — is a
**`killed-stuck` bail** like any other developer leaf's, and the step's budget
stays crossed: the check has fired for this step, and, as above, nothing re-arms it (see `<base directory>/BAIL.md`).

#### Before the Red of a `⟦suite-repair⟧` step — is the suite still red?

When the unchecked step carries `⟦suite-repair⟧`, run the full suite once on the current tip before its Red: the command is `$S/detect-test-command.sh --tier all`'s, run through `detach-command.sh` in the same start-then-wait shape as the preflight baseline. The red it was appended for may be gone (a rebase or an earlier step fixed it), and a repair step whose red no longer exists could only get an `UNTESTABLE` or a pin.

- **Green:** retire the step. Mark `step="$($S/next-unchecked.sh < .tdd/issue-<n>.md)"; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh suite-repair-retired`, tick it with `$S/tick-ledger.sh .tdd/issue-<n>.md "$($S/next-unchecked.sh < .tdd/issue-<n>.md)"` (no `--refactor-pending`, since no refactor loop follows), and commit the ledger with `git add .tdd/issue-<n>.md && git commit -m "plan: retire the suite-repair step, the full suite is green (#<n>)"`. Launch no leaf for it. Continue at *4. Draft PR*, whose full run, rebase and regrade follow as usual.
- **Red:** the step proceeds to Red as below, the failing suites being its red evidence.

#### Red — one failing test (developer leaf), then verify-red (blind)

1. **Develop.** Before the prompt is built, run `$S/refresh-spec.sh <n> .tdd/issue-<n>-spec.md`.
   Exit 0 and exit 3 go on, and exit 0 is named in the step's `### 🔴 Red` comment as a
   refreshed spec. Exit 2 goes on with the capture, and the `### 🔴 Red` comment says so.
   Exit 1 (the live criteria count differs from the capture's) **bails** with cause
   `needs-user`, naming both counts in the bail comment, before any leaf of the step
   launches (`Read` `<base directory>/BAIL.md`).
   Then build the prompt from the `red` template — it already instructs the leaf to
   write **exactly one** failing test pinning the criterion to **observable external
   behavior**, with **no production code**, and to run **the suite holding that case**, not
   the full suite, against the unmodified code, since the only question Red asks is whether
   that one case fails — and launch the leaf **through the supervisor**:
   ```
   $S/build-develop-prompt.sh red .tdd/issue-<n>-spec.md "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" '<test-cmd>' > .tdd/develop-red.prompt
   rm -f .tdd/develop-red.exit .tdd/develop-red.pid .tdd/red-prediction.md .tdd/red-run-output.txt
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
   cleanly, after the stop check in *Launching a leaf*; do not retry (see `<base directory>/BAIL.md`).
2. **Verify (blind).** Branch on the leaf's `AGAINST_UNMODIFIED` line.
   On **`UNTESTABLE`** there is no test on disk for a blind verifier to judge — sending
   nothing to verify-red would only get a malformed-verdict `REJECT` for the wrong reason —
   so skip verify-red and verify-pin entirely and **bail** immediately with cause
   `untestable-criterion`, carrying the leaf's `WHY:` as the reason (see `<base directory>/BAIL.md`). This is
   a **process** failure: the criterion as phrased cannot be tested as behavior, not that
   the plumbing broke.
   On **`FAILS`**, check the prediction before any verifier: run `red-divergence.sh` on the
   leaf's report and branch on **its** exit code:
   ```
   $S/red-divergence.sh .tdd/red-prediction.md .tdd/red-run-output.txt < .tdd/develop-red.out > .tdd/verify-red.reason; echo $?
   ```
   - **Exit 1 — prediction not written before the run:** the prediction file is missing or newer than the run's output. Narrate "prediction not written before the run" in the `### 🔴 Red` comment, not a divergence, and write that line to `.tdd/verify-red.reason`. It still spends the attempt like a `REJECT`: skip verify-red and verify-pin and enter the revise loop for red (when a verifier answers `REJECT`, `Read` `<base directory>/REVISE.md`).
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
     **revise loop** for red exactly as a verify-red `REJECT` does — the revise leaf answers `.tdd/verify-red.reason`, and the attempt spends
     `REVISE_BUDGET` like any other (when a verifier answers `REJECT`, `Read` `<base directory>/REVISE.md`).

   Run `$S/unreplaced-cases.sh "<step line>" .tdd/develop-red.out` on a `⟦replaces-case⟧` step once the
   Red report is written, against the current attempt's report (`.tdd/revise-red-<k>.out` after a red
   revise), before verify-red launches. Exit 1 prints each named case with no `REPLACES:` line:
   give the Red one chance to correct its report. Launch one `develop-replaces-report` leaf, spending no `REVISE_BUDGET`
   attempt and writing no `revise` mark, then run `$S/unreplaced-cases.sh` again as `$S/unreplaced-cases.sh "<step line>" .tdd/develop-red.out .tdd/develop-replaces-report.out` (`.tdd/revise-red-<k>.out` in place of `.tdd/develop-red.out` after a red revise), so a case the Red report already replaced still counts and a correction naming exactly the missing cases does not bail, before verify-red launches.
   Exit 1 again: **bail with cause=unreplaced-cases**, naming each case it printed, and launch no second correction leaf and no verifier — verify-green
   never runs on a step whose named cases lack a replacement (`Read` `<base directory>/BAIL.md`). Exit 2 — no answer could be obtained (no
   readable report, bad arguments) — bails with cause=unreplaced-cases at once, launching no correction leaf and no verifier (`Read` `<base directory>/BAIL.md`).
   The correction leaf: save the printed cases to `.tdd/replaces-missing.txt` (and read `.tdd/revise-red-<k>.out` in place of `.tdd/develop-red.out` after a red revise), then
   `$S/build-develop-prompt.sh replaces-report .tdd/issue-<n>-spec.md "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" '<test-cmd>' .tdd/develop-red.out .tdd/replaces-missing.txt > .tdd/develop-replaces-report.prompt`,
   `rm -f .tdd/develop-replaces-report.exit .tdd/develop-replaces-report.pid`, then
   `VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" $S/detach-leaf.sh $S/supervise.sh develop-replaces-report $S/run-leaf.sh .tdd/develop-replaces-report.prompt --permission-mode bypassPermissions > .tdd/develop-replaces-report.out 2> .tdd/develop-replaces-report.err`
   and `$S/wait-leaf.sh develop-replaces-report` in the foreground (on exit 3 call it again).
   Then run `$S/step-cost.sh "$($S/next-unchecked.sh < .tdd/issue-<n>.md)"` like after every other leaf. If that wait exits 1 or 2 (a killed-stuck correction leaf included), **bail with cause=replaces-report-failed** and launch no verify-red (`Read` `<base directory>/BAIL.md`).

   **Before each verify-red launch** (and before each verify-green, below), also check every earlier step's frozen record:
   `$S/tests-frozen.sh check-earlier .tdd/issue-<n>.md --step "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" [--except <case>]…`,
   with one `--except` for each case the current step's route names (`red-contradicted`, `red-supersede`, `repair`,
   `⟦replaces-case⟧`, `⟦fixture-repair⟧`). Exit 1 prints each changed or deleted case of an earlier step, with its step (a case renamed with its text otherwise unchanged is neither changed nor deleted):
   write that to `.tdd/verify-red.reason`, treat the attempt as a verify-red REJECT that spends REVISE_BUDGET, and launch
   no verifier for it. Exit 0 launches the verifier as before; exit 2 is a system failure: **bail** (`Read` `<base directory>/BAIL.md`).

   On a matched prediction, run
   the red verifier against the on-disk test and spec, **redirecting its stdout (the
   reason) to a file** — the revise step takes the reason as a *path*, not as text you
   retype:
   ```
   rm -f .tdd/verdict-red.exit .tdd/verdict-red.pid
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" $S/detach-leaf.sh $S/supervise.sh verdict-red $S/run-verdict.sh --step "$(cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" --fast-cmd '<fast-cmd>' red .tdd/issue-<n>-spec.md <test-path> <target-test-id> > .tdd/verify-red.reason 2> .tdd/verify-red.err
   $S/wait-leaf.sh verdict-red     # foreground; on exit 3 call it again
   $S/step-cost.sh "$($S/next-unchecked.sh < .tdd/issue-<n>.md)"   # the step's cost check — see *The step's cost check*
   ```
   Once verify-red PASSes, record the step's test files as they stand with
   `$S/tests-frozen.sh record --step "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" <test-path>`; tests-frozen exit 2 is a bail (see `<base directory>/BAIL.md`).
   With `--step "<step text>"` in place of a record file, the record file is the one `$S/tests-frozen.sh path "<step text>"`
   prints, `.tdd/tests-frozen-<k>.record` with `<k>` the first 16 hex digits of the step text's SHA-256: a step text is
   often longer than a filename may be and may hold a `/`, so the text itself is never the filename.
   That is the verifier shape from *Launching a leaf*: the wait returns the **verdict** —
   0 PASS, 1 REJECT, 2 malformed or killed-stuck — not the supervisor's status.
   On **`PASSES`** the criterion is **already satisfied** — never send that test to
   verify-red, whose verdict on a passing test can only be `REJECT`. Run the pin check
   instead and continue at the pin (when a Red reports `AGAINST_UNMODIFIED: PASSES`, `Read` `<base directory>/PIN.md`):
   ```
   rm -f .tdd/verdict-pin.exit .tdd/verdict-pin.pid
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" $S/detach-leaf.sh $S/supervise.sh verdict-pin $S/run-verdict.sh --step "$(cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" pin .tdd/issue-<n>-spec.md <test-path> <target-test-id> > .tdd/verify-pin.reason 2> .tdd/verify-pin.err
   $S/wait-leaf.sh verdict-pin     # foreground; on exit 3 call it again
   ```
   A `⟦ci-repair⟧` step is the one exception to `PASSES`: its test failed on CI and may pass
   here, so on `AGAINST_UNMODIFIED: PASSES` it goes on to Green with the failing CI job's log
   (test id and assertion diff) as its red evidence, never to verify-pin and never to the
   `test: pin` tick-and-commit.
   A step marked `⟦suite-repair⟧` or `⟦ci-repair⟧` is never frozen: for it `record --step` writes nothing and
   `check --step` exits 0, because its fix is often an edit to the very test file the full run or CI left red.
   A `⟦ci-repair⟧` step therefore records nothing before its green, and its green may edit the test the CI job failed.
   A step whose trailing marker is `⟦fixture-repair⟧` is frozen like any other, except for the one fixture file its
   text names (`repairs the fixture '<name>' in <path>,`): `check --step` exits 1 naming any other changed test file.
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
   - **REJECT (exit 1) whose reason file `.tdd/verify-red.reason` begins with a `GATE:` line:**
     the step's Red is routed back to the Red phase, not into the revise loop. Launch the
     `red-repair` red over the step's own target test through `supervise.sh`
     (`$S/build-develop-prompt.sh red-repair .tdd/issue-<n>-spec.md "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" '<test-cmd>' <target-test-id> .tdd/verify-red.reason`, the
     reason file being the brief), write no `revise` mark and spend no `REVISE_BUDGET`
     attempt, then run verify-red again. The route is taken **once per step**: a second
     `GATE:` REJECT in the same step after it is an ordinary verify-red REJECT, below.
   - **REJECT (exit 1):** enter the **revise loop** — when a verifier answers `REJECT`, `Read` `<base directory>/REVISE.md`. It
     returns either PASS (continue to Green) or budget-exhausted (**bail**, process failure) (`Read` `<base directory>/BAIL.md`).
   - **Malformed / killed-stuck (exit 2):** the verdict could not be obtained (unparseable
     or the verifier leaf was killed) — **bail** as a system failure, not a
     clean process stop (see `<base directory>/BAIL.md`). A verifier that exited cleanly with no verdict has already been
     relaunched by `verify.sh` itself, up to `VERI_NO_VERDICT_RETRIES` times (default 1,
     ADR-0020), so exit 2 arrives here only once that budget is spent — never relaunch it
     again from the conductor.

#### Green — minimum implementation (developer leaf), then verify-green (blind)

1. **Develop.** Build the prompt from the `green` template — the **minimum** production
   code, no generality the test does not demand, the **test itself untouched**, the
   fast command and the affected suites green — and launch **through the supervisor** (exit **2** → **bail**, after the stop
   check in *Launching a leaf*; see `<base directory>/BAIL.md`):
   ```
   $S/build-develop-prompt.sh green .tdd/issue-<n>-spec.md "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" '<test-cmd>' <test-path> '<target-test-id>' '<fast-cmd>' '<owed-cases>' > .tdd/develop-green.prompt
   rm -f .tdd/develop-green.exit .tdd/develop-green.pid
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" $S/detach-leaf.sh $S/supervise.sh develop-green $S/run-leaf.sh .tdd/develop-green.prompt --permission-mode bypassPermissions > .tdd/develop-green.out 2> .tdd/develop-green.err
   $S/wait-leaf.sh develop-green    # foreground; on exit 3 call it again
   $S/step-cost.sh "$($S/next-unchecked.sh < .tdd/issue-<n>.md)"   # the step's cost check — see *The step's cost check*
   ```
   The test path and target test id are the ones Red's report gave you. The leaf's report is
   in `.tdd/develop-green.out`, and ends with `IMPL_PATH:` (the production files it created
   or changed) and `SUITE: GREEN | RED` plus the suite's final summary line; both go into the
   narration below.

   After the wait exits 0 and before verify-green is launched, run `$S/suite-reported.sh develop-green`:
   exit 2 means the report carries no `SUITE:` line, so launch no verifier and **bail** as a system
   failure with cause `report-missing` (`Read` `<base directory>/BAIL.md`). A green that stops because the test looks wrong is exempt: it
   keeps its main outcome, a verify-green REJECT (a process outcome), never a `report-missing` bail.

   **A green report carrying `WRONG_TEST:` or a `SUPERSEDED:` line, with or without `WRONG_TEST:`,** gets `$S/wrong-test-route.sh .tdd/develop-green.out '<target-test-id>'` before any revise:
   - exit 0 prints `red <case>`, a case other than the step's own that the criterion contradicts. Run it with `VERI_STEP` set to the current step, and on exit 0 write a `reroute` event before the launch: `VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/next-unchecked.sh < .tdd/issue-<n>.md)" $S/event.sh reroute case=<case> kind=red`, `kind` being the first word `wrong-test-route.sh` printed, so a repeat `missing` reroute is distinguishable from a repeat of any other kind. The `red`, `repair`, `supersede` and `fixture` routes share the step's one free reroute, free only as the step's first reroute of any kind, `missing` included: a later `WRONG_TEST:` in the same step, once that reroute is used, answers `revise` (exit 3) and spends one `REVISE_BUDGET` attempt. A prior `missing` reroute uses up that free reroute, while `missing` itself stays free up to `VERI_MISSING_REROUTE_BUDGET` (see `missing` below). Write no `revise` mark and spend no `REVISE_BUDGET` attempt for the free one. Launch the `red-contradicted` red over that case through `supervise.sh` (`build-develop-prompt.sh red-contradicted`), verify it with verify-red like any red, re-record the step's frozen tests with `$S/tests-frozen.sh record --step "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" --red-case '<red-test-id>'` over both test paths, then retry green.
   - exit 0 may instead print `repair <case> <superseded>…`, a case the step's own Red wrote, with any older cases the green report lists on `SUPERSEDED:` lines (the case is the step's own `<red-test-id>` or is in the step's red record). It shares the step's one free reroute with `red`, `supersede` and `fixture`, free only as the step's first reroute of any kind, `missing` included (a prior `missing` reroute uses it up) and writes the same `reroute` event with `kind=repair` before the launch, with no `revise` mark and no `REVISE_BUDGET` attempt. Launch the `red-repair` red through `supervise.sh` (`build-develop-prompt.sh red-repair <case> .tdd/develop-green.out <superseded>…`: the case, the green report, which says why it is wrong, and the superseded cases), verify it with verify-red like any red, re-record the step's frozen tests with `$S/tests-frozen.sh record --step "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" --red-case '<red-test-id>'` over both test paths, then retry green.
   - exit 0 may instead print `supersede <case> <case>…`, two or more older cases the green report names on `SUPERSEDED:` lines because the step's change supersedes what they assert. It shares the step's one free reroute with `red`, `repair` and `fixture`, free only as the step's first reroute of any kind, `missing` included (a prior `missing` reroute uses it up) and writes the same `reroute` event with `kind=supersede` before the launch, with no `revise` mark and no `REVISE_BUDGET` attempt. Launch the `red-supersede` red through `supervise.sh` (`build-develop-prompt.sh red-supersede .tdd/develop-green.out <case>…`, every named case), verify each edited case with verify-red like any red, re-record the step's frozen tests with `$S/tests-frozen.sh record --step "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" --red-case '<red-test-id>'` over every test path, then retry green.
   - exit 3 (`revise`) runs the existing revise path unchanged: the verify-green REJECT.
   - exit 0 may instead print `missing <behaviour>`, a behaviour no test pins. The same route answers the other two entries: a verify-green REJECT (`$S/wrong-test-route.sh .tdd/verify-green.reason '<target-test-id>'`) and the conductor's mutation-parity REJECT (its stderr saved to a reason file, routed the same way), before any revise attempt is spent. It needs no free reroute of its own, though it uses up the step's one free reroute for the four other kinds: a `missing` route spends no `REVISE_BUDGET` attempt however many times one step takes it, bounded per step by `VERI_MISSING_REROUTE_BUDGET` (default 3). It writes the same `reroute` event with `kind=missing` before the launch, with no `revise` mark and no `REVISE_BUDGET` attempt. Launch the `red-missing` red through `supervise.sh` (`build-develop-prompt.sh red-missing .tdd/issue-<n>-spec.md "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" '<test-cmd>' <reason-file>`: the reason file is the brief), verify the added case with verify-red (verify-pin when it reports `AGAINST_UNMODIFIED: PASSES`), re-record the step's frozen tests with `$S/tests-frozen.sh record --step "$($S/next-unchecked.sh < .tdd/issue-<n>.md)" --red-case '<red-test-id>'` over the test paths, then run Green again. A second `red`, `repair`, `supersede` or `fixture` reroute in the step, and a rejection naming a product defect (`revise`, exit 3), spend `REVISE_BUDGET` as today. Once the step has taken `VERI_MISSING_REROUTE_BUDGET` `missing` reroutes, `wrong-test-route.sh` exits 1 printing `missing-exhausted <behaviour>`: **bail** with cause `missing-reroutes-exhausted`, a process failure (`Read` `<base directory>/BAIL.md`).
   - exit 0 may instead print `fixture <path> <name>`: `<name>` is a function defined in the test file `<path>` that is not a test case (a helper, fixture or shared setup). It shares the step's one free reroute with `red`, `repair` and `supersede`, free only as the step's first reroute of any kind, `missing` included (a prior `missing` reroute uses it up) and spends no `REVISE_BUDGET` attempt. Insert before the current step, with `add-ledger-step.sh … before`, the step `<the current step's criterion>: repairs the fixture '<name>' in <path>, reproduced by a case in <path> ⟦fixture-repair⟧`, commit the ledger, write the same `reroute` event with `kind=fixture`, and run that step's cycle; the current step then resumes at develop-green with its red case and frozen record kept. `add-ledger-step.sh` exit 1 (the growth cap, which files the step under `## Owed steps`) **bails** with cause `fixture-owed`, a process failure; exit 2 bails `step-add-refused` (see `<base directory>/BAIL.md`).
   - exit 2 is a system failure: **bail** (`Read` `<base directory>/BAIL.md`).

   After a reroute's red leaf and before the step's frozen tests are re-recorded, check that the step's own Red case (its `<red-test-id>`) still exists in its test file: the re-record's `--red-case '<red-test-id>'` is that check. A reroute that deleted it is a verify-red REJECT that spends `REVISE_BUDGET` (when a verifier answers `REJECT`, `Read` `<base directory>/REVISE.md`), and nothing is re-recorded: tests-frozen exit 1 writes no record and names the deleted case on stdout, which the conductor writes to `.tdd/verify-red.reason` as the reason.

   After that and before verify-green is launched, run `$S/tests-frozen.sh check --step "$($S/next-unchecked.sh < .tdd/issue-<n>.md)"`.
   On tests-frozen exit 1 a test file changed since verify-red, so write a reason naming the changed file to
   `.tdd/verify-green.reason`, treat the attempt as a verify-green REJECT that spends REVISE_BUDGET, and launch
   no verifier for that attempt. Run the earlier-steps check there too, as before verify-red above: its exit 1 is a verify-green
   REJECT naming the case and its step, spending REVISE_BUDGET, with no verifier launched; exit 2 bails (see `<base directory>/BAIL.md`). On tests-frozen exit 0 (and an
   earlier-steps exit 0) the verifier is launched as before.
   On tests-frozen exit 2 the check could not answer, so **bail** as a system failure, never a REJECT, and launch no verifier (`Read` `<base directory>/BAIL.md`).

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

   **`add-ledger-step.sh` exit 1 → bail with cause `step-too-big`** — see `<base directory>/BAIL.md`. The
   insertion would take the ledger past `VERI_STEP_GROWTH`, so the script has already filed
   the criteria under `## Owed steps`: the step's own red is discarded and the smaller steps
   it needs are not in the plan, so there is nothing for the run to go on with.
   **`add-ledger-step.sh` exit 2 → bail with cause `step-add-refused`** — see `<base directory>/BAIL.md`.
2. **Verify (blind)** — the verifier shape again, and the wait's code is again the verdict.
   Neither this verifier nor the develop leaf runs the full suite: a break outside the
   affected suites surfaces at the one full-suite run in *4. Draft PR*.
   The `⟦replaces-case⟧` unreplaced-cases check already ran in *Red*, before verify-red; it is not run again here.
   Run `$S/replaces-case-survivors.sh "<step text>"` before the launch below, on a ⟦replaces-case⟧ step only; its exit 1 means survivors (see the paragraph after the block).
   ```
   rm -f .tdd/verdict-green.exit .tdd/verdict-green.pid
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" $S/detach-leaf.sh $S/supervise.sh verdict-green $S/run-verdict.sh --step "$(cat .tdd/issue-<n>.md | $S/next-unchecked.sh)" --fast-cmd '<fast-cmd>' green .tdd/issue-<n>-spec.md <test-path> <target-test-id> > .tdd/verify-green.reason 2> .tdd/verify-green.err
   $S/wait-leaf.sh verdict-green    # foreground; on exit 3 call it again
   $S/step-cost.sh "$($S/next-unchecked.sh < .tdd/issue-<n>.md)"   # the step's cost check — see *The step's cost check*
   ```
   On a `⟦replaces-case⟧` step, a PASS is accepted only once the conductor's own run of
   `$S/mutation-parity.sh <pairs-table>` on that step's pairs table exits 0; exit 1 is a
   REJECT, exit 2 a bail (see `<base directory>/BAIL.md`). The PR body's pairs table is that run's report, and each row it
   reports owed goes into the PR body under `## Owed by a human`. Before that verify-green
   launches, the conductor runs `$S/replaces-case-survivors.sh "<step text>"`; exit 1 prints
   the named cases the suite still holds, and the conductor then relaunches the green leaf
   naming those survivors, records the relaunch as an event (`$S/event.sh`), and launches no
   verifier on that green. Each such relaunch spends one `REVISE_BUDGET` attempt, the verdict
   axis, since a surviving named case is a mechanical rejection of the green; when the budget
   is spent the run bails with `cause=revise-exhausted` (`Read` `<base directory>/BAIL.md`).
3. **Narrate + branch.** Post `### 🟢 Green` (implementation + green suite output) and
   `### 🔎 verify-green — PASS|REJECT` (the reason).
   - **PASS — check off the ledger step and commit atomically.** Tick STEP in the ledger,
     then commit the code **and** the ticked ledger in **one** commit so git and ledger
     never diverge. The tick carries `--refactor-pending`, which appends ` ⟂ refactor
     pending` to that same line: the step is green, but its refactor loop and
     verify-refactor are still ahead of it, so a run interrupted between here and them must
     resume into that loop rather than read the tick as *done*.
     **Before the tick, on every step not marked `⟦skill-edit⟧`, run
     `$S/graded-changed.sh <step-base-sha>`** over the step's commits, `<step-base-sha>` being the
     commit the step started from (`git log -1 --format=%H -- .tdd/issue-<n>.md`). Its exit 1
     prints each graded unit the step changed: **bail** with cause `graded-edit-outside-skill-edit`,
     a process failure, naming each unit it printed, and tick nothing (`Read` `<base directory>/BAIL.md`).
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
     rejected a non-fast-forward) launch the reconcile leaf: when that happens, `Read` and run `<base directory>/RECONCILE.md`.
     On exit **2** (its
     event could not be written) **bail** (`Read` `<base directory>/BAIL.md`).
     **Then run `$S/stop-requested.sh`**, immediately after that push: this ledger commit is
     the boundary `at-ledger` was waiting for, and `at-leaf` and `now` have nothing left to
     abandon, so on exit 0 any mode it printed goes to *Stopping* here (when that happens, `Read` `<base directory>/STOPPING.md`). On exit 2 go to
     *Stopping* in mode `at-ledger`, narrating that the request was unreadable. On exit 3
     continue to the Refactor loop.
     A `⟦ci-repair⟧` step's green is judged against a fresh CI run on the pushed fix,
     not only a local `make test`: after the push above, *4. Draft PR*'s `wait-ci.sh` line
     is called on the pushed sha, and read the way that step reads it. A red
     CI there is the second red, and **bails** with cause `ci-red` (see `<base directory>/BAIL.md`).
     A `⟦ci-repair⟧` step is judged by the ci-repair verify-green variant, which judges only evidence that exists before the push — the failing job's log before the fix, a diff touching what it names, the local suites green — and not the local revert-goes-red check, which a CI-only failure can never pass; the green CI run on the pushed fix comes after. It never requires a CI run on the fix. Its CI verdict is the post-push `wait-ci.sh` wait, where red bails `ci-red` (see `<base directory>/BAIL.md`).
   - **REJECT (exit 1):** enter the **revise loop** — when a verifier answers `REJECT`, `Read` `<base directory>/REVISE.md`. On a
     recovered PASS, do the same atomic tick-and-commit and continue; on budget-exhausted,
     **bail** (see `<base directory>/BAIL.md`).
   - **Malformed / killed-stuck (exit 2):** **bail** — see `<base directory>/BAIL.md`.

#### Refactor loop — one leaf applies the step's transforms, then verify-refactor (blind, once)

1. **One refactor leaf for the step.** Ask the budget first, with a count of **0**: that
   call is what decides whether the leaf runs at all, since `VERI_REFACTOR_BUDGET=0`
   switches refactoring off. Then build the prompt from the `refactor` template — which
   carries the budget to the leaf as the number of transforms it may apply — and launch
   **through the supervisor** (exit **2** → **bail**, after the stop check in *Launching a
   leaf*; see `<base directory>/BAIL.md`):
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
5. **Verify (blind, once) on the settled result — unless nothing landed.** After the checks
   in 2, when `git rev-list --count <green-sha>..HEAD` is 0 and `git status --porcelain`
   prints nothing — the leaf landed no transform, or the budget was 0 and no leaf ran —
   launch **no** verify-refactor: there is no change for it to judge. Record
   `VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$($S/next-pending-refactor.sh < .tdd/issue-<n>.md)" $S/event.sh verify-refactor-skipped reason=nothing-landed`,
   post `### 🔎 verify-refactor — SKIPPED (nothing landed)`, and treat the step as on a
   verify-refactor PASS whose verdict carries no flags: 6's PASS branch runs with the
   leaf's flags only. Otherwise:
   ```
   rm -f .tdd/verdict-refactor.exit .tdd/verdict-refactor.pid
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current)" $S/detach-leaf.sh $S/supervise.sh verdict-refactor $S/run-verdict.sh --step "$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current)" --fast-cmd '<fast-cmd>' refactor .tdd/issue-<n>-spec.md <test-path> <green-sha> > .tdd/verify-refactor.reason 2> .tdd/verify-refactor.err
   $S/wait-leaf.sh verdict-refactor  # foreground; on exit 3 call it again
   ```
   — one verdict on the final state (the **fast tier** plus the **affected suites** still
   green, code up to standard, no smuggled generality).
6. **Narrate + branch.** Post `### 🛠️ Refactor` (the transforms applied, or "no refactor
   warranted", plus any triangulation flagged) and `### 🔎 verify-refactor — PASS|REJECT|SKIPPED`.
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
   **test-only** candidate, and an **out-of-scope** one the rule below leaves to the
   structural pass, is in neither list: it is recorded through
   `refactor-owed.sh`, below and at the Draft PR, and is not narrated as a backlog. Each
   list says **how many candidates** it holds and then **lists** them, one per line. A
   count with no items is not a backlog, and the two classes run together are a backlog
   nobody can size.

   An **out-of-scope** candidate is routed by whether its transform changes a file in
   `<touched-files>`. One that changes **at least one** is done in the step, and the refactor
   leaf reports it as a `CANDIDATES: in-step | <files> | <transform>` line: a cover leaf
   (`build-develop-prompt.sh cover`, launched through the supervisor and read through
   `$S/cover-outcome.sh`, as the structural pass does) first mutates the code the candidate
   will move; on `COVERED: no` it is recorded with `refactor-owed.sh` as for a test-only one
   (RF20) and not transformed. Its `<bound>` is `<touched-files>` plus the `<files>` that line
   names. When covered, its transform is bounded to `<touched-files>`
   plus the files the candidate names, is checked with `$S/transform-touches-tests.sh
   <green-sha> <bound>` before verify-refactor runs, and counts against the step's budget.
   One that changes **no** file in `<touched-files>`, reported as a
   `CANDIDATES: out-of-bounds | <candidate>` line, is never done in the step: it is
   recorded with `refactor-owed.sh` as `out-of-bounds`, apart from the candidates left to
   the structural pass at the Draft PR.

   Mark the same three figures in the log — the observed count, unclamped,
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
   Each in-step candidate is appended on its own, right after its own cover leaf exits and
   before the next cover leaf is launched, because every cover leaf writes the same
   `.tdd/develop-cover.out` and the next one overwrites it:
   ```
   { printf '%s\n' '<its CANDIDATES: in-step line>'; cat .tdd/develop-cover.out; } | $S/refactor-owed.sh append .tdd/issue-<n>-refactor-owed.md "<STEP>" "$touched"
   ```
   Its input on stdin is the refactor leaf's report `.tdd/develop-refactor.out` once, and, for
   each in-step candidate, that candidate's `CANDIDATES: in-step` line followed by its own cover
   leaf's report. `append` records an in-step candidate exactly when its own cover leaf
   answered `COVERED: no`, and no other in-step candidate.
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
     loop has already closed and no triangulation reopens it. **Before the clear**, run
     `$S/graded-changed.sh <green-sha>` over the refactor leaf's commits: its exit 1 prints each
     graded unit they changed, and the run **bails** with cause `graded-edit-outside-skill-edit`, a
     process failure, naming each unit, with the refactor-pending mark left in place (`Read`
     `<base directory>/BAIL.md`):
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
     malformed — a `<k>` that is not a whole number ≥ 1 — and bails with cause `step-add-refused` (`Read` `<base directory>/BAIL.md`). A criterion no
     ledger step serves yet is no obstacle: the script tags the new step `⟦criterion k⟧` all
     the same. Neither reporting one — no `uncovered-spec` flag
     from the leaf and none in the verdict — is no call and no mark at all.
     **exit 1** is that one call meeting the plan-growth budget: the values are filed as
     owed steps rather than planned — the script's own entry in `SCRIPTS.md` says how — and
     `next-unchecked.sh` never finds them there, so the run does not plan what it recorded.
     Narrate it as the owed steps it is and carry on to the clear below — the step verified
     PASS and the values are recorded; the plan simply did not grow, which is nothing to
     stop a run for. That grown ledger rides the same commit as the clear.
     A clear left uncommitted is not a clear, and a step inserted into a ledger nothing
     commits is a step the next run never sees: resume reads the **committed** ledger, so
     until that commit exists the step still says pending and the plan is still the one the
     leaf grew from. The push copies the step's
     finished state to the remote on the same terms as Green's above: exit **1** launches
     the reconcile leaf (when that happens, `Read` and run `<base directory>/RECONCILE.md`). Exit **2** is a **bail** (`Read` `<base directory>/BAIL.md`).
     **Then run `$S/stop-requested.sh`**, immediately after that push, as Green does after
     its own: on exit 0 any mode it printed goes to *Stopping* here (when that happens, `Read` `<base directory>/STOPPING.md`). On exit 2 go to
     *Stopping* in mode `at-ledger`, narrating that the request was unreadable; on exit 3
     carry on.
     Then **mirror to the issue**:
     post a `### ✅ Step done` comment, then ask whether the step's criterion is finished
     (`$S/criterion-finished.sh <k> < .tdd/issue-<n>.md`, k from the step's `⟦criterion k⟧`):
     on exit **0** tick it in the **issue body** (`$S/tick-issue-criterion.sh <n>
     "$(gh api repos/{owner}/{repo}/issues/<n> -q .body | $S/ledger-steps.sh criterion <k>)"`, the human mirror); on exit **3** tick nothing, since a step serving it is
     still open or pending; on exit **2** the criterion could not be read, so **bail** with cause
     `criterion-unreadable` (a system failure) and never treat it as exit 3 (see `<base directory>/BAIL.md`). Mark
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
     projection: **bail** (`Read` `<base directory>/BAIL.md`). (Earlier steps' commits are preserved.)
   - **REJECT (exit 1):** enter the **revise loop** — when a verifier answers `REJECT`, `Read` `<base directory>/REVISE.md`. On recovered PASS, mirror and loop; on
     budget-exhausted, **bail** (`Read` `<base directory>/BAIL.md`). (Earlier steps' commits are preserved.)
   - **Malformed / killed-stuck (exit 2):** **bail** (`Read` `<base directory>/BAIL.md`). (Earlier steps' commits are preserved.)

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
leaf (see `<base directory>/BAIL.md`). After its wait exits 0 and before the verifier is launched, run `$S/suite-reported.sh develop-diff`:
exit 2 means the leaf left no `SUITE:` line, so launch no verifier and **bail** as a system
failure with cause `report-missing` (`Read` `<base directory>/BAIL.md`). The `diff` revise leaf asks for the line too, so after its wait
exits 0 the same check, `$S/suite-reported.sh revise-diff-<k>` for the `revise-diff-<k>` leaf, runs
before the re-verify with the same exit 2 outcome. The verifier's verdict closes the `⟦diff-checked⟧` step:

- **PASS (exit 0):** tick the `⟦diff-checked⟧` step with `tick-ledger.sh` — without
  `--refactor-pending`, since no refactor loop follows — commit the ledger and push it as
  Green does, post `### ✅ Step done`, then tick its criterion in the issue body with `tick-issue-criterion.sh` on
  `criterion-finished.sh` exit 0, ticking nothing on exit 3, exactly as a Refactor loop's
  PASS does.
- **REJECT (exit 1):** a revise of the `⟦diff-checked⟧` step's `develop-diff` work under
  `REVISE_BUDGET` — when a verifier answers `REJECT`, `Read` `<base directory>/REVISE.md`. On a recovered PASS tick as above, on
  budget-exhausted **bail** (`Read` `<base directory>/BAIL.md`).
- **Malformed / killed-stuck (exit 2):** no verdict on the `⟦diff-checked⟧` step could be
  obtained, so **bail** as a system failure (`no-verdict`) — see `<base directory>/BAIL.md`.

A `⟦fixture-repair⟧` step's verify-green PASS closes it the same way: ticked with
`tick-ledger.sh` without `--refactor-pending`, committed with a `test:` subject, no Refactor
loop run, and its criterion ticked with `tick-issue-criterion.sh` on `criterion-finished.sh`
exit 0, ticking nothing on exit 3, as a `⟦diff-checked⟧` PASS does.

#### A `⟦phases: …⟧` step — each listed phase, a developer leaf then a blind verifier

When `next-unchecked.sh` hands over a step listing `⟦phases: …⟧`, then and not before, in place
of Red, Green and Refactor, `Read` and run `<base directory>/PHASED.md`.

### 4. Draft PR

Reached when `next-unchecked.sh` exits 3 — every ledger step is checked off but the
`⟦full-suite⟧` and `⟦human-owed⟧` lines, which that script skips and no cycle closes: an
unchecked line carrying either does not hold the run back from this step. The full suite
must be green before this step: each time the run enters this step, run `$S/detect-test-command.sh --tier all`'s command via `detach-command.sh` once,
in the same start-then-wait shape as the preflight baseline — the branch's own full-suite gate, since every leaf runs the fast
command, the affected suites, or both. A run that comes back here after a repair step's cycle runs it again. That nothing is left uncommitted and no step is still only
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
git add .tdd/issue-<n>.md .tdd/issue-<n>-added.md
git commit -m "plan: repair the red full suite (#<n>)"
```
That call passes no `--criterion` on purpose: the repair step serves its anchor's criterion.
**`add-ledger-step.sh` exit 2 → bail with cause `step-add-refused`** — see `<base directory>/BAIL.md`.
**`add-ledger-step.sh` exit 1 on the `⟦suite-repair⟧` insertion → bail with cause `suite-red`, naming every suite still red**, exactly as the second-red-run bail below does (`Read` `<base directory>/BAIL.md`).

A second red result on the full run after a repair step does **bail** — the repair step is
one more cycle, not a loop — and the bail names every suite still red, not only the first (`Read` `<base directory>/BAIL.md`).
The cap is one `⟦suite-repair⟧` step per run (a resume starts a new run), and `add-ledger-step.sh`,
not the conductor's judgement, decides it: its exit 1 on the insertion above is the whole answer,
and the conductor does not count repair steps in the ledger itself.
```
VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=suite-red classification="$($S/classify-bail.sh suite-red)" suites='<every suite still red>'
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
   step that is checked but still only green. On either, **do not ready the PR**, and come back
   here only once both questions have gone quiet — an empty status, and
   `next-pending-refactor.sh` exiting 3 — by going to sub-step 2, whose reset runs before its ask and so discards that work whatever the ask answers: now `Read`
   sub-step 2 of `<base directory>/RESUME.md`. For a pending step sub-step 2 also
   re-enters that step's refactor loop. With **no step pending and none unchecked** the
   reset is the whole remedy: sub-steps 2 and 3 both exit 3, sub-step 4's `### ▶️ Resuming`
   comment names the paths the reset discarded, and the run comes back here and readies the
   PR — refusing the same tree for ever is not an outcome, discarding it loudly is.
   Once both have gone quiet, bring the branch up to the default one, which may have moved
   while the run worked:
   ```
   $S/rebase-onto-default.sh
   ```
   `rebase-onto-default.sh`'s exit code decides the next action, so nothing after it — the
   rebased tip's full test run in particular — is started until it has returned, and never in
   the same message as the rebase.
   An exit 3 from `rebase-onto-default.sh` — the branch already contains `origin/<default>` —
   continues unchanged to sub-step 2. An exit 2 from `rebase-onto-default.sh` — no answer
   could be obtained, such as an origin that cannot be fetched — does **bail**, as a
   **system** failure (`no-verdict`), with the PR left a draft (`Read` `<base directory>/BAIL.md`). An exit 0 — the branch was
   behind and the rebase applied cleanly — has changed the tree, and the first line it
   printed is `<pre-rebase-sha>`, the sha the branch held before the rebase. The rebased tip
   is a tree no suite has run on, and two green branches can combine into a red one, so first run
   the regrade block below on it, which re-signs a `GRADED` line the rebase alone made stale, and then run
   the full test command (`$S/detect-test-command.sh --tier all`'s, via `detach-command.sh`) once on the rebased tip,
   in the same start-then-wait shape as the preflight baseline, and read its exit code from `wait`.
   A red result on the rebased tip does **bail**, as a **process** failure
   (`rebased-tip-red`), with the PR left a draft: it is never readied (`Read` `<base directory>/BAIL.md`). Before the bail's push,
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
   ```
   Once the `develop-rebase` leaf has resolved the conflict, run the regrade block below
   **before** `verify-rebase` is launched, so the verifier judges a tip whose `GRADED` lines are
   current. A stale `GRADED` line from the rebase is no defect of the resolution: it spends no
   `revise` mark and no `REVISE_BUDGET` attempt. Then launch the verifier:
   ```
   rm -f .tdd/verdict-rebase.exit .tdd/verdict-rebase.pid
   VERI_TEST_CMD='<test-cmd>' VERI_ISSUE=<n> VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" $S/detach-leaf.sh $S/supervise.sh verdict-rebase $S/run-verdict.sh --step "$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)" rebase .tdd/issue-<n>-spec.md <onto-sha> <pre-rebase-sha> > .tdd/verify-rebase.reason 2> .tdd/verify-rebase.err
   $S/wait-leaf.sh verdict-rebase   # foreground; on exit 3 call it again
   ```
   A verify-rebase `REJECT` goes round the revise loop with phase `rebase`, within
   `REVISE_BUDGET` like any other phase (when a verifier answers `REJECT`, `Read` `<base directory>/REVISE.md`). A malformed verdict does **bail** as a **system**
   failure (`no-verdict`, see `<base directory>/BAIL.md`).
   Only on a verify-rebase `PASS` does the run go on to ready the PR, and first as on exit 0:
   the full test command once on the rebased tip (the regrade having already run before `verify-rebase`), a bail on red (`rebased-tip-red`) with
   `git reset --hard <pre-rebase-sha>` before the bail's push, and on green the push under
   the lease pinned to `<pre-rebase-sha>` (see `<base directory>/BAIL.md`).

   A rebase not resolved within budget — the leaf reports `REBASE: FAILED` or exits 1 or 2,
   a killed leaf among them, or `REVISE_BUDGET` runs out on verify-rebase `REJECT`s — has
   left a resolution no verifier passed on the branch, so first put the branch back where it
   stood:
   ```
   git reset --hard <pre-rebase-sha>
   ```
   The branch is left un-rebased, and the run does **bail** with cause `rebase-unresolved`, a **process** failure, with the PR left a draft, its
   bail comment naming every conflicting file `rebase-onto-default.sh` printed, so the human it hands the conflict to knows where it is (`Read` `<base directory>/BAIL.md`).

   The regrade runs after the run's last rebase and before the full suite runs on the rebased tip, so a `GRADED` line made stale only by the rebase never turns that suite red; with no rebase it runs here, before the PR is readied. It regrades every unit the run signed with `grade-prose.sh` (a unit whose `GRADED` line the branch adds since `git merge-base HEAD origin/<default>`, in a `GRADED` file at any depth of the tree, the repository root's included), and reads the block's exit: exit 1 (a REJECT) is handled as a red full suite is, by appending a repair step; exit 2 (no verdict could be obtained) is a system-failure bail with cause `no-verdict`, never a repair step (see `<base directory>/BAIL.md`). Once a unit's text has been REJECTed, a regrade of the same text (the same signature input) may not re-sign it: only an author run that changes the text, followed by a PASS, may. Once that repair step's cycle closes, the run comes back to this Draft PR step and runs the full suite again, then the rebase and the regrade, as it does after a `⟦suite-repair⟧` step.
   ```
   base=$(git merge-base HEAD origin/<default>)
   git diff "$base" HEAD -U0 -- ':(glob)**/GRADED' | sed -n 's/^+\([^+][^ ]*\) .*/\1/p' | { rc=0; while read -r unit; do
     $S/grade-prose.sh "$(dirname "$unit")/REQUIREMENTS.md" "$unit" </dev/null || { r=$?; [ "$r" -gt "$rc" ] && rc=$r; }
   done
   $S/grade-prose.sh --convert </dev/null || { r=$?; [ "$r" -gt "$rc" ] && rc=$r; }
   exit "$rc"; }
   ```
   After the units the run signed, the block runs `$S/grade-prose.sh --convert` on the tree, so a unit the default branch signed under a formula the branch replaces is re-signed under the tree's before the rebased tip's full suite; its exit is folded into the block's highest exit code.

   Run `$S/refactor-owed.sh list .tdd/issue-<n>-refactor-owed.md` once, before the PR is readied.
   When it prints a candidate (exit 0), then and not before, run the issue's one structural pass:
   `Read` and run `<base directory>/STRUCTURAL.md`. On exit 3 the run never reads it.
   No candidate — `list` exits 3, and a missing `.tdd/issue-<n>-refactor-owed.md` is the
   `list` exit-3 case — skips the pass with no bail: it is marked `stopped=nothing-structural`
   before the PR is readied:
   ```
   VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh structural-pass stopped=nothing-structural
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
   blocked=; $S/pr-ready.sh <pr-number> "$(git rev-parse HEAD)" 2> .tdd/pr-ready.err || { blocked=1; VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=pr-ready-failed classification="$($S/classify-bail.sh pr-ready-failed)"; }
   [ -n "$blocked" ] || $S/wait-ci.sh <pr-url> 540 "" "$(git rev-parse HEAD)" > .tdd/wait-ci.out 2> .tdd/wait-ci.err; ci=$?    # exit 3 → run this line again, in a new Bash call
   grep -F 'conflicts with its base branch' .tdd/wait-ci.err > /dev/null; conflict=$?
   [ "$ci" != 2 ] || [ "$conflict" = 0 ] || VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=ci-timeout classification="$($S/classify-bail.sh ci-timeout)"
   graded=1; [ "$ci" != 2 ] || [ "$conflict" != 0 ] || { $S/rebase-onto-default.sh --graded-only > .tdd/graded-rebase.out; graded=$?; }
   [ "$ci" != 2 ] || [ "$conflict" != 0 ] || [ "$graded" = 0 ] || [ ! -e .tdd/ci-conflict-rebased ] || VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=ci-conflict classification="$($S/classify-bail.sh ci-conflict)"
   [ "$ci" != 1 ] || gh run view <run-id> --log-failed          # a failed check only → its suite and FAIL - line
   [ "$ci" != 1 ] || ! $S/ledger-steps.sh has-mark ci-repair < .tdd/issue-<n>.md > /dev/null || VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=ci-red classification="$($S/classify-bail.sh ci-red)" failed="$(cat .tdd/wait-ci.out)"
   [ "$ci" = 0 ] || [ "$ci" = 2 ] || $S/ledger-steps.sh has-mark ci-repair < .tdd/issue-<n>.md > /dev/null; no_repair=$?
   [ "$no_repair" = 0 ] || { step="$($S/ledger-steps.sh last-done < .tdd/issue-<n>.md)"; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh step-added anchor="$(printf %s "$step")" added=1; }
   [ "$no_repair" = 0 ] || $S/add-ledger-step.sh .tdd/issue-<n>.md after "$($S/ledger-steps.sh last-done < .tdd/issue-<n>.md)" '<fix the CI failure: <suite> — <its FAIL - line>> ⟦ci-repair⟧'
   [ "$no_repair" = 0 ] || { git add .tdd/issue-<n>.md .tdd/issue-<n>-added.md && git commit -m "plan: repair the red CI check (#<n>)"; }
   ```
   That call passes no `--criterion` on purpose: the repair step serves its anchor's criterion.
   **`add-ledger-step.sh` exit 2 → bail with cause `step-add-refused`** — see `<base directory>/BAIL.md`.
   When `pr-ready.sh` exits non-zero, its stderr is kept in `.tdd/pr-ready.err` and the block writes exactly one event, the `pr-ready-failed` bail, and nothing else: `blocked` makes the wait line skip `wait-ci.sh` and leave `ci` at 0, so no CI deadline is started, no `ci-timeout`, `ci-conflict` or `ci-red` bail follows, no `step-added` event, `⟦ci-repair⟧` ledger line or `plan: repair the red CI check` commit is made and no `gh run view` is asked for. The run **bails** as a **system** failure (`pr-ready-failed`, classified by `classify-bail.sh`) with the PR left a draft, the bail comment carrying the text of `.tdd/pr-ready.err` as its last reason (`Read` `<base directory>/BAIL.md`).
   A `ci-timeout` or `ci-red` bail ends the step there, and neither the `done` mark nor the
   `metrics:` commit below follows it (`Read` `<base directory>/BAIL.md`). Otherwise:
   ```
   VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh done pr=<pr-url>
   $S/metrics.sh <n> > .tdd/issue-<n>-metrics.md; metrics=$?
   if [ "$metrics" = 0 ]; then
     git add .tdd/issue-<n>-metrics.md
     git commit -m "metrics: what solving #<n> cost (#<n>)"
   fi
   $S/push-branch.sh
   $S/wait-ci.sh <pr-url> 540 "" "$(git rev-parse HEAD)" > .tdd/wait-ci.out 2> .tdd/wait-ci.err; ci=$?    # exit 3 → run this line again, in a new Bash call
   [ "$ci" != 1 ] || ! $S/ledger-steps.sh has-mark ci-repair < .tdd/issue-<n>.md > /dev/null || VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=ci-red classification="$($S/classify-bail.sh ci-red)" failed="$(cat .tdd/wait-ci.out)"
   [ "$ci" = 0 ] || [ "$ci" = 2 ] || $S/ledger-steps.sh has-mark ci-repair < .tdd/issue-<n>.md > /dev/null; no_repair=$?
   [ "$no_repair" = 0 ] || { step="$($S/ledger-steps.sh last-done < .tdd/issue-<n>.md)"; VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$step" $S/event.sh step-added anchor="$(printf %s "$step")" added=1; }
   [ "$no_repair" = 0 ] || $S/add-ledger-step.sh .tdd/issue-<n>.md after "$($S/ledger-steps.sh last-done < .tdd/issue-<n>.md)" '<fix the CI failure: <suite> — <its FAIL - line>> ⟦ci-repair⟧'
   [ "$no_repair" = 0 ] || { git add .tdd/issue-<n>.md .tdd/issue-<n>-added.md && git commit -m "plan: repair the red CI check (#<n>)"; }
   grep -F 'conflicts with its base branch' .tdd/wait-ci.err > /dev/null; conflict=$?
   [ "$ci" != 2 ] || [ "$conflict" = 0 ] || VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=ci-timeout classification="$($S/classify-bail.sh ci-timeout)"
   graded=1; [ "$ci" != 2 ] || [ "$conflict" != 0 ] || { $S/rebase-onto-default.sh --graded-only > .tdd/graded-rebase.out; graded=$?; }
   [ "$ci" != 2 ] || [ "$conflict" != 0 ] || [ "$graded" = 0 ] || [ ! -e .tdd/ci-conflict-rebased ] || VERI_ISSUE=<n> VERI_ACTOR=conductor $S/event.sh bail cause=ci-conflict classification="$($S/classify-bail.sh ci-conflict)"
   $S/refactor-owed.sh render .tdd/issue-<n>-refactor-owed.md
   gh api -X PATCH repos/{owner}/{repo}/pulls/<pr-number> -f title="<type>: <criterion summary> (#<n>)" -f body="<Closes #<n> — summary: the plan's steps, each a blind-verified R→G→R cycle, ledger committed; followed by the contents of .tdd/issue-<n>-metrics.md (or, when $metrics is not 0, the line 'metrics could not be rendered: metrics.sh exited $metrics' in its place), followed by that render's output, followed by the ledger's ## Owed steps bullets, followed by the conductor's mutation-parity.sh report as the pairs table, followed by its ⟦human-owed⟧ lines and each row that report owes under ## Owed by a human>"
   ```
   **`add-ledger-step.sh` exit 2 → bail with cause `step-add-refused`** — see `<base directory>/BAIL.md`.
   The readied PR's CI is read fail-closed, the way the `merge` skill reads it: an empty
   rollup is never a pass, and a completed check whose conclusion is anything other than
   `SUCCESS`, `NEUTRAL` or `SKIPPED` counts as failed. A pending check never counts as
   green, and the wait is `wait-ci.sh`, one bounded slice per Bash call, given the sha just
   pushed (`git rev-parse HEAD`) so a rollup still reporting the previous head reads as pending: its exit 3 means a
   check is still pending, so call it again in a new Bash call; its exit 2 — a check still
   pending past the deadline its first call recorded, checks still queued `VERI_CI_QUEUE_WAIT` seconds after the first call that saw them queued, or no answer from `gh` — does
   **bail**, with cause `ci-timeout`, rather than waiting on (`Read` `<base directory>/BAIL.md`).
   That deadline is `wait-ci.sh`'s own bound, since the call gives no total-seconds: twice the
   mean of the last 5 completed CI runs, capped at 10 minutes, or 540 s when fewer than 5
   exist or `gh` cannot answer.
   A failed check does not bail: read its run's log with `gh run view <run-id> --log-failed`,
   append a repair step to the ledger whose text quotes the failing suite and its `FAIL -`
   line — or the error line, when the suite died before writing one — commit the ledger, and
   return to step 3, *The cycle loop*, without the `done` mark: the quoted line is that
   step's red evidence, the same way a red full run's repair step is.
   A second red CI result after a CI repair step does **bail**, with cause `ci-red`, the way
   a second red full run does — the repair step is one more cycle, not a loop (`Read` `<base directory>/BAIL.md`).
   A conductor never re-runs a failed CI job — no `gh run rerun`, no re-run of a failed
   check: a red check is answered only by the repair step or the `ci-red` bail above, since
   a re-run can turn a real failure into one that reads as a flake. Re-running a known flake
   is the operator's decision, made outside a run.
   That bail keys on `⟦ci-repair⟧` only: a ledger holding a `⟦suite-repair⟧` step and no
   `⟦ci-repair⟧` step still gets its one CI repair attempt.
   A `wait-ci.sh` exit 2 whose stderr names a conflict — the PR conflicts with its base
   branch, so no workflow will start on it — is not a timeout. The conflict is first offered to
   `$S/rebase-onto-default.sh --graded-only`, which resolves a conflict confined to `GRADED` files
   by unit — the branch's line for each unit it signs, the base's line for every other unit — and
   prints `<pre-rebase-sha>` then the onto sha, or aborts and exits non-zero leaving HEAD where it
   stood. Its exit 0 touches no `.tdd/ci-conflict-rebased` and never spends the run's one rebase: it goes on
   with the regrade block, the full suite once on the rebased tip, the push under the lease pinned
   to the printed `<pre-rebase-sha>`, and the same `wait-ci.sh` line, a red rebased tip taking
   sub-step 1's `rebased-tip-red` bail with its reset (`Read` `<base directory>/BAIL.md`). Its non-zero exit takes the rule unchanged:
   with `.tdd/ci-conflict-rebased` absent, `touch .tdd/ci-conflict-rebased` and rebase onto
   `origin/<default>` once, through the existing rebase path of sub-step 1: `$S/rebase-onto-default.sh`
   (no flag), its `develop-rebase` leaf and rebase verifier (`verify-rebase`) when it conflicts, the
   regrade block and then the full suite once on the rebased tip, and the push under the lease pinned
   to `<pre-rebase-sha>` — then wait for CI again with the same `wait-ci.sh` line; with it present,
   **bail** with cause `ci-conflict`, rather than rebasing again (`Read` `<base directory>/BAIL.md`).
   There too `rebase-onto-default.sh`'s exit code decides the next action, so nothing after it — the
   rebased tip's full test run in particular — is started until it has returned, and never in the
   same message as the rebase. Sub-step 1's own rebase takes no flag and does not change.
   The `metrics:` push starts a CI run of its own on the readied PR, so it is read the same
   way, by `wait-ci.sh` after the push; a red there (exit 1) is a CI-only failure on code
   that was already green, so it appends one `⟦ci-repair⟧` step to the ledger with the same
   `step-added` event a conductor-added step gets, through the same three lines and ledger
   commit as a failed check above, and returns to step 3, *The cycle loop*, to repair it as a
   red full suite is repaired; it bails with cause `ci-red` only when the ledger already holds
   a `⟦ci-repair⟧` step, and exit 2 bails with cause `ci-timeout` (`Read` `<base directory>/BAIL.md`).
   A `wait-ci.sh` exit 2 after the `metrics:` push whose stderr names a conflict takes the same one-rebase path as a conflict at the first CI wait, and bails with cause `ci-conflict` on a second, so the run never waits into `ci-timeout` on it (`Read` `<base directory>/BAIL.md`).
   The `done` mark comes before the render because `metrics.sh` reads it for both the Outcome
   and the issue's wall time: a report rendered before it exists says `unknown` for both. The
   body is rewritten only after the `metrics:` commit is pushed, so it never quotes a file the
   branch does not yet carry. The title drops the `WIP:` prefix step 2.3 opened it with, and
   `gh_pr_ready` (in `veri/github.py`, behind `pr-ready.sh`, never sourced into the conductor's shell) is what turns the run's claim into a review request: a finished run that left
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

A verifier's `REJECT` does not stop the run: `Read` and run `<base directory>/REVISE.md`. It spends `REVISE_BUDGET` revise attempts, **default 2**, before bailing the step (see `<base directory>/BAIL.md`).

## Detecting the test command

Do not pick it by hand. Run `$S/detect-test-command.sh --tier fast --issue <body-file> <repo-root>` (its command goes through `detach-command.sh`)
once, from the target repo's root, with the issue body preflight step 0.3 saved: it prints
the one test command of that tier on stdout and exits 0. On **exit 3** it prints nothing — no
marker it trusts matched — so **bail** with cause `needs-user`, asking the user for the command in the bail comment rather than guessing (`Read` `<base directory>/BAIL.md`).

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
  a blind-verified pin or a bail — never a Green, save on a `⟦replaces-case⟧` step, whose
  pin is followed by the green that deletes exactly the named cases.
- **The committed ledger is the source of truth.** Loop the cycle over its steps until none
  remain; check each step off **atomically with its green commit**; the issue thread only
  **mirrors** the ledger. Never hand-edit the ledger — use `tick-ledger.sh`, or `reorder-ledger-steps.sh` to reorder unchecked steps.
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
  the reason; when a verifier answers `REJECT`, `Read` `<base directory>/REVISE.md`). If it exhausts, **bail** (process failure, see `<base directory>/BAIL.md`). On a **killed-stuck** leaf past
  its retry budget, or an unreadable verdict, **bail** (system failure, see `<base directory>/BAIL.md`). Always preserve
  commits and classify the cause. Never hand-fix the code yourself or loop past the budget.
