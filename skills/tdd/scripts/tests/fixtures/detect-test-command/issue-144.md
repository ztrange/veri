## Parent

Leaf cost thread. Follows #121 (the leaf timeout is sized from the baseline run) and #120/#131 (an issue's `Test command:` line). Those made a slow suite *survivable* for a leaf. This issue makes a leaf run the slow suite *fewer times*.

## Problem

Every developer prompt hands the leaf `{{TEST_CMD}}` and says to run the **full suite** with it:

- `develop-red.md:28` runs the one new case "with the test command above", which is the whole suite.
- `develop-green.md` step 2 runs the full suite.
- `develop-refactor.md:31` runs the full suite after **each** transform.

The blind verifiers run it again: `verify-green.md:15` and `verify-refactor.md` check 1. Leaves also often run it twice, once to look and once to confirm.

Measured from the leaf transcripts of the overnight runs on 2026-09-13, 00:15–06:40 local. Full-suite runs per phase:

| phase | #107 (`make test`, median 65 s) | #137 (`make docs-test`, median ~295 s) |
|---|---|---|
| develop-red | 25 runs / 12 leaves: 30 min | 6 / 5: 13 min |
| develop-green | 12 / 11: 13 min | 7 / 5: 34 min |
| verify-green | 18 / 11: 20 min | 8 / 5: 25 min |
| develop-refactor | 75 / 55: 84 min | 28 / 23: 128 min |
| verify-refactor | 18 / 12: 16 min | 9 / 4: 24 min |
| **all leaves** | **154 runs: 168 of 358 leaf-min (47%)** | **60 runs: 230 of 374 leaf-min (61%)** |

Neither run finished overnight: #107 reached 12/13 steps, #137 reached 5/7.

- **Refactor is the biggest item.** `VERI_REFACTOR_BUDGET` defaults to 5 since #106, so one step can run the full suite up to six times back to back: five transforms, then verify-refactor.
- **Red needs almost none of it.** The only question Red answers is whether one case fails against unmodified code.

The two runs also shared the machine. That is part of why `make docs-test` took ~5 min and `make docs` took 3.7 min instead of ~16 s. Every duplicate run slows the other conductor too.

## What to build

The full suite runs where the guarantee lives: once in develop-green before it reports, and in the two blind verifiers. Everywhere else, a leaf runs **the suite it touched**.

- **develop-red**: run the suite file that holds the new case, not `{{TEST_CMD}}`. If the repository has no way to run one file, fall back to the test command and say so in the report.
- **develop-green**: iterate on the target case's suite. Run the full suite **once**, right before reporting `SUITE:`.
- **develop-refactor**: after its one transform, run the suites covering the touched files, not the full suite.
  - verify-refactor still runs the full suite on the settled result.
  - The trade-off, stated in the prompt and the commit body: a break in a suite nobody touched now surfaces at verify-refactor, not at the transform that caused it. It becomes a REJECT → revise, not a revert inside the loop. "One transform, so a break is attributable" still holds for every suite the transform could plausibly break.
- **verify-green / verify-refactor**: unchanged. They keep "run the project's full test suite". That is the blind guarantee, and this issue must not weaken it.
- **Every leaf that runs a suite**: run it in the foreground and report only after it exits. A #137 refactor leaf exited with its `make docs-test` still running in the background, and the conductor re-ran it (~5 min).
- **How a leaf runs one suite:** the leaf establishes it by reading the repository, the same way `_develop-shared.md` rule 1 already has it establish conventions. For veri itself, a suite is an executable `skills/tdd/scripts/tests/<name>.test.sh`. No new script parameter is needed, so the verifier stays blind: `build-verify-prompt.sh`'s arguments do not change.

## Acceptance criteria

- [x] The built `develop-red` prompt tells the leaf to run the suite holding its new case, and does not tell it to run the full suite
- [x] The built `develop-green` prompt says to iterate on the target case's suite and to run the full suite exactly once, before the `SUITE:` report line
- [x] The built `develop-refactor` prompt says to run the suites covering the touched files after the transform, not the full suite, and names verify-refactor as where the full suite runs
- [x] The built `verify-green` and `verify-refactor` prompts still require the project's full test suite. A test pins this, and has been watched to fail with the sentence removed
- [x] Every built developer prompt says to run test commands in the foreground and report only after they exit
- [x] `build-verify-prompt.sh` accepts the same arguments as before (no new parameter reaches a verifier)
- [x] `SKILL.md`, where it describes each phase's leaf, and CLAUDE.md, if it describes suite runs, say which leaves run the full suite

## Notes

- **Files:** `skills/tdd/scripts/prompts/develop-red.md`, `develop-green.md`, `develop-refactor.md`, `_develop-shared.md`, possibly `develop-revise.md`; `skills/tdd/scripts/tests/build-develop-prompt.test.sh`, `build-verify-prompt.test.sh`; `skills/tdd/SKILL.md`.
- **Out of scope:**
  - The refactor budget itself (#106's default of 5). It multiplies this cost but is a separate knob on the cost axis.
  - Speeding up `make docs-test`.
  - Running two conductors at once.
- **Expected effect, an estimate and not measured:** about 3 full-suite runs per step instead of ~13 (#107) or ~12 (#137), plus targeted suite runs that are seconds on `make test`. `build-guards.test.sh` alone takes up to ~4 min, so a #137-style docs issue saves less.

Test command: make test

## Blocked by

None.
