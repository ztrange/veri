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

Beside the conductor sits **`/tdd-fix <one-line description>`**, the way a bug gets filed so
that a later `/tdd <n>` can read it: it asks only for what that line left out, opens the
issue with the headings the conductor's spec capture copies, labels it `bug` and
`ready-for-agent`, and then asks once whether to start the fix run.

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

veri is a Claude Code skill, not an application. Install it once, user-level, as a symlink
to this clone — then `/tdd <n>` works from any repo on the machine:

```sh
ln -s "$(pwd)/skills/tdd" ~/.claude/skills/tdd
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
