### 📊 Metrics — issue 2488

Wall time for the issue: 951 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 2 of 7 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.17 over 66 turns, in 1 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88648 tokens, largest 184884 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 88648 |
| 2 | $0.02 | 89013 |
| 3 | $0.05 | 92773 |
| 4 | $0.03 | 94416 |
| 5 | $0.02 | 95032 |
| 6 | $0.02 | 95731 |
| 7 | $0.02 | 96378 |
| 8 | $0.02 | 96838 |
| 9 | $0.02 | 97399 |
| 10 | $0.03 | 98371 |
| 11 | $0.03 | 99370 |
| 12 | $0.14 | 114870 |
| 13 | $0.03 | 116327 |
| 14 | $0.03 | 117175 |
| 15 | $0.04 | 118833 |
| 16 | $0.06 | 123353 |
| 17 | $0.03 | 123877 |
| 18 | $0.03 | 124715 |
| 19 | $0.04 | 126322 |
| 20 | $0.06 | 130331 |
| 21 | $0.03 | 130818 |
| 22 | $0.03 | 131710 |
| 23 | $0.03 | 132100 |
| 24 | $0.03 | 132400 |
| 25 | $0.03 | 133173 |
| 26 | $0.03 | 133781 |
| 27 | $0.04 | 135131 |
| 28 | $0.03 | 135849 |
| 29 | $0.04 | 137760 |
| 30 | $0.03 | 138090 |
| 31 | $0.03 | 138621 |
| 32 | $0.03 | 139443 |
| 33 | $0.03 | 139719 |
| 34 | $0.03 | 140410 |
| 35 | $0.04 | 141344 |
| 36 | $0.03 | 141965 |
| 37 | $0.04 | 143226 |
| 38 | $0.04 | 144468 |
| 39 | $0.03 | 144840 |
| 40 | $0.09 | 152561 |
| 41 | $0.04 | 154053 |
| 42 | $0.04 | 155329 |
| 43 | $0.04 | 155913 |
| 44 | $0.04 | 156740 |
| 45 | $0.04 | 157458 |
| 46 | $0.04 | 158208 |
| 47 | $0.04 | 159378 |
| 48 | $0.04 | 160194 |
| 49 | $0.04 | 160937 |
| 50 | $0.04 | 161967 |
| 51 | $0.04 | 162655 |
| 52 | $0.03 | 162961 |
| 53 | $0.04 | 164007 |
| 54 | $0.04 | 164731 |
| 55 | $0.04 | 165298 |
| 56 | $0.05 | 167706 |
| 57 | $0.04 | 168349 |
| 58 | $0.04 | 168547 |
| 59 | $0.04 | 169001 |
| 60 | $0.04 | 170164 |
| 61 | $0.05 | 171862 |
| 62 | $0.04 | 173055 |
| 63 | $0.04 | 173783 |
| 64 | $0.05 | 176018 |
| 65 | $0.07 | 180669 |
| 66 | $0.07 | 184884 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 24 | 22 | 2 | 4 | 2033 | 36668 | 39437 | 0.12 |
| red | 3 | 1 | 0 | 0 | 78 | 63 | 15 | 30 | 6623 | 522054 | 93212 | 0.35 |
| green | 5 | 1 | 1 | 0 | 306 | 114 | 26 | 52 | 10632 | 919675 | 114450 | 0.60 |
| red-missing | 1 | 0 | 0 | 0 | 60 | 44 | 8 | 16 | 4870 | 422736 | 44261 | 0.20 |
| pin | 2 | 2 | 0 | 0 | 48 | 34 | 8 | 16 | 3464 | 245664 | 40588 | 0.16 |
| refactor | 1 | 0 | 0 | 0 | 10 | 6 | 4 | 8 | 513 | 128092 | 21082 | 0.07 |
| prose | 1 | 0 | 0 | 0 | 31 | 29 | 1 | 2 | 3885 | 649 | 39850 | 0.14 |
| skill-edit | 3 | 0 | 0 | 0 | 57 | 48 | 14 | 28 | 3545 | 742404 | 88753 | 0.33 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 5 | 1 | 0 | 192 | 116 | 23 | 46 | 10632 | 710768 | 125678 | 0.49 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 334 | 167 | 40 | 80 | 17503 | 1564121 | 227352 | 1.01 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 306 | 0.60 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 31 | 0.14 |
| skill-edit | 0 | 0.00 | 57 | 0.33 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `wait-ci.sh` exits 4 — a code of its own, distinct from 0, 1, 2 and 3 — on its first poll when the PR's head reports no check runs and no commit statuses and none of the head's `.github/workflows/*` files carries a `pull_request` or `pull_request_target` trigger: no `.tdd/ci-deadline-<sha>` is recorded and no poll sleep is served; the conflict refusal (exit 2) and the draft refusal (exit 2) keep precedence, and a PR still reporting a head other than `<head-sha>` stays pending (3); the header's status line names exit 4; small in-process cases in `tests/py/unit/test_wait_ci.py` faking only `gh`, and older cases there that pin exit 3 for a rollup with no check are superseded by this step ⟦criterion 1⟧ | 10 | 3 | 1 | 0 | 0 | 0 | 222 | 49 | 98 | 21596 | 1798487 | 264928 | 1.17 | 667 | 1/2 | 0/5 | nothing-left |  |  | already-satisfied |
| A late CI is unaffected: `wait-ci.sh` still exits 3 when the rollup reports no check yet but a head workflow carries a `pull_request` trigger, exits 3 while a check is pending, and 0 or 1 when the checks land green or red; small in-process cases in `tests/py/unit/test_wait_ci.py` faking only `gh`, no production change ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 12 | 24 | 4506 | 439734 | 48665 | 0.21 | unknown | unknown | unknown | unknown |  |  | pin |
| `skills/tdd/SCRIPTS.md`'s `wait-ci.sh` entry (SC38) documents exit 4, a PR whose rollup reports no checks on the first poll with no head workflow triggered by pull requests, distinct from pending (3) and from past-the-deadline (2) ⟦skill-edit⟧ ⟦criterion 1⟧ | 4 | 0 | 0 | 0 | 0 | 0 | 77 | 15 | 30 | 7430 | 743053 | 128603 | 0.47 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `wait-ci.sh` exits 4 — a code of its own, distinct from 0, 1, 2 and 3 — on its first poll when the PR's head reports no check runs and no commit statuses and none of the head's `.github/workflows/*` files carries a `pull_request` or `pull_request_target` trigger: no `.tdd/ci-deadline-<sha>` is recorded and no poll sleep is served; the conflict refusal (exit 2) and the draft refusal (exit 2) keep precedence, and a PR still reporting a head other than `<head-sha>` stays pending (3); the header's status line names exit 4; small in-process cases in `tests/py/unit/test_wait_ci.py` faking only `gh`, and older cases there that pin exit 3 for a rollup with no check are superseded by this step ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 10 | 0.07 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 2 | 1 | 2 | 1 | 2 | 2 |  |  |  |
| fast | 18 | 18 | 18 | 18 | 17 |  |  |  |  |  |
| target | 1 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 78 | 156 | 35565 | 3017942 | 481633 | 1.97 |
