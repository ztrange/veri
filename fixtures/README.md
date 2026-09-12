# veri fixtures

Materials to demo `/tdd` end-to-end — on a seeded single-criterion issue and on
a multi-criterion one that exercises the ledger loop, the revise loop and a classified
bail — and to demo the blind verifier in isolation.

- [`demo-project/`](./demo-project) — a minimal, zero-dependency Python target. No
  implementation yet; one trivial passing test keeps the baseline green.
- [`seed-demo-issue.sh`](./seed-demo-issue.sh) — creates the single-criterion fixture
  issue (`slugify(text)`) on a GitHub repo.
- [`demo-verify-red-catch.sh`](./demo-verify-red-catch.sh) — stands up a throwaway copy of
  the demo project, drops in a deliberately **weak** test, and runs the real blind
  `verify-red` against it. A correct verifier REJECTs it (exit 1). No GitHub needed; makes
  one real `claude -p` call (set `CLAUDE_BIN` to a stub for a dry run of the plumbing).
- [`demo-revise-recovers.sh`](./demo-revise-recovers.sh) — shows the **revise loop**
  recovering a step: the real `verify.sh`/`supervise.sh` plumbing is driven with a stub leaf
  that REJECTs the first attempt and PASSes after a supervised revise leaf carries the
  reason forward — recovered within the attempt budget, exit 0. No GitHub, no model call.
- [`seed-demo-multi-issue.sh`](./seed-demo-multi-issue.sh) — creates the **multi-criterion**
  fixture issue (a general `slugify` specified by several triangulating criteria) for
  demoing the loops + ledger rung: a committed plan ledger and one cycle per criterion.
- [`demo-ledger-loop.sh`](./demo-ledger-loop.sh) — deterministic (no model) demo of the
  **loop + resume** primitives: drives the real `next-unchecked.sh`/`tick-ledger.sh` to
  drain a ledger, including a simulated stop-and-resume from the next unchecked step.
- [`demo-classified-bail.sh`](./demo-classified-bail.sh) — deterministic demo of the
  **classified bail**: for each forced cause it runs the real `classify-bail.sh` and renders
  the bail comment, showing a plumbing failure is labelled `system`, a methodology failure
  `process`, and an unknown cause errors rather than mislabelling.

## Running the demo

The conductor reads a GitHub issue, pushes a branch, and opens a draft PR, so the demo
runs against a real GitHub repo with push access. Use a throwaway repo:

1. **Stand up a target repo** from the demo project:
   ```sh
   cp -r fixtures/demo-project /tmp/veri-demo && cd /tmp/veri-demo
   git init && git add -A && git commit -m "chore: seed demo project"
   gh repo create veri-demo --private --source=. --push
   ```
   Make the `tdd` skill invocable there. Nothing is copied: install it once,
   user-level, as a symlink to the veri clone (the README's *Install* section), or for a
   one-off symlink it into the target's own `.claude/skills/`:
   ```sh
   mkdir -p .claude/skills && ln -s <veri-repo>/skills/tdd .claude/skills/tdd
   ```
   The conductor's preflight then writes the `.tdd` ignore rule into the target's
   `.gitignore` on the first run (`ensure-run-state-ignored.sh`), so leaf logs never land
   in the demo repo's history.

2. **Seed the fixture issue** on that repo:
   ```sh
   <veri-repo>/fixtures/seed-demo-issue.sh   # prints the new issue URL/number
   ```

3. **Run the conductor** from a Claude Code session in `/tmp/veri-demo`:
   ```
   /tdd <n>
   ```

## What you should observe

- A `tdd/<n>-demo-add-a-slugify...` branch is created.
- The issue thread carries a start comment, then for each phase a developer-phase comment
  (🔴 Red, 🟢 Green, 🛠️ Refactor) **followed by its blind verdict** (🔎 verify-red /
  verify-green / verify-refactor — PASS|REJECT + reason), and a final ✅ Done comment with
  the PR link.
- The full suite (`python3 -m unittest discover -q`) is green before the commits.
- A **draft** PR exists, linked with `Closes #<n>`, **not merged**.
- A `REJECT` does not stop the run: it enters the bounded revise loop (`REVISE_BUDGET`,
  default 2), and each attempt is mirrored as a ♻️ Revise comment carrying the verifier's
  reason verbatim. Only an exhausted budget — or a killed-stuck leaf, or an unreadable
  verdict — **bails**, and then you get a ⛔ Bailed comment naming the phase and
  classifying the cause as a **system** or **process** failure, with every completed
  step's commit preserved on the pushed branch and no PR opened.

## Demoing the blind verifier alone

To see verification catch bad work without a full GitHub run:

```sh
fixtures/demo-verify-red-catch.sh   # expect: REJECT (exit 1)
```
