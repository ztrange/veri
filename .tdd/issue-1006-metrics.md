### 📊 Metrics — issue 1006

Wall time for the issue: 10448 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1304.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 18 | 10 | 1 | 2 | 1166 | 12193 | 43636 | 0.19 |
| diff | 13 | 5 | 2 | 0 | 6279 | 276 | 77 | 150 | 25873 | 3649660 | 598476 | 4.56 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 6 | 2 | 0 | 3830 | 119 | 32 | 62 | 11777 | 1337481 | 354141 | 1.67 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 2467 | 167 | 46 | 90 | 15262 | 2324372 | 287971 | 3.07 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 5099 | 2.31 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Extract Function: `skills/tdd/scripts/veri/ledger_steps.py` gains `current_or_last_done(records)` — `current`'s answer, or `last_done`'s when `current` has none, exit 3 only when both are — wired as a fourth verb `current-or-last-done` that reads stdin once; `USAGE` (`ledger_steps.py:7`) and the shim's header comment (`ledger-steps.sh:4`, plus a line describing the verb) name it; new cases in `skills/tdd/scripts/tests/py/test_ledger_steps.py` and, through the entry point, in `skills/tdd/scripts/tests/ledger-steps.test.sh` pin that it prints what `current` prints when a step is open, what `last-done` prints when every step is ticked, and exits 3 with nothing on stdout for a ledger with no step; the only existing lines changed are the pinned usage line at `tests/ledger-steps.test.sh:40` and `tests/py/test_ledger_steps.py:8`, which become the new `USAGE`, so `ledger-steps.sh bogus` still exits 2 with that one usage line. Predicate: `[ "$(printf -- '- [x] a\n- [ ] b\n' | skills/tdd/scripts/ledger-steps.sh current-or-last-done)" = b ] && [ "$(printf -- '- [x] a\n' | skills/tdd/scripts/ledger-steps.sh current-or-last-done)" = a ] && skills/tdd/scripts/ledger-steps.sh bogus </dev/null 2>&1 | grep -F 'current-or-last-done' >/dev/null` ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 53 | 13 | 26 | 6218 | 721182 | 104622 | 0.89 | 349 | n/a | n/a | n/a |  |  | full |
| Extend Test Double: the stub `ledger-steps.sh` that `skills/tdd/scripts/tests/skill-leaf-env.test.sh`'s `scan_current_step_title` plants (`:561-563`) answers `current-or-last-done` exactly as it answers `current`, still exiting 2 on any other verb; and `skills/tdd/scripts/tests/skill-leaf-launch.test.sh`'s `ledger_read_re` (`:223`) admits `ledger-steps.sh current-or-last-done` as a ledger read a blind verifier launch may carry; no assertion changes, `scan_inline_ledger_reads` (`skill-leaf-env.test.sh:921-931`) is not loosened, and both suites stay green against today's SKILL.md. Predicate: `grep -F 'current-or-last-done' skills/tdd/scripts/tests/skill-leaf-env.test.sh >/dev/null && grep -F 'current-or-last-done' skills/tdd/scripts/tests/skill-leaf-launch.test.sh >/dev/null` ⟦diff-checked⟧ ⟦criterion 3⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 61 | 20 | 40 | 6354 | 915537 | 174691 | 1.31 | 830 | 1/2 | unknown | unknown |  |  | full |
| Substitute Algorithm: every one of the 19 `skills/tdd/SKILL.md` lines spelling `$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current || { cat .tdd/issue-<n>.md | $S/ledger-steps.sh last-done; })` reads `$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current-or-last-done)` instead, every other character of each line unchanged — the general verifier launch, develop-rebase, verify-rebase and verify-transform, revise mark, revise leaf, re-verify, revise-diff, revise-exhausted, reconcile, bail, stop and resume blocks — so each line hands the same step text to the same leaf, verifier, event or prompt builder for a ledger with an open step and for one with every step ticked, and `tests/skill-leaf-env.test.sh` and `tests/skill-leaf-launch.test.sh` pass with their `stage_recorder … -last-done` cases unchanged. Predicate: `! git grep -nE 'ledger-steps\.sh current *\|\|' skills/tdd/SKILL.md && [ "$(git grep -o 'ledger-steps\.sh current-or-last-done' skills/tdd/SKILL.md | wc -l | tr -d ' ')" -ge 22 ]` ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 37 | 12 | 20 | 3804 | 458408 | 87248 | 0.66 | 646 | n/a | n/a | n/a |  |  | full |
| across the branch, the only edits to files under `skills/tdd/scripts/tests/` are new cases plus the three named edits — the `scan_current_step_title` stub in `skill-leaf-env.test.sh`, `ledger_read_re`/`last_done_re` in `skill-leaf-launch.test.sh`, and the pinned usage line in `ledger-steps.test.sh` and `py/test_ledger_steps.py` — and no assertion changes (`git diff origin/main...HEAD -- skills/tdd/scripts/tests/`) ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 37 | 10 | 20 | 3292 | 468957 | 92576 | 0.69 | 290 | n/a | n/a | n/a |  |  | full |
| fix the full-suite failure: orchestrate.test.sh — FAIL - #1126 a conductor orchestrate.sh stops over VERI_CONDUCTOR_CTX_BUDGET is stopped by SIGTERM to its process group: a writer in it on the conductor's stdout ends 143, never 141 of SIGPIPE (got writer 141). It passed 28/28 three times rerun alone, and this branch touches neither orchestrate.sh nor its suite, so `make test` must be green on the branch with no edit to orchestrate.test.sh or any other test file beyond those criterion 3 names ⟦suite-repair⟧ ⟦diff-checked⟧ ⟦criterion 3⟧ | 3 | 1 | 1 | 0 | 0 | 0 | 88 | 22 | 44 | 6205 | 1085576 | 139339 | 1.00 | 5457 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 103 | 97 | 85 | 77 | 74 | 1134 |
| affected | 5 | 75 | 91 | 88 | 338 | 53 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 78 | 152 | 27039 | 3661853 | 642112 | 4.74 |
