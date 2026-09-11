# veri

A Claude Code skill suite that solves GitHub issues by strict **TDD/XP** discipline.

veri takes a GitHub issue, plans the work, and drives it through Red → Green → Refactor
cycles — but with a twist that gives the suite its name: **every test is verified by a
blind, independent agent.** A separate leaf, given only the test and the issue spec (never
the author's reasoning), runs the test itself to confirm it genuinely fails for the right
reason, and later that it genuinely passes. Verification can't rubber-stamp the work
because it never sees the work's justification.

## How it works

A **conductor** (`/solve-issue <number>`) drives one issue end-to-end. It owns no coding
itself — it launches short-lived `claude -p` **leaves** through a **supervisor** that
watches each leaf's heartbeat and kills/retries/escalates anything that hangs. Control
over a stuck agent is a first-class property, not an afterthought.

```
/solve-issue <n>
  ├─ baseline: git repo? suite green? clean tree? gh authed?
  ├─ branch:   tdd/<n>-slug
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
3. **Parallel** — several conductors at once (git worktree per issue branch).

## Install

veri is a Claude Code skill, not an application. Install it once, user-level, as a symlink
to this clone — then `/solve-issue <n>` works from any repo on the machine:

```sh
ln -s "$(pwd)/skills/solve-issue" ~/.claude/skills/solve-issue
```

The skill locates its own scripts from the base directory Claude Code reports when it
loads, so nothing is copied into a target repo. On the first run against a repo the
conductor's preflight writes the `.tdd` ignore rule into that repo's `.gitignore`
(`ensure-run-state-ignored.sh`, idempotent) so leaf logs and prompts never enter history;
only the per-issue ledger is committed. Preflight also refuses to start unless `gh` and
the `claude` CLI are both authenticated.

## Documentation

- [`docs/walkthrough.html`](./docs/walkthrough.html) — **veri, Annotated**: every one of
  the twelve scripts in full, source beside commentary, ordered by the data flow of one
  cycle. Bash constructs in the commentary carry a hover gloss and link into a reference
  section covering every construct the suite uses. The page is **generated** from the real
  scripts by `docs/build-walkthrough.py` (`make docs`), so the source it shows cannot
  drift; `make docs-check` verifies the committed page still matches.
- [`CONTEXT.md`](./CONTEXT.md) — the domain glossary (ubiquitous language) and scope ladder.
- [`docs/adr/`](./docs/adr/) — Architecture Decision Records 0001–0012, one per resolved
  design fork.

## Status

Rung 1 of the scope ladder — **single issue, end to end** — is complete. The
`/solve-issue` conductor (`skills/solve-issue/`) decomposes an issue into a
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

Next: rung 2 of the [scope ladder](./CONTEXT.md) — drain every *solvable* issue (its
dependencies closed) one after another — then rung 3, several conductors in parallel over
git worktrees. Demo materials live in [`fixtures/`](./fixtures).
