### 📊 Metrics — issue 3237

Wall time for the issue: 3406 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 29 s, excluded from it.
Steps done: 9 of 11 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3272.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 17 | 15 | 3 | 6 | 1943 | 43080 | 23588 | 0.08 |
| red | 14 | 5 | 0 | 0 | 366 | 178 | 66 | 126 | 21408 | 1131045 | 256243 | 0.97 |
| green | 12 | 5 | 1 | 0 | 578 | 119 | 57 | 108 | 13573 | 924469 | 194953 | 0.72 |
| refactor | 5 | 0 | 0 | 0 | 29 | 18 | 12 | 22 | 1134 | 143586 | 75138 | 0.21 |
| red-missing | 1 | 0 | 0 | 0 | 19 | 12 | 3 | 6 | 1644 | 54314 | 24516 | 0.08 |
| pin | 5 | 3 | 2 | 0 | 91 | 60 | 17 | 34 | 6460 | 246078 | 72887 | 0.27 |
| prose | 10 | 0 | 0 | 0 | 414 | 393 | 10 | 20 | 62945 | 99655 | 485197 | 1.85 |
| skill-edit | 2 | 0 | 0 | 0 | 30 | 25 | 10 | 16 | 2288 | 448466 | 137878 | 0.41 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 17 | 14 | 3 | 0 | 623 | 165 | 61 | 116 | 18016 | 872381 | 267602 | 0.94 |
| developer | claude-sonnet-5-5 | 21 | 0 | 0 | 0 | 477 | 237 | 97 | 186 | 28146 | 1670191 | 379723 | 1.40 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 58 | 0.18 |
| green | 185 | 0.22 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 37 | 0.11 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `refactor-touched.sh --issue <base> --candidate '<c>' --check` prints nothing and exits 0 when the candidate names at least one tracked file the issue's commits (`<base>..HEAD`) changed, pinned by a case in `skills/tdd/scripts/tests/py/test_refactor_touched.py` ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 41 | 19 | 38 | 4552 | 317720 | 90201 | 0.30 | 232 | unknown | 0/5 | nothing-structural |  |  | full |
| `refactor-touched.sh --issue <base> --candidate '<c>' --check` exits 1 when the candidate names tracked files and none of them was changed by the issue's commits; its case names only an untouched tracked file, expects exit 1, and fails against a `--check` that always exits 0, in `skills/tdd/scripts/tests/py/test_refactor_touched.py` ⟦criterion 2⟧ | 9 | 3 | 1 | 0 | 0 | 0 | 83 | 32 | 60 | 9354 | 475559 | 150038 | 0.52 | 369 | unknown | 0/5 | nothing-structural |  |  | already-satisfied |
| `refactor-touched.sh --issue <base> --candidate '<c>' --check` prints nothing and exits 0 when the candidate names no tracked file at all, pinned by a case in `skills/tdd/scripts/tests/py/test_refactor_touched.py` ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 24 | 9 | 18 | 2835 | 153302 | 33518 | 0.13 | unknown | unknown | unknown | unknown |  |  | pin |
| `refactor-touched.sh --issue <base> --check` given without `--candidate` is a bad argument: it exits 2 and prints no file list on stdout, pinned by a case in `skills/tdd/scripts/tests/py/test_refactor_touched.py` ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 44 | 19 | 38 | 4495 | 305625 | 78989 | 0.27 | 203 | unknown | 0/5 | nothing-structural |  |  | full |
| `refactor-owed.sh not-done <file> '<candidate>' out-of-bounds` exits 0 and records the row, and `render` shows it under `### Not done` as `<candidate> — out-of-bounds`, pinned by a case in `skills/tdd/scripts/tests/py/test_refactor_owed.py` ⟦criterion 3⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 41 | 21 | 38 | 4740 | 310275 | 80119 | 0.28 | 205 | unknown | 0/5 | nothing-structural |  |  | full |
| `refactor-owed.sh not-done` with a reason outside the five known ones (`budget-spent`, `no-predicate`, `transform-rejected`, `uncovered`, `out-of-bounds`) still exits 2 and writes nothing, pinned by a case in `skills/tdd/scripts/tests/py/test_refactor_owed.py` ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 36 | 12 | 22 | 4403 | 202874 | 34038 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| `transform-touches-tests.sh <base-sha> <bound> --touched <list>` exits 0 when the commits in `<base-sha>..HEAD` change at least one file in the comma-separated `<list>`, change no test file, and stay inside `<bound>`, pinned by a case in `skills/tdd/scripts/tests/py/test_transform_touches_tests.py` ⟦criterion 4⟧ | 2 | 0 | 1 | 0 | 0 | 0 | 35 | 11 | 22 | 4331 | 213793 | 36009 | 0.15 | unknown | unknown | unknown | unknown |  |  | full |
| `transform-touches-tests.sh <base-sha> <bound> --touched <list>` exits 1 printing `transform changed no file the issue touched` when the commits in `<base-sha>..HEAD` change only a file outside `<list>` but inside `<bound>`; the case fails against a script that ignores `--touched`, in `skills/tdd/scripts/tests/py/test_transform_touches_tests.py` ⟦criterion 5⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 51 | 23 | 42 | 5819 | 362242 | 87826 | 0.31 | 235 | unknown | 0/5 | nothing-structural |  |  | full |
| `transform-touches-tests.sh <base-sha> <bound>` without `--touched` behaves as today: a range changing only a file inside `<bound>` (and no test file) exits 0 whether or not the issue touched that file, pinned by a case in `skills/tdd/scripts/tests/py/test_transform_touches_tests.py` ⟦criterion 4⟧ | 2 | 0 | 1 | 0 | 0 | 0 | 32 | 9 | 18 | 3690 | 158102 | 32999 | 0.14 | unknown | unknown | unknown | unknown |  |  | full |
| skill-edit step for the unit `skills/tdd/STRUCTURAL.md`: the per-candidate block runs `refactor-touched.sh --issue <issue-base> --candidate '<candidate>' --check` before the predicate leaf, and on its exit 1 launches no predicate, cover or transform leaf and records the candidate `not-done … out-of-bounds` followed by the not-done commit; the transform check passes `--touched "$($S/refactor-touched.sh --issue <issue-base>)"`, its exit 1 rejecting the transform like a bound violation, meeting requirements DP93, DP94 and DP40 ⟦skill-edit⟧ ⟦criterion 6⟧ | 5 | 0 | 0 | 0 | 0 | 0 | 51 | 10 | 16 | 6919 | 82414 | 54377 | 0.21 | unknown | unknown | unknown | unknown |  |  | full |
| skill-edit step for the unit `skills/tdd/SKILL.md`: the Refactor loop's out-of-scope paragraph has the in-step check run `$S/transform-touches-tests.sh <green-sha> <bound> --touched <touched-files>`, its exit 1 rejecting the transform before verify-refactor runs, meeting requirement RF61 ⟦skill-edit⟧ ⟦criterion 7⟧ | 5 | 0 | 0 | 0 | 0 | 0 | 243 | 8 | 16 | 37802 | 463542 | 434778 | 1.51 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `refactor-touched.sh --issue <base> --candidate '<c>' --check` prints nothing and exits 0 when the candidate names at least one tracked file the issue's commits (`<base>..HEAD`) changed, pinned by a case in `skills/tdd/scripts/tests/py/test_refactor_touched.py` ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | skipped | 0 | 6 | 0.04 |
| `refactor-touched.sh --issue <base> --candidate '<c>' --check` exits 1 when the candidate names tracked files and none of them was changed by the issue's commits; its case names only an untouched tracked file, expects exit 1, and fails against a `--check` that always exits 0, in `skills/tdd/scripts/tests/py/test_refactor_touched.py` ⟦criterion 2⟧ | 1 | 0/5 | nothing-structural | skipped | 0 | 6 | 0.04 |
| `refactor-touched.sh --issue <base> --check` given without `--candidate` is a bad argument: it exits 2 and prints no file list on stdout, pinned by a case in `skills/tdd/scripts/tests/py/test_refactor_touched.py` ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | skipped | 0 | 6 | 0.04 |
| `refactor-owed.sh not-done <file> '<candidate>' out-of-bounds` exits 0 and records the row, and `render` shows it under `### Not done` as `<candidate> — out-of-bounds`, pinned by a case in `skills/tdd/scripts/tests/py/test_refactor_owed.py` ⟦criterion 3⟧ | 1 | 0/5 | nothing-structural | skipped | 0 | 5 | 0.04 |
| `transform-touches-tests.sh <base-sha> <bound> --touched <list>` exits 1 printing `transform changed no file the issue touched` when the commits in `<base-sha>..HEAD` change only a file outside `<list>` but inside `<bound>`; the case fails against a script that ignores `--touched`, in `skills/tdd/scripts/tests/py/test_transform_touches_tests.py` ⟦criterion 5⟧ | 1 | 0/5 | nothing-structural | skipped | 0 | 6 | 0.04 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 3 | 2 | 7 | 3 | 3 | 2 |
| fast | 20 | 19 | 21 | 20 | 21 | 18 | 21 | 21 | 23 | 22 | 24 | 19 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 2 | 1 | 1 | 1 | 2 | 2 | 1 | 2 | 1 | 1 | 2 | 2 | 1 | 2 | 1 | 2 | 1 | 1 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 178 | 338 | 111395 | 3090693 | 1270400 | 4.60 |
