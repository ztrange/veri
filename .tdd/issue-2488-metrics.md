### 📊 Metrics — issue 2488

Wall time for the issue: 724 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 6 of 15 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $9.10 over 181 turns, in 3 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88648 tokens, largest 186423 tokens
Conductor context: first turn 88673 tokens, largest 156281 tokens
Conductor context: first turn 88656 tokens, largest 147027 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.59 | 88648 |
| 2 | $0.03 | 89013 |
| 3 | $0.06 | 92773 |
| 4 | $0.04 | 94416 |
| 5 | $0.03 | 95032 |
| 6 | $0.04 | 95731 |
| 7 | $0.03 | 96378 |
| 8 | $0.04 | 96838 |
| 9 | $0.03 | 97399 |
| 10 | $0.04 | 98371 |
| 11 | $0.04 | 99370 |
| 12 | $0.15 | 114870 |
| 13 | $0.05 | 116327 |
| 14 | $0.04 | 117175 |
| 15 | $0.04 | 118833 |
| 16 | $0.07 | 123353 |
| 17 | $0.04 | 123877 |
| 18 | $0.05 | 124715 |
| 19 | $0.04 | 126322 |
| 20 | $0.07 | 130331 |
| 21 | $0.04 | 130818 |
| 22 | $0.05 | 131710 |
| 23 | $0.04 | 132100 |
| 24 | $0.04 | 132400 |
| 25 | $0.04 | 133173 |
| 26 | $0.04 | 133781 |
| 27 | $0.05 | 135131 |
| 28 | $0.04 | 135849 |
| 29 | $0.06 | 137760 |
| 30 | $0.04 | 138090 |
| 31 | $0.04 | 138621 |
| 32 | $0.04 | 139443 |
| 33 | $0.04 | 139719 |
| 34 | $0.05 | 140410 |
| 35 | $0.04 | 141344 |
| 36 | $0.05 | 141965 |
| 37 | $0.05 | 143226 |
| 38 | $0.05 | 144468 |
| 39 | $0.04 | 144840 |
| 40 | $0.10 | 152561 |
| 41 | $0.05 | 154053 |
| 42 | $0.05 | 155329 |
| 43 | $0.05 | 155913 |
| 44 | $0.05 | 156740 |
| 45 | $0.05 | 157458 |
| 46 | $0.04 | 158208 |
| 47 | $0.05 | 159378 |
| 48 | $0.05 | 160194 |
| 49 | $0.05 | 160937 |
| 50 | $0.05 | 161967 |
| 51 | $0.05 | 162655 |
| 52 | $0.05 | 162961 |
| 53 | $0.05 | 164007 |
| 54 | $0.05 | 164731 |
| 55 | $0.05 | 165298 |
| 56 | $0.06 | 167706 |
| 57 | $0.05 | 168349 |
| 58 | $0.04 | 168547 |
| 59 | $0.05 | 169001 |
| 60 | $0.05 | 170164 |
| 61 | $0.06 | 171862 |
| 62 | $0.06 | 173055 |
| 63 | $0.05 | 173783 |
| 64 | $0.06 | 176018 |
| 65 | $0.08 | 180669 |
| 66 | $0.08 | 184884 |
| 67 | $0.06 | 185670 |
| 68 | $0.05 | 186423 |
| 69 | $0.58 | 88673 |
| 70 | $0.03 | 89604 |
| 71 | $0.06 | 93327 |
| 72 | $0.04 | 95171 |
| 73 | $0.05 | 98047 |
| 74 | $0.06 | 101878 |
| 75 | $0.03 | 102372 |
| 76 | $0.03 | 102762 |
| 77 | $0.04 | 103272 |
| 78 | $0.03 | 103556 |
| 79 | $0.03 | 103878 |
| 80 | $0.03 | 104132 |
| 81 | $0.04 | 104883 |
| 82 | $0.03 | 105524 |
| 83 | $0.04 | 107411 |
| 84 | $0.04 | 108579 |
| 85 | $0.04 | 109919 |
| 86 | $0.05 | 112138 |
| 87 | $0.04 | 112945 |
| 88 | $0.03 | 113229 |
| 89 | $0.04 | 114519 |
| 90 | $0.04 | 114995 |
| 91 | $0.04 | 115762 |
| 92 | $0.05 | 118223 |
| 93 | $0.04 | 119218 |
| 94 | $0.03 | 119467 |
| 95 | $0.04 | 119752 |
| 96 | $0.04 | 120643 |
| 97 | $0.04 | 121757 |
| 98 | $0.04 | 122425 |
| 99 | $0.14 | 136948 |
| 100 | $0.06 | 139486 |
| 101 | $0.04 | 140119 |
| 102 | $0.04 | 140415 |
| 103 | $0.04 | 140978 |
| 104 | $0.05 | 142241 |
| 105 | $0.04 | 142924 |
| 106 | $0.04 | 143541 |
| 107 | $0.04 | 144184 |
| 108 | $0.05 | 145419 |
| 109 | $0.04 | 145804 |
| 110 | $0.05 | 146586 |
| 111 | $0.04 | 147001 |
| 112 | $0.04 | 147590 |
| 113 | $0.04 | 148288 |
| 114 | $0.05 | 149614 |
| 115 | $0.04 | 150059 |
| 116 | $0.04 | 150477 |
| 117 | $0.05 | 151639 |
| 118 | $0.05 | 152989 |
| 119 | $0.04 | 153361 |
| 120 | $0.05 | 153776 |
| 121 | $0.04 | 154320 |
| 122 | $0.04 | 154995 |
| 123 | $0.05 | 155919 |
| 124 | $0.04 | 156281 |
| 125 | $0.57 | 88656 |
| 126 | $0.06 | 93324 |
| 127 | $0.02 | 93869 |
| 128 | $0.05 | 97762 |
| 129 | $0.05 | 101442 |
| 130 | $0.02 | 101912 |
| 131 | $0.02 | 102331 |
| 132 | $0.02 | 102730 |
| 133 | $0.02 | 103020 |
| 134 | $0.02 | 103289 |
| 135 | $0.02 | 103751 |
| 136 | $0.02 | 104046 |
| 137 | $0.03 | 104724 |
| 138 | $0.04 | 106483 |
| 139 | $0.04 | 108647 |
| 140 | $0.03 | 109694 |
| 141 | $0.03 | 110338 |
| 142 | $0.03 | 111771 |
| 143 | $0.03 | 112459 |
| 144 | $0.03 | 113010 |
| 145 | $0.03 | 113329 |
| 146 | $0.03 | 114064 |
| 147 | $0.03 | 114756 |
| 148 | $0.03 | 115158 |
| 149 | $0.03 | 115914 |
| 150 | $0.03 | 116488 |
| 151 | $0.03 | 117323 |
| 152 | $0.03 | 118440 |
| 153 | $0.03 | 118736 |
| 154 | $0.09 | 126672 |
| 155 | $0.03 | 127698 |
| 156 | $0.04 | 129032 |
| 157 | $0.03 | 129744 |
| 158 | $0.03 | 130855 |
| 159 | $0.03 | 131941 |
| 160 | $0.03 | 132612 |
| 161 | $0.03 | 133603 |
| 162 | $0.04 | 134824 |
| 163 | $0.03 | 135389 |
| 164 | $0.03 | 136253 |
| 165 | $0.03 | 137113 |
| 166 | $0.03 | 138058 |
| 167 | $0.04 | 139132 |
| 168 | $0.03 | 139590 |
| 169 | $0.04 | 140588 |
| 170 | $0.03 | 141395 |
| 171 | $0.04 | 142242 |
| 172 | $0.03 | 142984 |
| 173 | $0.06 | 147027 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 24 | 22 | 2 | 4 | 2033 | 36668 | 39437 | 0.12 |
| red | 7 | 2 | 0 | 0 | 171 | 137 | 33 | 66 | 14558 | 1105657 | 229665 | 0.83 |
| green | 12 | 1 | 4 | 0 | 659 | 285 | 60 | 120 | 27971 | 2077024 | 257424 | 1.53 |
| red-missing | 2 | 0 | 0 | 0 | 89 | 65 | 14 | 26 | 7905 | 600834 | 69907 | 0.31 |
| pin | 5 | 5 | 0 | 0 | 113 | 77 | 23 | 46 | 8242 | 710532 | 122538 | 0.46 |
| refactor | 1 | 0 | 0 | 0 | 10 | 6 | 4 | 8 | 513 | 128092 | 21082 | 0.07 |
| prose | 11 | 0 | 0 | 0 | 510 | 483 | 11 | 22 | 74054 | 63920 | 529945 | 2.07 |
| skill-edit | 5 | 0 | 0 | 0 | 559 | 99 | 27 | 54 | 8138 | 1695649 | 395089 | 1.24 |
| reconcile | 1 | 0 | 0 | 0 | 13 | 6 | 3 | 6 | 509 | 69451 | 35929 | 0.10 |
| exhausted | 1 | 0 | 0 | 0 | 36 | 13 | 3 | 6 | 1080 | 86235 | 17115 | 0.12 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 13 | 9 | 4 | 0 | 432 | 224 | 57 | 114 | 22629 | 1810236 | 277816 | 1.10 |
| developer | claude-sonnet-5-5 | 15 | 0 | 0 | 0 | 578 | 331 | 76 | 150 | 34815 | 2698105 | 471326 | 2.06 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 105 | 56 | 9 | 18 | 5367 | 306152 | 43955 | 0.39 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 33 | 0.25 |
| green | 306 | 0.60 | 353 | 0.93 |
| red-missing | 0 | 0.00 | 29 | 0.11 |
| pin | 0 | 0.00 | 25 | 0.09 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| reconcile | 0 | 0.00 | 13 | 0.10 |
| exhausted | 0 | 0.00 | 36 | 0.12 |
| verify-green | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `wait-ci.sh` exits 4 — a code of its own, distinct from 0, 1, 2 and 3 — on its first poll when the PR's head reports no check runs and no commit statuses and none of the head's `.github/workflows/*` files carries a `pull_request` or `pull_request_target` trigger: no `.tdd/ci-deadline-<sha>` is recorded and no poll sleep is served; the conflict refusal (exit 2) and the draft refusal (exit 2) keep precedence, and a PR still reporting a head other than `<head-sha>` stays pending (3); the header's status line names exit 4; small in-process cases in `tests/py/unit/test_wait_ci.py` faking only `gh`, and older cases there that pin exit 3 for a rollup with no check are superseded by this step ⟦criterion 1⟧ | 10 | 3 | 1 | 0 | 0 | 0 | 222 | 49 | 98 | 21596 | 1798487 | 264928 | 1.17 | 667 | 1/2 | 0/5 | nothing-left |  |  | already-satisfied |
| A late CI is unaffected: `wait-ci.sh` still exits 3 when the rollup reports no check yet but a head workflow carries a `pull_request` trigger, exits 3 while a check is pending, and 0 or 1 when the checks land green or red; small in-process cases in `tests/py/unit/test_wait_ci.py` faking only `gh`, no production change ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 12 | 24 | 4506 | 439734 | 48665 | 0.21 | unknown | unknown | unknown | unknown |  |  | pin |
| `skills/tdd/SCRIPTS.md`'s `wait-ci.sh` entry (SC38) documents exit 4, a PR whose rollup reports no checks on the first poll with no head workflow triggered by pull requests, distinct from pending (3) and from past-the-deadline (2) ⟦skill-edit⟧ ⟦criterion 1⟧ | 9 | 0 | 0 | 0 | 0 | 0 | 166 | 25 | 50 | 20347 | 1066799 | 293355 | 1.04 | -816894 | unknown | unknown | unknown |  |  | full |
| `skills/tdd/SKILL.md`'s Draft PR step routes a `wait-ci.sh` exit 4 at both CI waits (the first wait and the wait after the `metrics:` push) as no CI gate for this pull request: no bail mark, no `ci-timeout` cause, no `⟦ci-repair⟧` step appended; the run goes on to the `done` mark, the `metrics:` commit and a `### ✅ Done` comment that says the repository reports no checks on this pull request; pins outside the unit in `skills/tdd/scripts/tests/py/test_skill_ci_conflict.py` updated in the same commit ⟦skill-edit⟧ ⟦criterion 2⟧ | 3 | 0 | 0 | 0 | 0 | 0 | 245 | 9 | 18 | 34784 | 662139 | 459575 | 1.56 | 734 | unknown | unknown | unknown |  |  | full |
| Running the Draft PR step's CI command blocks from `skills/tdd/SKILL.md` under `bash -c` with a `wait-ci.sh` stub that exits 4 writes no `bail` event and no `ci-timeout` cause, appends no step to the ledger, and writes the `done` mark; a medium case with a real process (`@pytest.mark.process`), against stub scripts as `test_skill_ci_conflict.py` does, no production change ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 49 | 11 | 22 | 5008 | 370759 | 73608 | 0.27 | unknown | unknown | unknown | unknown |  |  | pin |
| `queued-merge.sh` still refuses to merge when `wait-ci.sh` exits 4: no `gh pr merge` is called and it exits non-zero, so an empty rollup is still not a pass at merge time; a small in-process case in `tests/py/unit/test_queued_merge.py`, no production change ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 26 | 10 | 20 | 3026 | 328821 | 42801 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_supervise_process.py::test_2380_a_leaf_queued_on_the_full_suite_lock_past_the_hard_timeout_is_not_killed_stuck — AssertionError: harvest-usage.sh: no closing result record in .tdd/verify-rebase.log — no usage event appended for verify-rebase ⟦suite-repair⟧ ⟦criterion 4⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 6 | 3 | 6 | 509 | 69451 | 35929 | 0.10 | unknown | unknown | unknown | unknown |  |  | full |
| `wait_ci.py`'s `runs_on_pull_requests` reads each head workflow's `on:` trigger block instead of matching raw text: `pull_request` or `pull_request_target` counts as running on pull requests when bare, with no `types:`, or with `types:` naming any of opened, synchronize, reopened or ready_for_review, and does not count when its `types:` name none of those; the list form (`on: [push, pull_request]`) and the mapping form are both read; a mention only in a comment or an `if:` does not count; stdlib only, no YAML library and no new requirements-dev.txt entry; cases each red first: ps-mutuus/gs-marketplace's exact trigger `on: pull_request: types: [closed]` reaches exit 4, `types: [opened, synchronize]` stays on exit 3, a workflow whose only mention of pull_request is a comment or an `if:` reaches exit 4; small in-process cases in `tests/py/unit/test_wait_ci.py` faking only `gh` ⟦added⟧ ⟦criterion 1⟧ | 12 | 2 | 3 | 0 | 0 | 0 | 247 | 55 | 108 | 26133 | 1770573 | 287729 | 1.50 | unknown | 2/2 | unknown | unknown |  |  | already-satisfied |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `wait-ci.sh` exits 4 — a code of its own, distinct from 0, 1, 2 and 3 — on its first poll when the PR's head reports no check runs and no commit statuses and none of the head's `.github/workflows/*` files carries a `pull_request` or `pull_request_target` trigger: no `.tdd/ci-deadline-<sha>` is recorded and no poll sleep is served; the conflict refusal (exit 2) and the draft refusal (exit 2) keep precedence, and a PR still reporting a head other than `<head-sha>` stays pending (3); the header's status line names exit 4; small in-process cases in `tests/py/unit/test_wait_ci.py` faking only `gh`, and older cases there that pin exit 3 for a rollup with no check are superseded by this step ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 10 | 0.07 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 2 | 1 | 2 | 1 | 2 | 2 | 2 | 1 | 2 | 1 | 1 | 2 | 2 | 2 | 2 | 2 |  |  |  |
| fast | 18 | 18 | 18 | 18 | 17 | 17 | 16 | 19 | 19 | 20 | 20 |  |  |  |  |  |  |  |  |  |
| target | 1 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 1 | 1 | 1 | 1 | 2 | 2 | 1 | 2 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 180 | 358 | 145003 | 6574062 | 1718131 | 6.86 |
