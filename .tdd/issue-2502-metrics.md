### 📊 Metrics — issue 2502

Wall time for the issue: 3657 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2639.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.41 over 58 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 84245 tokens, largest 143882 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.53 | 84245 |
| 2 | $0.07 | 90863 |
| 3 | $0.05 | 94843 |
| 4 | $0.03 | 96526 |
| 5 | $0.02 | 97108 |
| 6 | $0.02 | 97792 |
| 7 | $0.02 | 98181 |
| 8 | $0.02 | 98489 |
| 9 | $0.02 | 98765 |
| 10 | $0.03 | 99628 |
| 11 | $0.02 | 100093 |
| 12 | $0.06 | 105607 |
| 13 | $0.04 | 107693 |
| 14 | $0.03 | 109113 |
| 15 | $0.02 | 109502 |
| 16 | $0.03 | 110405 |
| 17 | $0.03 | 111085 |
| 18 | $0.04 | 113784 |
| 19 | $0.03 | 114451 |
| 20 | $0.03 | 115792 |
| 21 | $0.03 | 116810 |
| 22 | $0.03 | 118089 |
| 23 | $0.03 | 118865 |
| 24 | $0.03 | 119972 |
| 25 | $0.03 | 120823 |
| 26 | $0.03 | 121533 |
| 27 | $0.03 | 122345 |
| 28 | $0.03 | 123042 |
| 29 | $0.03 | 123426 |
| 30 | $0.03 | 124586 |
| 31 | $0.04 | 126267 |
| 32 | $0.03 | 126650 |
| 33 | $0.03 | 126881 |
| 34 | $0.03 | 127247 |
| 35 | $0.03 | 127961 |
| 36 | $0.03 | 128403 |
| 37 | $0.03 | 129061 |
| 38 | $0.03 | 129518 |
| 39 | $0.03 | 129891 |
| 40 | $0.04 | 131417 |
| 41 | $0.03 | 131895 |
| 42 | $0.04 | 133536 |
| 43 | $0.03 | 134165 |
| 44 | $0.04 | 135421 |
| 45 | $0.03 | 136157 |
| 46 | $0.04 | 137339 |
| 47 | $0.03 | 137917 |
| 48 | $0.04 | 139817 |
| 49 | $0.03 | 140603 |
| 50 | $0.03 | 140998 |
| 51 | $0.03 | 141210 |
| 52 | $0.03 | 141361 |
| 53 | $0.03 | 141571 |
| 54 | $0.03 | 142178 |
| 55 | $0.04 | 143101 |
| 56 | $0.03 | 143258 |
| 57 | $0.03 | 143533 |
| 58 | $0.03 | 143882 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 8 | 1 | 2 | 1040 | 0 | 34962 | 0.10 |
| red | 7 | 2 | 0 | 0 | 163 | 110 | 34 | 68 | 12815 | 1115967 | 171825 | 0.67 |
| green | 4 | 2 | 0 | 0 | 194 | 43 | 19 | 38 | 5019 | 585257 | 71943 | 0.29 |
| refactor | 2 | 0 | 0 | 0 | 12 | 6 | 4 | 8 | 426 | 102637 | 34016 | 0.10 |
| pin | 3 | 3 | 0 | 0 | 57 | 31 | 12 | 24 | 3446 | 346759 | 51995 | 0.20 |
| prose | 5 | 0 | 0 | 0 | 95 | 82 | 5 | 10 | 13347 | 32249 | 154377 | 0.52 |
| skill-edit | 1 | 0 | 0 | 0 | 8 | 6 | 3 | 6 | 738 | 138600 | 43174 | 0.13 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 8 | 0 | 0 | 197 | 79 | 27 | 54 | 8796 | 747374 | 156812 | 0.55 |
| developer | claude-sonnet-5-5 | 9 | 0 | 0 | 0 | 240 | 119 | 43 | 86 | 13950 | 1403246 | 207929 | 0.80 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| With `VERI_CI_ON_PR=0`, `wait-ci.sh <pr-url>` on a mergeable, non-draft PR whose head has no check runs and no commit statuses exits 0 on its first poll, writes no `.tdd/ci-deadline-*` file, and prints one stderr line saying the PR has no checks and `VERI_CI_ON_PR=0` says none will come; reproduced by a small case in `skills/tdd/scripts/tests/py/unit/test_wait_ci.py`, faking only the `gh` boundary ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 53 | 20 | 40 | 5896 | 601392 | 116585 | 0.41 | 293 | unknown | 0/5 | nothing-left |  |  | full |
| With `VERI_CI_ON_PR` unset or `1`, the same mergeable, non-draft PR whose head has no check runs and no commit statuses still ends its slice with exit 3, as on `main`; pinned by a small case in `skills/tdd/scripts/tests/py/unit/test_wait_ci.py`, faking only the `gh` boundary ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 30 | 12 | 24 | 3662 | 411256 | 42607 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| With `VERI_CI_ON_PR=0`, a head with a failed check run still exits 1 and prints the failed check's name on stdout; pinned by a small case in `skills/tdd/scripts/tests/py/unit/test_wait_ci.py`, faking only the `gh` boundary ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 29 | 10 | 20 | 3520 | 325394 | 41593 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| With `VERI_CI_ON_PR=0`, a head with a pending check run still ends its slice with exit 3; pinned by a small case in `skills/tdd/scripts/tests/py/unit/test_wait_ci.py`, faking only the `gh` boundary ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 30 | 9 | 18 | 3384 | 276015 | 37210 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| A `VERI_CI_ON_PR` other than `0`, `1` or empty is refused with exit 2, naming the value on stderr; reproduced by a small case in `skills/tdd/scripts/tests/py/unit/test_wait_ci.py`, faking only the `gh` boundary ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 48 | 18 | 36 | 5244 | 536563 | 91784 | 0.34 | 227 | unknown | 0/5 | nothing-left |  |  | full |
| skill-edit step for the unit `skills/tdd/SCRIPTS.md`: row SC38 in `skills/tdd/REQUIREMENTS.md` under `## skills/tdd/SCRIPTS.md` is rewritten in place exactly as the issue's `## Requirements` states it (one row rewritten, none added), and the `wait-ci.sh` entry names `VERI_CI_ON_PR`, its exit-0 case for a head with no check runs and no commit statuses, and its exit 2 on another value; the unit grades PASS against its whole list and is signed in `skills/tdd/GRADED` inside this step ⟦skill-edit⟧ ⟦criterion 3⟧ | 5 | 0 | 0 | 0 | 0 | 0 | 62 | 7 | 14 | 9783 | 170200 | 154545 | 0.50 | 103 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| With `VERI_CI_ON_PR=0`, `wait-ci.sh <pr-url>` on a mergeable, non-draft PR whose head has no check runs and no commit statuses exits 0 on its first poll, writes no `.tdd/ci-deadline-*` file, and prints one stderr line saying the PR has no checks and `VERI_CI_ON_PR=0` says none will come; reproduced by a small case in `skills/tdd/scripts/tests/py/unit/test_wait_ci.py`, faking only the `gh` boundary ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.05 |
| A `VERI_CI_ON_PR` other than `0`, `1` or empty is refused with exit 2, naming the value on stderr; reproduced by a small case in `skills/tdd/scripts/tests/py/unit/test_wait_ci.py`, faking only the `gh` boundary ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 3 | 3 | 2 | 0 | 3 | 2 | 2 | 2 | 3 | 3 |
| fast | 29 | 26 | 26 | 26 |  |  |  |  |  |  |  |
| target | 2 | 2 | 3 | 2 | 3 | 2 | 2 | 3 |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 78 | 156 | 36831 | 2321469 | 562292 | 4.42 (estimate) |
