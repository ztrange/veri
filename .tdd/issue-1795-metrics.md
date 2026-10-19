### 📊 Metrics — issue 1795

Wall time for the issue: 1134 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1818.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 17 | 15 | 4 | 8 | 1389 | 111810 | 16613 | 0.07 |
| diff | 6 | 3 | 0 | 0 | 148 | 93 | 25 | 48 | 7531 | 651184 | 84787 | 0.35 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 92 | 62 | 14 | 26 | 5026 | 340665 | 59556 | 0.23 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 73 | 46 | 15 | 30 | 3894 | 422329 | 41844 | 0.19 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The four uncalled bash helpers `write_ledger`, `write_refactor_owed`, `expect_widening_names` and `expect_nothing_to_do` are deleted from `skills/tdd/scripts/tests/affected-suites.test.sh`, so no bash definition or call of any of them remains anywhere under `skills/` (the unrelated Python functions named `write_ledger` in `veri/add_ledger_step.py` and `tests/py/test_preserve_attempt.py` are other code and stay); test-only, no production change, the suite still green ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 23 | 7 | 14 | 2035 | 186549 | 28208 | 0.11 | 74 | n/a | n/a | n/a |  |  | full |
| No guard table, roster or workflow comment outside `.tdd/` and `docs/` names `affected-suites.test.sh` any more: `skills/tdd/scripts/tests/no-nested-suites.test.sh` drops its three `mentions_reported affected-suites.test.sh …` cases (#1011, #1138, #538 fixture mentions), and its #538 plant case — a real launch of another suite planted into a copy of a suite is still reported — is re-pointed at another bash suite that stays in the tree, so that guard's coverage is kept; `CLAUDE.md`'s suite counts, if any, match the tree; test-only, no production change ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 37 | 10 | 20 | 2973 | 282678 | 30209 | 0.13 | 84 | n/a | n/a | n/a |  |  | full |
| `skills/tdd/scripts/tests/affected-suites.test.sh` is deleted, so the no-range usage behaviour (exit 2, stderr naming the unresolvable revision `no-range` then the `usage: affected-suites.sh <base>..<head>` line) is pinned by exactly one case, the existing pytest case `test_main_returns_2_with_the_usage_line_for_no_argument_and_names_an_unresolvable_base` in `skills/tdd/scripts/tests/py/test_affected_suites.py`, left unchanged; test-only, no production change, `make test` still green with the suite gone ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 8 | 14 | 2523 | 181957 | 26370 | 0.11 | 77 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s |
| --- | ---: | ---: | ---: | ---: | ---: |
| fast | 7 | 7 | 7 | 6 | 7 |
| affected | 0 | 0 | 0 | 1 | 0 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 29 | 56 | 8920 | 762994 | 101400 | 0.42 |
