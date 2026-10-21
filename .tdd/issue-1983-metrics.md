### 📊 Metrics — issue 1983

Wall time for the issue: 2540 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 159 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2044.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 18 | 16 | 1 | 2 | 1435 | 0 | 29710 | 0.09 |
| red | 4 | 1 | 0 | 0 | 184 | 127 | 26 | 50 | 11639 | 868310 | 111764 | 0.48 |
| green | 4 | 1 | 0 | 0 | 531 | 145 | 37 | 72 | 11946 | 1089135 | 152406 | 0.88 |
| refactor | 2 | 1 | 0 | 0 | 26 | 15 | 6 | 10 | 915 | 119741 | 25381 | 0.08 |
| diff | 6 | 3 | 0 | 0 | 565 | 160 | 37 | 74 | 12220 | 1148838 | 110143 | 0.51 |
| pin | 2 | 2 | 0 | 0 | 31 | 20 | 9 | 18 | 2695 | 244636 | 30396 | 0.13 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 9 | 9 | 0 | 0 | 363 | 116 | 33 | 62 | 10596 | 766704 | 162216 | 0.59 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 493 | 239 | 52 | 104 | 19924 | 1762669 | 176103 | 0.82 |
| developer | claude-opus-5-5 | 3 | 0 | 0 | 0 | 499 | 128 | 31 | 60 | 10330 | 941287 | 121481 | 0.77 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A session-scoped pytest fixture prepares one committed git scratch tree once, and a per-case copy of it (made in-process, no `git init`) is a git repository whose HEAD is the prepared commit, while a file written into one case's copy appears neither in another copy nor in the prepared tree; pinned by a process-marked case in a new `skills/tdd/scripts/tests/py/test_scratch_tree_process.py`, no production change ⟦criterion 2⟧ | 8 | 3 | 0 | 0 | 0 | 0 | 199 | 51 | 96 | 16156 | 1384227 | 226889 | 1.14 | 723 | 2/2 | 0/5 | nothing-left |  |  | full |
| grade-prose's "repo with history" case in `test_grade_prose_process.py` builds its repo from a copy of the prepared scratch tree instead of `git init`, and every grade-prose case keeps its name and its outcome (the same exit code and output for the same requirement/guide pair); no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 8 | 16 | 2492 | 213342 | 28875 | 0.12 | 189 | n/a | n/a | n/a |  |  | full |
| One process-marked case runs mutation-parity over a table holding a proven, an unproven and an owed row in one scratch tree and pins each row's verdict line and the exit code, and pins exit 2 for a row whose suite path does not exist and for a row whose pytest node id is not collected; no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 68 | 14 | 28 | 5035 | 484724 | 46225 | 0.21 | unknown | unknown | unknown | unknown |  |  | pin |
| `test_mutation_parity_process.py`'s committed scratch repositories are built from a copy of the prepared scratch tree instead of `git init`, and every mutation-parity case keeps its name and its verdict outcome; no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 81 | 15 | 30 | 4558 | 469236 | 34020 | 0.18 | 217 | n/a | n/a | n/a |  |  | full |
| After mutation-parity judges a row — a bash-suite row and a pytest-suite row alike — the mutated source file is byte-identical to its content before the run and no bytecode compiled from the mutated source survives anywhere in the case's tree; pinned per case by a process-marked case ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 13 | 26 | 6004 | 452871 | 46833 | 0.22 | unknown | unknown | unknown | unknown |  |  | pin |
| `test_skill_edit_step_process.py`'s cases build their git repositories from a copy of the prepared scratch tree instead of `git init`, and every skill-edit-step case keeps its name and its outcome; no production change ⟦diff-checked⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 45 | 14 | 28 | 5170 | 466260 | 47248 | 0.22 | 228 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A session-scoped pytest fixture prepares one committed git scratch tree once, and a per-case copy of it (made in-process, no `git init`) is a git repository whose HEAD is the prepared commit, while a file written into one case's copy appears neither in another copy nor in the prepared tree; pinned by a process-marked case in a new `skills/tdd/scripts/tests/py/test_scratch_tree_process.py`, no production change ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 26 | 0.08 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 1 | 1 | 343 | 3 | 6 | 1 | 54 | 55 | 20 | 21 | 77 | 23 | 49 | 49 |
| fast | 7 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 |  |  |  |  |  |
| target | 0 | 1 | 1 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 116 | 226 | 40850 | 3470660 | 459800 | 2.18 |
