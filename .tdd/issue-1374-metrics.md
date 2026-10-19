### 📊 Metrics — issue 1374

Wall time for the issue: 3166 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1796.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 7 | 1 | 2 | 886 | 17463 | 14004 | 0.05 |
| diff | 4 | 2 | 0 | 0 | 321 | 113 | 36 | 70 | 13834 | 1363901 | 109429 | 0.55 |
| red | 2 | 0 | 0 | 0 | 61 | 52 | 13 | 26 | 5503 | 415887 | 38053 | 0.19 |
| pin | 2 | 2 | 0 | 0 | 26 | 18 | 8 | 14 | 2185 | 188603 | 29082 | 0.11 |
| rebase | 2 | 1 | 0 | 0 | 1032 | 35 | 15 | 30 | 3756 | 454318 | 45327 | 0.20 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 735 | 80 | 27 | 52 | 9045 | 771192 | 114735 | 0.45 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 715 | 145 | 46 | 90 | 17119 | 1668980 | 121160 | 0.64 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The dead libraries still on the tree — lib/candidate-line.sh, lib/exit-contract.sh, lib/ledger.sh, lib/main-working-tree.sh, lib/number-in.sh, lib/pid-file.sh, lib/preserve.sh, lib/report.sh, lib/verify-options.sh (leaf-model.sh, leaf-role.sh and session-env.sh are already gone) — are deleted together with the suites whose only subject they were (tests/unit/candidate-line.test.sh, tests/unit/exit-contract.test.sh, tests/unit/ledger.test.sh, tests/main-working-tree.test.sh), and every remaining suite that reads one of them (the pending-mark audit, run_verdict's verify-options comparison, scratch-copy-libs' exit-contract audit) stops reading it, with the fast tier and the affected suites green; no production behaviour changes ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 69 | 21 | 40 | 8991 | 876022 | 69097 | 0.35 | 222 | n/a | n/a | n/a |  |  | full |
| SKILL.md, SCRIPTS.md (whose `tick-ledger.sh` entry still says it ticks through `lib/ledger.sh`'s `ledger_tick`; it names `veri/ledger.py` instead), CLAUDE.md and the guard tables outside `.tdd/` and `docs/` no longer name any of the deleted libraries ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 15 | 30 | 4843 | 487879 | 40332 | 0.20 | 175 | n/a | n/a | n/a |  |  | full |
| A small pytest case fails, naming the file, for any `skills/tdd/scripts/lib/*.sh` that no script, SKILL.md, Makefile line or hook sources or runs and that no remaining bash suite sources, and passes on the tree (the live github.sh, count-line-guard.sh, venv-python.sh, watch.sh, background.sh, missing-argument-exit.sh are not named); it lists a repo directory, so it carries `@pytest.mark.tree_audit("…")` ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 11 | 20 | 4095 | 307707 | 34462 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_comment_class.py — FAILED skills/tdd/scripts/tests/py/test_comment_class.py::test_main_sweeps_the_unit_fixture_guard_and_offline_suites_to_empty_sweepable_reports - the sweep still names the deleted tests/unit/ledger.test.sh (and the c-through-e glob now holds no file), so it reports (2, "") where (0, "") is expected ⟦suite-repair⟧ ⟦criterion 1⟧ | 4 | 2 | 0 | 0 | 0 | 0 | 71 | 25 | 50 | 7349 | 751101 | 78000 | 0.34 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 9 | 10 | 12 | 13 |  |  |  |
| affected | 0 | 46 | 0 | 46 | 0 | 58 | 0 |
| target | 0 | 1 | 0 | 0 |  |  |  |
| all | 497 | 507 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 73 | 142 | 26164 | 2440172 | 235895 | 1.10 |
