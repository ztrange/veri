### 📊 Metrics — issue 1721

Wall time for the issue: 3407 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 9 of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1746.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 8 | 1 | 2 | 1016 | 0 | 30529 | 0.09 |
| red | 19 | 8 | 0 | 0 | 410 | 311 | 100 | 198 | 35113 | 2862160 | 431517 | 1.83 |
| green | 20 | 7 | 2 | 0 | 1812 | 363 | 123 | 248 | 32081 | 3683177 | 354466 | 1.98 |
| refactor | 14 | 7 | 0 | 0 | 278 | 91 | 43 | 82 | 8385 | 1038526 | 206338 | 0.70 |
| pin | 2 | 2 | 0 | 0 | 50 | 32 | 10 | 20 | 3028 | 276226 | 29470 | 0.13 |
| exhausted | 1 | 0 | 0 | 0 | 25 | 21 | 3 | 6 | 924 | 74852 | 12489 | 0.10 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 27 | 25 | 2 | 0 | 1578 | 311 | 105 | 210 | 29149 | 2734781 | 439646 | 1.75 |
| developer | claude-sonnet-5-5 | 22 | 0 | 0 | 0 | 623 | 309 | 121 | 238 | 35576 | 3571586 | 451745 | 1.84 |
| developer | claude-opus-5-5 | 8 | 0 | 0 | 0 | 384 | 206 | 54 | 108 | 15822 | 1628574 | 173418 | 1.24 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 37 | 0.14 |
| green | 149 | 0.27 | 292 | 0.71 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 25 | 0.10 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `run-finished.sh <issue>` for an issue with no run under `.tdd/wt/` exits 2 and says on stderr that there is no run for that issue; the new script (a `/bin/sh` shim over a `veri/` module, as `status.sh` is) has a no-argument usage line with exit 2 and a declared caller, so the repo-wide audits stay green ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 100 | 31 | 62 | 8275 | 922543 | 106530 | 0.52 | 586 | unknown | 0/5 | nothing-left |  |  | full |
| `run-finished.sh <issue>` exits 0 and prints nothing when the run's state is `done` as `status.sh` reports it, the ledger in the run's worktree has no unchecked step and no `⟂ refactor pending` mark, and the run's PR body has no unticked `⟦human-owed⟧` line ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 54 | 14 | 28 | 5594 | 457266 | 39846 | 0.20 | unknown | unknown | unknown | unknown |  |  | pin |
| When the run's state as `status.sh` reports it is not `done`, `run-finished.sh <issue>` exits 1 and prints the line `not-done <state>` ⟦criterion 2⟧ | 7 | 1 | 1 | 0 | 0 | 0 | 170 | 51 | 102 | 14092 | 1552102 | 137460 | 0.95 | unknown | 2/2 | unknown | unknown |  |  | full |
| When the run's state as `status.sh` reports it is not `done`, `run-finished.sh <issue>` exits 1 and prints the line `not-done <state>` Build any scratch git repository in the suite with the harness's `new_repo`, never a bare `git init` (`tests/unit/no-report-copies.test.sh` refuses it). ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 74 | 31 | 60 | 7520 | 823236 | 127806 | 0.48 | 265 | unknown | 0/5 | nothing-structural |  |  | full |
| When the run's ledger has an unchecked step, `run-finished.sh <issue>` exits 1 and prints one `unchecked <step>` line per unchecked step Build any scratch git repository in the suite with the harness's `new_repo`, never a bare `git init` (`tests/unit/no-report-copies.test.sh` refuses it). ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 69 | 26 | 52 | 7481 | 735164 | 90759 | 0.38 | 214 | unknown | 0/5 | nothing-left |  |  | full |
| When a ledger step still carries `⟂ refactor pending`, `run-finished.sh <issue>` exits 1 and prints one `refactor-pending <step>` line per such step Build any scratch git repository in the suite with the harness's `new_repo`, never a bare `git init` (`tests/unit/no-report-copies.test.sh` refuses it). ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 61 | 26 | 52 | 7347 | 739451 | 92086 | 0.38 | 182 | unknown | 0/5 | nothing-left |  |  | full |
| When the run's PR body holds an unticked `⟦human-owed⟧` line, `run-finished.sh <issue>` exits 1 and prints one `human-owed <line>` line per unticked line; several unmet conditions together each print their own line Build any scratch git repository in the suite with the harness's `new_repo`, never a bare `git init` (`tests/unit/no-report-copies.test.sh` refuses it). ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 69 | 26 | 52 | 7502 | 736841 | 91093 | 0.38 | 197 | unknown | 0/5 | nothing-left |  |  | full |
| When the run's PR body cannot be read (no PR found, or the GitHub read fails), `run-finished.sh <issue>` exits 2 and says on stderr that the PR body could not be read Build any scratch git repository in the suite with the harness's `new_repo`, never a bare `git init` (`tests/unit/no-report-copies.test.sh` refuses it). ⟦criterion 3⟧ | 9 | 3 | 1 | 0 | 0 | 0 | 125 | 36 | 72 | 11029 | 997414 | 139892 | 0.74 | 350 | red 1/2, green 1/2 | 0/5 | nothing-left |  |  | full |
| `run-finished.sh <issue>` writes nothing: after a run of it no file in the repository has changed, and every GitHub call it makes is a read (no POST, PATCH, PUT or DELETE) Build any scratch git repository in the suite with the harness's `new_repo`, never a bare `git init` (`tests/unit/no-report-copies.test.sh` refuses it). ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 37 | 11 | 22 | 4539 | 330497 | 36902 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| fix the full-suite failure: skills/tdd/scripts/tests/py/unit/test_pending_mark_literal.py — FAILED test_no_script_or_module_but_lib_ledger_sh_and_veri_ledger_py_and_no_line_of_skill_md_spells_a_box: veri/run_finished.py:40 spells a box (only lib/ledger.sh and veri/ledger.py may spell a checkbox literal) ⟦suite-repair⟧ ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 59 | 27 | 52 | 6152 | 640427 | 171906 | 0.56 | 811 | unknown | 1/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `run-finished.sh <issue>` for an issue with no run under `.tdd/wt/` exits 2 and says on stderr that there is no run for that issue; the new script (a `/bin/sh` shim over a `veri/` module, as `status.sh` is) has a no-argument usage line with exit 2 and a declared caller, so the repo-wide audits stay green ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 34 | 0.09 |
| When the run's state as `status.sh` reports it is not `done`, `run-finished.sh <issue>` exits 1 and prints the line `not-done <state>` Build any scratch git repository in the suite with the harness's `new_repo`, never a bare `git init` (`tests/unit/no-report-copies.test.sh` refuses it). ⟦criterion 2⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 57 | 0.11 |
| When the run's ledger has an unchecked step, `run-finished.sh <issue>` exits 1 and prints one `unchecked <step>` line per unchecked step Build any scratch git repository in the suite with the harness's `new_repo`, never a bare `git init` (`tests/unit/no-report-copies.test.sh` refuses it). ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 34 | 0.09 |
| When a ledger step still carries `⟂ refactor pending`, `run-finished.sh <issue>` exits 1 and prints one `refactor-pending <step>` line per such step Build any scratch git repository in the suite with the harness's `new_repo`, never a bare `git init` (`tests/unit/no-report-copies.test.sh` refuses it). ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 34 | 0.09 |
| When the run's PR body holds an unticked `⟦human-owed⟧` line, `run-finished.sh <issue>` exits 1 and prints one `human-owed <line>` line per unticked line; several unmet conditions together each print their own line Build any scratch git repository in the suite with the harness's `new_repo`, never a bare `git init` (`tests/unit/no-report-copies.test.sh` refuses it). ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 34 | 0.09 |
| When the run's PR body cannot be read (no PR found, or the GitHub read fails), `run-finished.sh <issue>` exits 2 and says on stderr that the PR body could not be read Build any scratch git repository in the suite with the harness's `new_repo`, never a bare `git init` (`tests/unit/no-report-copies.test.sh` refuses it). ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 36 | 0.09 |
| fix the full-suite failure: skills/tdd/scripts/tests/py/unit/test_pending_mark_literal.py — FAILED test_no_script_or_module_but_lib_ledger_sh_and_veri_ledger_py_and_no_line_of_skill_md_spells_a_box: veri/run_finished.py:40 spells a box (only lib/ledger.sh and veri/ledger.py may spell a checkbox literal) ⟦suite-repair⟧ ⟦criterion 4⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 49 | 0.15 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 106 | 18 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 1 | 2 | 2 | 2 | 1 | 2 | 3 | 4 |
| fast | 19 | 17 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 17 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 17 | 16 | 0 | 21 | 625 | 17 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 2 | 0 | 0 | 2 | 2 | 0 | 3 | 3 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 280 | 556 | 80547 | 7934941 | 1064809 | 4.83 |
