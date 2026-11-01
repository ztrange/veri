# veri

A Claude Code skill suite that solves GitHub issues by strict **TDD/XP** discipline.

veri takes a GitHub issue, plans the work, and drives it through Red → Green → Refactor
cycles — but with a twist that gives the suite its name: **every test is verified by a
blind, independent agent.** A separate leaf, given only the test and the issue spec (never
the author's reasoning), runs the test itself to confirm it genuinely fails for the right
reason, and later that it genuinely passes. Verification can't rubber-stamp the work
because it never sees the work's justification.

## How it works

A **conductor** (`/tdd <number>`) drives one issue end-to-end. It owns no coding
itself — it launches short-lived `claude -p` **leaves** through a **supervisor** that
watches each leaf's heartbeat and kills/retries/escalates anything that hangs. Control
over a stuck agent is a first-class property, not an afterthought.

```
/tdd <n>
  ├─ baseline: git repo? suite green? clean tree? gh authed?
  ├─ worktree: .tdd/wt/<n> on tdd/<n>-slug (your checkout is not switched)
  ├─ scope-and-plan → ledger (.tdd/issue-<n>.md)  +  mirror plan to the issue
  └─ loop over plan steps:
        red            (dev: one failing test)
        verify-red     (blind: runs it · right-reason fail? quality?)
        green          (dev: minimum impl)
        verify-green   (blind: runs test + suite · genuine pass?)
        ✓ green commit (ledger checked off atomically)
        refactor loop  (one behavior-preserving transform, suite-gated, until none)
        verify-refactor(blind, once: suite green + up to standard)
        refactor commit
        mirror cycle outcome to the issue
  └─ done → push → draft PR (Closes #n)
```

A `REJECT` verdict triggers a **bounded revise loop** (≤2 attempts) before escalating. On
**bail**, completed cycles are preserved, the branch is pushed, and a diagnostic comment is
posted to the issue that classifies the cause as a **system** failure (plumbing broke) or a
**process** failure (methodology spoke).

Beside the conductor sits **`/vfile bug|refactor|feature [<one line>]`**, the way an issue gets
filed so that a later `/tdd <n>` can read it: it asks only for what that line left out and
opens the issue with the headings the conductor's spec capture copies. Before an issue
exists, **`/vplan`** turns an idea into a PRD of small sub-PRDs, each one sized for a
single `/tdd` run.

## Design principles

- **Generality comes from triangulation, never from hand-written code.** Each acceptance
  criterion is a failing test; refactor is strictly behavior-preserving.
- **The local ledger is the source of truth** (committed atomically with each cycle); the
  GitHub issue thread is the human-facing mirror.
- **Branch per issue → draft PR; a human always merges.** veri never auto-merges.

## Scope ladder

veri grows in three rungs, each wrapping the previous — never a rewrite:

1. **Single issue** — solve one named issue end-to-end.
2. **Loop** — drain all *solvable* issues (dependencies closed), one after another.
3. **Parallel** — several conductors at once (the per-issue worktree, already in place, is
   what keeps them apart).

## Install

veri is a Claude Code skill, not an application. One skill, `vinstall`, is installed once,
user-level, as a symlink to this clone — then `/vinstall` links the skills you type into each
project, as ignored symlinks:

```sh
ln -s "$(pwd)/skills/vinstall" ~/.claude/skills/vinstall
```

The skill locates its own scripts from the base directory Claude Code reports when it
loads, so nothing is copied into a target repo. On the first run against a repo the
conductor's preflight writes the `.tdd` ignore rule into that repo's `.gitignore`
(`ensure-run-state-ignored.sh`, idempotent) so leaf logs and prompts never enter history;
only the per-issue ledger is committed. Preflight also refuses to start unless `gh` and
the `claude` CLI are both authenticated.

Preflight infers the target repo's full-suite test command from what the repo committed —
a `package.json` test script, a `Makefile` `test` target, pytest config, `go.mod`,
`Cargo.toml`. When that inference is wrong, put a `.veri/test-command` file in the target
repo: its first non-empty line is run verbatim as the full suite, ahead of every
inference. That file is the per-repo escape hatch; without it, a repo veri cannot read is
asked about rather than guessed at.

The `veri: all tests` command must be the project's whole merge gate: a run's full suite is
never a subset of what the merge checks, or a run can report green and still fail the gate.

The run does not switch your checkout. The issue branch is checked out in a **linked git
worktree** at `.tdd/wt/<n>` inside the target repo (created by `issue-worktree.sh`, cut
from the default branch, sharing the one object store), and everything — spec, ledger, leaf
logs, commits, push, PR — happens in there. The directory you launched from stays on the
branch it was on, so a skill symlinked out of it or a dev server serving it never silently
starts seeing the issue branch. The worktree is left in place after the draft PR, because a
resume lands back in it; once the PR is merged, retire it with
`skills/tdd/scripts/issue-worktree.sh --remove <n>`, which refuses to remove one
that still holds uncommitted work.

`/tdd <scope>` (rung 2) drains a backlog instead of one named issue — any argument that is
not an integer names a **scope**, and bare `/tdd` means the `plain` one: it asks
`solvable-issues.sh` which issues veri may take, runs the conductor on the
first, then **asks again** — a finished issue's draft PR now `Closes` it, and closing its
dependencies may have freed others, so the set is recomputed every iteration rather than
walked from a stale list. An issue is taken only if it is open, carries the
**`ready-for-agent`** label — the human's explicit opt-in, since nothing is taken because
it merely exists — every issue under its **`## Blocked by`** heading is closed, and no open
PR already says `Closes #<n>` for it. The scope picks that label: `plain` is the bare
`ready-for-agent`, any other scope is `ready-for-agent:<scope>`, and `VERI_LABEL` still
overrides it outright. The intended use is partitioning — **one label per loop**,
so two loops running against the same repository drain disjoint pools instead of racing for
the same issues. The first bail stops the loop unless you pass
`--continue-on-bail`, `VERI_MAX_ISSUES` caps an invocation (default: no cap), and the loop
adds no failure mode of its own — every outcome is a single-issue outcome, and the
committed ledgers make an interrupted run resumable by invoking `/tdd <scope>` again.

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
hand, and `skills/tdd/scripts/run-conductor.sh <n>`, which builds that same command line — the procedure as
the prompt, the streaming flags, `--permission-mode bypassPermissions`, and the parent
session's handles severed, plus `--model opus` (or `--model $VERI_MODEL_CONDUCTOR` when that variable is set and non-empty; unset or empty means Opus) — and is what an unattended or scheduled launch should call.

**Interactive or print mode is a trade you pick per run.** An interactive conductor can be
steered — asked a question, redirected, interrupted mid-run — and costs ~25,000 tokens a
request more, the harness surface an interactive session re-sends on every request (#207,
recorded at `run-conductor.sh:7`). A print-mode conductor is that much cheaper per request,
and cannot be steered: there is no human on the other end of its turn, so every decision the
procedure would put to an operator becomes a bail instead — it stops and says why, and you
read that afterwards rather than answering it at the time.

**The skill snapshot: a run executes one skill from its first launch to its last.**
`skills/tdd/scripts/run-conductor.sh <n>` does not run the skill as it sits in the clone. It fetches `origin`,
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

**Disk: a per-launch `TMPDIR`, and a free-space check.** `run-conductor.sh` starts the conductor
with `TMPDIR` set to a fresh `veri-run-<n>-…` directory inside the inherited one, so whatever a
project's tests leave in `os.tmpdir()` goes with it: the directory is removed when the conductor
exits (any exit code) and on SIGTERM, SIGINT or SIGHUP. Its path and the launcher's pid are
recorded in `.tdd/issue-<n>-tmpdir-skill-commit`; a launcher killed outright leaves the directory, and the next
`run-conductor.sh` start for any issue removes each recorded `veri-run-*` directory whose pid no
longer answers `kill -0` — never a live owner's, one with no record, or one outside the inherited
`TMPDIR`; an unreadable record is left alone and named on stderr. `VERI_MIN_FREE_GB` (default
20, a whole number >= 0, `0` disables) is the free space, in GB, that the filesystems holding the
inherited `TMPDIR` and the repository must each have before launch; below it the launch is exit 2,
naming the path, the free GB and the variable, and so is a value that is not a whole number >= 0.

**The record survives only a run that got past preflight.** After the conductor exits,
`run-conductor.sh` keeps `.tdd/issue-<n>-skill-commit` when `.tdd/wt/<n>` is registered as a
git worktree or a local `tdd/<n>-*` branch exists — what step 1.2, the first thing after
preflight, creates — and removes it otherwise, whatever the conductor's exit code. An
unregistered `.tdd/wt/<n>` directory, such as the one `VERI_NEW_SKILL=1` leaves, does not
count. So a launch that stopped at preflight pins nothing, and the next launch takes the
fresh tip.

When no commit can be resolved at all the launch runs unpinned, says so on stderr, and hands
the conductor `VERI_SKILL_UNPINNED=1` for the plan comment (step 2.4).

## Documentation

- [`docs/walkthrough.html`](./docs/walkthrough.html) — **veri, Annotated**: every one of
  the conductor's scripts in full, source beside commentary, ordered by the data flow of one
  cycle. Bash constructs in the commentary carry a hover gloss and link into a reference
  section covering every construct the suite uses. The page is **generated** from the real
  scripts by `docs/build-walkthrough.py` (`make docs`), so the source it shows cannot
  drift; `make docs-check` verifies the committed page still matches. Published at
  <https://ztrange.github.io/veri/> by hand-running `.github/workflows/pages.yml`, so a
  deploy is a decision rather than a side effect of a merge.
- [`CONTEXT.md`](./CONTEXT.md) — the domain glossary (ubiquitous language) and scope ladder.
- [`docs/adr/`](./docs/adr/) — Architecture Decision Records 0001–0016, one per resolved
  design fork.

## Status

Rung 1 of the scope ladder — **single issue, end to end** — is complete. The
`/tdd` conductor (`skills/tdd/`) decomposes an issue into a
committed ledger and loops it through Red → Green → Refactor, writing no code itself:
every phase is a short-lived `claude -p` leaf launched through the supervisor, and every
phase is confirmed by a blind independent verifier that runs the test itself. A `REJECT`
enters the bounded revise loop; a hang or an unreadable verdict bails, preserving
completed commits and classifying the cause as system or process. Runs are resumable from
the ledger, and finish on a draft PR.

Shipped: the walking skeleton (#2), blind verification (#3), supervised leaves (#4),
retries (#5), loops + ledger (#6), hardened edges (#7), bounded stuck-retry (#12),
streaming heartbeat (#14), deterministic bail classification (#18), the run-state
ignore guard that makes a target repo safe to run in (#27) and the *already satisfied*
step outcome — a blind verify-pin instead of a doomed red (#31).

Rung 2 of the [scope ladder](./CONTEXT.md) is `/tdd <scope>` (#41): drain every
*solvable* issue one after another. Next: rung 3, several conductors in parallel, each in
its own worktree (#43 laid the ground). Demo materials live in [`fixtures/`](./fixtures).
